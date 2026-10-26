"""Owned smooth-view control. Ground truth is never supplied to the estimator."""
import hashlib
import json
import os
from pathlib import Path
import sys
from bounded_process import run

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/private/trackon-motion-0362"
SOURCE = ROOT / "assets/private/dense-photo-0332"


def prepare():
    import cv2
    import numpy as np
    from dense_photo_0332 import intersect
    from check_dense_grid_contract import bilinear
    cv2.setNumThreads(4)
    meta = json.loads((SOURCE / "inputs.json").read_text())
    for name, digest in {**meta["images"], "truth.npz": meta["truth_sha256"]}.items():
        assert hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() == digest
    truth = np.load(SOURCE/"truth.npz")
    rectangles, k = truth["rectangles"], truth["K"]
    rng = np.random.default_rng(331)
    recreated = np.array([[x,y,rng.uniform(2.6,3.5)] for y in np.linspace(-1,1,5) for x in np.linspace(-.63,.63,4)])
    assert np.array_equal(recreated, rectangles)
    textures = []
    for _ in rectangles:
        texture = cv2.GaussianBlur(rng.normal(size=(64,64)),(0,0),.8)
        textures.append(.25+.4*(texture-texture.min())/(texture.max()-texture.min()))
    yy, xx = np.mgrid[:1280,:720]
    pixels = np.column_stack((xx.ravel(),yy.ravel()))

    def render(pose, gain, bias, generator):
        xyz, labels = intersect(pose,pixels,rectangles,k)
        image = np.full(len(pixels),.08)
        for index,(x,y,_) in enumerate(rectangles):
            selected = labels == index
            uv = np.clip((xyz[selected,:2]-[x-.16,y-.19])/[.32,.38]*63,0,63)
            image[selected] = bilinear(textures[index],uv,[64,64])
        image = gain*image+bias+generator.normal(0,1/255,len(image))
        assert np.isfinite(image).all() and image.min()>=0 and image.max()<=1
        return np.round(image.reshape(1280,720)*255).astype("uint8")

    anchors = []
    for i,(gain,bias) in enumerate(zip([1.,1.07,.94],[0.,.01,-.01])):
        generated = render(truth["poses"][i],gain,bias,rng)
        anchor = cv2.imread(str(SOURCE/f"view-{i}.png"),cv2.IMREAD_GRAYSCALE)
        assert np.array_equal(generated,anchor), "anchor reproduction differs"
        anchors.append(anchor)
    poses = []
    images = []
    noise = np.random.default_rng(362)
    for i,yaw in enumerate([0,3,6,9,12,15,18,12,6,0,-6,-12,-18]):
        pitch = min(i*2.5,15)
        rotation = cv2.Rodrigues(np.array([0,np.deg2rad(yaw),0]))[0] @ cv2.Rodrigues(np.array([np.deg2rad(pitch),0,0]))[0]
        pose = np.eye(4); pose[:3,:3] = rotation; pose[:3,3] = [0,0,3]-rotation@np.array([0,0,3])
        poses.append(pose)
        if i in (0,6,12):
            images.append(anchors[i//6])
        else:
            gain = float(np.interp(i,[0,6,12],[1.,1.07,.94]))
            bias = float(np.interp(i,[0,6,12],[0.,.01,-.01]))
            images.append(render(pose,gain,bias,noise))
    query = np.load(SOURCE/"raw-endpoints.npz")["query"]
    xyz, labels = intersect(poses[0],query,rectangles,k)
    mask = labels >= 0
    expected = []
    for pose in poses:
        local = xyz@pose[:3,:3].T+pose[:3,3]
        uv = local[:,:2]/local[:,2,None]*k[0,0]+k[:2,2]
        hit, target = intersect(pose,uv,rectangles,k)
        mask &= (target==labels)&np.isfinite(hit).all(1)&(np.linalg.norm(hit-xyz,axis=1)<1e-6)
        mask &= (uv >= 4).all(1)&(uv <= [715,1275]).all(1)
        expected.append(uv)
    np.savez(OUT/"inputs.npz",images=np.stack(images),query=query.astype(np.float32))
    np.savez(OUT/"truth.npz",expected=np.stack(expected),visible=mask,poses=np.stack(poses))
    report = dict(anchor_arrays_exact=True,queries=len(query),visible_all_frames=int(mask.sum()),
                  inputs_sha256=hashlib.sha256((OUT/"inputs.npz").read_bytes()).hexdigest())
    (OUT/"prepared.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
    assert mask.sum()>=48


def worker():
    import check_trackon_load_0359 as loader
    sys.path.insert(0,str(ROOT/"assets/private/trackon-forward-0361/runtime"))
    import numpy as np
    import torch
    from torch.nn import functional as F
    model = loader.main(report_dir=OUT)
    model.memory_extension(72); model.eval()
    data = np.load(OUT/"inputs.npz")
    points = torch.from_numpy(data["query"])
    count = len(points)
    predictions, visibility = [], []
    with torch.inference_mode():
        memory = torch.zeros(count,72,256); mask = torch.ones(count,72,dtype=torch.bool)
        for i, gray in enumerate(data["images"]):
            frame = torch.from_numpy(gray.copy()).float()[None,None].expand(1,3,-1,-1)
            height, width = frame.shape[-2:]
            features = model.extract_frame_features(frame)
            if i == 0:
                field = features[-1].reshape(1,model.Hf,model.Wf,model.D).permute(0,3,1,2)
                grid = (points/torch.tensor([width,height])*2-1).reshape(1,count,1,2)
                query = F.grid_sample(field,grid,mode="bilinear",padding_mode="border",align_corners=False)[0,:,:,0].transpose(0,1)
            p, logits, newest = model.track_frame(query,mask,memory,features,height,width)
            assert p.shape==(count,2) and torch.isfinite(p).all() and torch.isfinite(logits).all()
            predictions.append(p.numpy().copy()); visibility.append(logits.sigmoid().numpy().copy())
            memory = torch.roll(memory,-1,dims=1); memory[:,-1] = newest
            mask = torch.roll(mask,-1,dims=1); mask[:,-1] = False
            print("Completed frame",i,flush=True)
    np.savez(OUT/"predictions.npz",predictions=np.stack(predictions),visibility=np.stack(visibility))


def evaluate():
    import numpy as np
    truth = np.load(OUT/"truth.npz"); prediction = np.load(OUT/"predictions.npz")
    error = np.linalg.norm(prediction["predictions"]-truth["expected"],axis=-1)
    visible = truth["visible"]
    p95 = np.quantile(error[:,visible],.95,axis=1)
    np.savez(OUT/"errors.npz",all_errors=error,visible=visible)
    result = dict(status="TECHNICAL_CHECK_PASSED" if np.all(p95<=3) else "REJECT",
                  native_p95_px=p95.tolist(),fixed_visible_points=int(visible.sum()),
                  all_query_points=error.shape[1],model_confidence_filter=False,
                  scope="owned scene smooth-view endpoints, not patient/medical accuracy")
    (OUT/"result.json").write_text(json.dumps(result,indent=2));print(json.dumps(result))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    stage=sys.argv[1]
    if stage.endswith("-worker"):
        {"prepare":prepare,"infer":worker,"evaluate":evaluate}[stage[:-7]]();return
    receipt=OUT/(stage+"-worker.json")
    if receipt.exists():raise RuntimeError("stage already attempted; inspect receipt")
    if stage=="infer":
        assert json.loads((OUT/"prepare-worker.json").read_text())["status"]=="TECHNICAL_CHECK_PASSED"
    python=ROOT/(".venv-trackon0357/Scripts/python.exe" if stage=="infer" else ".venv/Scripts/python.exe")
    limits={"prepare":(300,2),"infer":(600,4),"evaluate":(30,1)}
    seconds,gib=limits[stage];env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",OMP_NUM_THREADS="4")
    result=run([str(python),__file__,stage+"-worker"],ROOT,env,OUT/(stage+".log"),receipt,seconds,gib*1024**3)
    print(json.dumps(result))


if __name__=="__main__":main()
