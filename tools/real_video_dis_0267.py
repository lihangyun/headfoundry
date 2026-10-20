"""Native video-motion readiness only;no scan,camera solve or reconstructed head."""
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from headfoundry.manifest import sha256_file,validate_input_assets
OUT=ROOT/"assets/private/native-dense-video-0267"
PILOT=ROOT/"assets/private/real-capture-pilot-v1"


def cue(image):
    value=(image[:,:,2].astype(float)-image[:,:,0]>12).astype(np.uint8)
    mask=np.zeros(value.shape,np.uint8);mask[500:820,100:620]=value[500:820,100:620]
    count,labels,stats,_=cv2.connectedComponentsWithStats(mask)
    if count<=1:return mask
    mask=(labels==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA]))).astype(np.uint8)*255
    return cv2.erode(mask,np.ones((8,8),np.uint8))


def sample(field,points):
    points=np.asarray(points,np.float32)
    if points.ndim!=2 or points.shape[1]!=2:raise ValueError("Nx2 points required")
    if not len(points):return np.empty((0,2),np.float32)
    good=np.isfinite(points).all(1)&(points[:,0]>=0)&(points[:,1]>=0)&(points[:,0]<=field.shape[1]-1)&(points[:,1]<=field.shape[0]-1)
    safe=np.where(good[:,None],points,0).astype(np.float32)
    values=cv2.remap(field,safe[:,0,None],safe[:,1,None],cv2.INTER_LINEAR).reshape(-1,2)
    values[~good]=np.nan
    return values


def transport(first,second,points,mask):
    f=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(first,second,None)
    b=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(second,first,None)
    target=points+sample(f,points);back=target+sample(b,target)
    error=np.linalg.norm(back-points,axis=1)
    valid=np.isfinite(target).all(1)&np.isfinite(error)&(error<=.75)
    rounded=np.rint(np.nan_to_num(target)).astype(np.int64)
    inside=(rounded[:,0]>=0)&(rounded[:,0]<mask.shape[1])&(rounded[:,1]>=0)&(rounded[:,1]<mask.shape[0])
    valid&=inside
    ids=np.flatnonzero(inside);valid[ids]&=mask[rounded[ids,1],rounded[ids,0]]>0
    return target,valid,error


def controls():
    cv2.setNumThreads(4)
    rng=np.random.default_rng(267)
    image=cv2.GaussianBlur(rng.integers(0,256,(160,160),dtype=np.uint8),(3,3),0)
    shifted=cv2.warpAffine(image,np.array([[1,0,3],[0,1,-2]],np.float32),(160,160),borderMode=cv2.BORDER_REFLECT)
    x,y=np.meshgrid(np.arange(32,129,12),np.arange(32,129,12));points=np.c_[x.ravel(),y.ravel()].astype(np.float32)
    estimated,valid,_=transport(image,shifted,points,np.full(image.shape,255,np.uint8))
    errors=np.linalg.norm(estimated-points-[3,-2],axis=1)
    if not valid.all() or np.percentile(errors,95)>1:raise AssertionError("Known translation failed")
    field=np.full((10,10,2),[2,-3],np.float32)
    np.testing.assert_array_equal(sample(field,np.array([[3.25,4.5]],np.float32)),[[2,-3]])
    assert np.isnan(sample(field,np.array([[-1,0]],np.float32))).all()
    assert sample(field,np.empty((0,2))).shape==(0,2)
    try:sample(field,np.zeros((2,3)))
    except ValueError:pass
    else:raise AssertionError("Bad coordinate shape accepted")
    same,ok,_=transport(image,image,points,np.full(image.shape,255,np.uint8))
    assert ok.all() and np.max(np.linalg.norm(same-points,axis=1))<1e-5
    return dict(status="TECHNICAL_CHECK_PASSED",scope="synthetic_2d_controls_only",translation_p95_px=float(np.percentile(errors,95)),checks=6)


