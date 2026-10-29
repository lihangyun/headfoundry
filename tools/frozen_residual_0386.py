"""Archived arithmetic only; no data fit, image edit or acceptance change."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'assets/private/closed-experiments'


def read_archive(folder, expected):
    path = BASE/folder/'evidence.zip'
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == expected
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        return {name: archive.read(name) for name in archive.namelist()}


def npz(raw):
    return dict(np.load(io.BytesIO(raw), allow_pickle=False))


def fundamental(k, first, second):
    rotation = second[:3,:3]@first[:3,:3].T
    t = second[:3,3]-rotation@first[:3,3]
    cross = np.array([[0,-t[2],t[1]],[t[2],0,-t[0]],[-t[1],t[0],0]])
    inv = np.linalg.inv(k)
    return inv.T@cross@rotation@inv


def errors(f, first, second):
    a = np.c_[first,np.ones(len(first))]; b = np.c_[second,np.ones(len(second))]
    lb = a@f.T; la = b@f
    value = np.sum(b*lb,axis=1)
    da = np.linalg.norm(la[:,:2],axis=1); db = np.linalg.norm(lb[:,:2],axis=1)
    assert np.isfinite(value).all() and (da>0).all() and (db>0).all()
    return np.c_[abs(value)/da, abs(value)/db, abs(value)/np.sqrt(da**2+db**2)]


def main():
    old = read_archive('0383-roma-video','75559d3b50277fddc66b6a50f179d1bb4633e885976fb905dee864c060b62266')
    saved = read_archive('0385-archive-geometry','7e5bc84d7e3cff0c5fab9078e8c61e6632b923bdc0d46d30c6a3b0f1822af1ec')
    raw = npz(old['raw-observations.npz']); obs = npz(saved['observations.npz']); state = npz(saved['initial.npz'])
    k, poses = state['K'], state['poses']; xy = obs['xy']; ids = obs['source_ids']
    # Small exact independently constructed pinhole fixture and perpendicular perturbation.
    kk = np.array([[1000,0,359.5],[0,1000,639.5],[0,0,1.]])
    aa = np.eye(4); bb = np.eye(4); bb[0,3]=1
    xyz = np.array([[0.,0.,5.],[1.,.4,7.],[-.2,-.7,4.]])
    def project(p):
        q = xyz@p[:3,:3].T+p[:3,3]; h = q@kk.T
        return h[:,:2]/h[:,2:]
    first, second = project(aa), project(bb); ff = fundamental(kk,aa,bb)
    exact = errors(ff,first,second); moved = second+np.array([0.,5.])
    bad = errors(ff,first,moved)
    assert exact.max()<1e-9 and np.allclose(bad[:,1],5.,atol=1e-9,rtol=0)
    pairs = {}; per_point = {}
    for a,b in ((0,1),(0,2),(1,2)):
        e = errors(fundamental(k,poses[a],poses[b]),xy[a],xy[b]); name=f'{a}-{b}'
        pairs[name] = {split:dict(line_a_p95_px=float(np.percentile(e[ix,0],95)),
                                  line_b_p95_px=float(np.percentile(e[ix,1],95)),
                                  sampson_p95_px=float(np.percentile(e[ix,2],95)))
                       for split,ix in [('train',obs['train']),('held',obs['held'])]}
        per_point[name] = e.tolist()
    points = []
    for i,source in enumerate(ids):
        points.append(dict(source_id=int(source), split='held' if i in obs['held'] else 'train',
            xy=xy[:,i].tolist(), pair_errors={pair:row[i] for pair,row in per_point.items()},
            matcher={str(c):dict(confidence=float(raw[f'confidence_{c}'][source]),
                                 back_confidence=float(raw[f'back_confidence_{c}'][source]),
                                 fb_px=float(raw[f'fb_{c}'][source])) for c in (1,2)}))
    result = dict(status='TECHNICAL_CHECK_PASSED', scope='arithmetic audit only;0385REJECT unchanged',
                  control_exact_max_px=float(exact.max()), control_wrong_line_b_px=bad[:,1].tolist(),
                  pair_summary=pairs, all_points=points,
                  admitted_source_bounds=[xy[0].min(0).tolist(),xy[0].max(0).tolist()],
                  held_source_ids=ids[obs['held']].tolist())
    destination = BASE/'0386-frozen-residual'
    destination.mkdir(exist_ok=False)
    blob = json.dumps(result,indent=2,allow_nan=False).encode()
    source = Path(__file__).read_bytes()
    path = destination/'evidence.zip'
    with zipfile.ZipFile(path,'x',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('result.json',blob)
        archive.writestr('source/frozen_residual_0386.py',source)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None and archive.read('result.json') == blob
        assert archive.read('source/frozen_residual_0386.py') == source
    print(json.dumps(dict(pair_summary=pairs,query38=next(p for p in points if p['source_id']==38),
                         bounds=result['admitted_source_bounds'],archive_bytes=path.stat().st_size,
                         archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest()),indent=2))


if __name__ == '__main__':
    main()