def run():
    started=time.perf_counter();cv2.setNumThreads(4)
    if (cv2.__version__,np.__version__)!=("5.0.0","2.5.2"):raise ValueError("Runtime drift")
    control=controls();(OUT/"controls.json").write_text(json.dumps(control,indent=2))
    manifest=json.loads((PILOT/"manifest.json").read_text(encoding="utf-8"))
    records=[x for x in manifest["inputs"] if x["id"]=="real-case-001-video"]
    if len(records)!=1 or manifest.get("training_allowed") is not False or manifest.get("upload_allowed") is not False:
        raise ValueError("Exact local-video-only scope required")
    if validate_input_assets({**manifest,"inputs":records},PILOT):raise ValueError("Video rights/hash failure")
    source=PILOT/records[0]["path"]
    audit=json.loads((ROOT/"assets/private/video-observability-0252/report.json").read_text())
    if records[0]["sha256"]!=audit["source_sha256"]:raise ValueError("Different source video")
    capture=cv2.VideoCapture(str(source));keys=set(range(0,1041,12))|{624,1040}
    snapshots={};steps=[];cycles=[];observed=[];xy=np.empty((0,2),np.float32);ids=np.empty(0,np.int64);next_id=0;previous=None;reference=None
    for ordinal in range(1041):
        if time.perf_counter()-started>360:raise TimeoutError("Registered360s video budget")
        ok,image=capture.read()
        if not ok:raise ValueError("Premature video EOF")
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        if image.shape!=(1280,720,3) or hashlib.sha256(rgb.tobytes()).hexdigest()!=audit["frame_records"][ordinal]["rgb_sha256"]:
            raise ValueError("Sequential pixel identity failure")
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY);mask=cue(image)
        if previous is not None:
            moved,valid,error=transport(previous,gray,xy,mask)
            steps.append(dict(frame=ordinal,active_before=len(ids),retained=int(valid.sum()),ended_ids=ids[~valid].tolist()))
            xy,ids=moved[valid],ids[valid]
        if ordinal in [624,1040] and reference is not None:
            ref_gray,ref_xy,ref_ids=reference
            direct,dvalid,_=transport(ref_gray,gray,ref_xy,mask)
            common,si,di=np.intersect1d(ids,ref_ids[dvalid],return_indices=True)
            direct_valid=direct[dvalid];delta=np.linalg.norm(xy[si]-direct_valid[di],axis=1)
            closed=common[delta<=.75];chosen=direct_valid[di][delta<=.75]
            span=np.ptp(chosen,axis=0) if len(chosen) else np.zeros(2)
            p95=float(np.percentile(delta,95)) if len(delta) else None
            row=dict(frame=ordinal,reference_ids=len(ref_ids),sequential_survivors=len(np.intersect1d(ids,ref_ids)),
                     direct_valid=int(dvalid.sum()),both_valid=len(common),both_valid_disagreement_p95_px=p95,
                     closure_ids=len(closed),even=int((closed%2==0).sum()),odd=int((closed%2==1).sum()),span_px=span.tolist())
            row["passed"]=bool(p95 is not None and p95<=3 and row["even"]>=30 and row["odd"]>=30 and (span>=50).all())
            cycles.append(row)
            np.savez_compressed(OUT/f"cycle-{ordinal}.npz",reference_ids=ref_ids,direct_xy=direct,direct_valid=dvalid,
                                common_ids=common,seq_xy=xy[si],direct_common_xy=direct_valid[di],disagreement_px=delta)
        if ordinal in keys:
            seed_mask=mask.copy()
            for p in xy:cv2.circle(seed_mask,tuple(np.rint(p).astype(int)),5,0,-1)
            fresh=cv2.goodFeaturesToTrack(gray,maxCorners=400,qualityLevel=.01,minDistance=5,blockSize=7,mask=seed_mask)
            if fresh is not None:
                fresh=fresh.reshape(-1,2);xy=np.r_[xy,fresh];ids=np.r_[ids,np.arange(next_id,next_id+len(fresh))];next_id+=len(fresh)
            snapshots[ordinal]=set(ids.tolist());observed.append((ordinal,ids.copy(),xy.copy()))
        if ordinal==612:reference=(gray.copy(),xy.copy(),ids.copy())
        if ordinal in [144,408]:
            display=image.copy()
            for ident,p in zip(ids,xy):cv2.circle(display,tuple(np.rint(p).astype(int)),2,(0,255,0),-1)
            cv2.putText(display,f'FRAME {ordinal}: SOURCE/TRACKS ONLY - NOT A HEAD RESULT',(10,35),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255),1)
            cv2.imwrite(str(OUT/f"source-tracks-{ordinal}.png"),display)
        previous=gray
        if ordinal%120==0:(OUT/"progress.json").write_text(json.dumps(dict(frame=ordinal,active=len(ids),total_ids=next_id,seconds=time.perf_counter()-started)))
    if capture.read()[0]:raise ValueError("Unexpected extra source frames")
    capture.release()
    if sha256_file(source)!=records[0]["sha256"]:raise ValueError("Source changed")
    frame_ids=sorted(snapshots);adjacent=[len(snapshots[a]&snapshots[b]) for a,b in zip(frame_ids,frame_ids[1:])]
    neighbors={k:set() for k in frame_ids}
    for i,a in enumerate(frame_ids):
        for b in frame_ids[i+1:]:
            if len(snapshots[a]&snapshots[b])>=50:neighbors[a].add(b);neighbors[b].add(a)
    unseen=set(frame_ids);components=[]
    while unseen:
        component={unseen.pop()};todo=list(component)
        while todo:
            added=neighbors[todo.pop()]&unseen;unseen-=added;component|=added;todo.extend(added)
        components.append(component)
    largest=max(components,key=len);profiles={k for k in frame_ids if 120<=k<=168 or 396<=k<=444}
    graph_pass=bool(np.mean(np.array(adjacent)>=50)>=.8 and len(largest)>=.8*len(frame_ids) and profiles<=largest)
    passed=graph_pass and len(cycles)==2 and all(x["passed"] for x in cycles)
    np.savez_compressed(OUT/"observations.npz",frame=np.concatenate([np.full(len(ids),f) for f,ids,xy in observed]),
                        ids=np.concatenate([ids for f,ids,xy in observed]),xy=np.concatenate([xy for f,ids,xy in observed]))
    report=dict(status="TECHNICAL_CHECK_PASSED" if passed else "REJECT",scope="native_video_consistency_readiness_not_physical_truth",
                frames_decoded=1041,keyframes=len(frame_ids),total_track_ids=next_id,adjacent_shared=adjacent,
                largest_component=sorted(largest),raw_graph_pass=graph_pass,cycles=cycles,seconds=time.perf_counter()-started,
                source_sha256=records[0]["sha256"],case002_and_scans_read=False,camera="UNVERIFIED",head="UNVERIFIED",training=False,upload=False)
    (OUT/"steps.json").write_text(json.dumps(steps));(OUT/"report.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))


if __name__=="__main__":
    OUT.mkdir(exist_ok=True)
    try:
        if sys.argv[1:]==["controls"]:print(json.dumps(controls()))
        elif sys.argv[1:]==["run"]:
            with (OUT/"run-once.json").open("x") as f:json.dump(dict(started=time.time()),f)
            run()
        else:raise SystemExit("controls|run required")
    except BaseException as error:
        (OUT/"failure.json").write_text(json.dumps(dict(status="REJECT",type=type(error).__name__,error=str(error))))
        raise
