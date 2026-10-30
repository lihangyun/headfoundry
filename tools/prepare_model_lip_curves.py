"""Provisional generic surface attachment and archived two-render transfer."""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
import numpy as np
from prepare_lip_curves import CURVES,ROOT
sys.path.insert(0,str(ROOT/'src'))
from headfoundry.curve_observations import point_to_polyline
from headfoundry.raster import lift_pixels
from headfoundry.flame_expression import FlameExpressionModel


def project(v,e,k):
    camera=v@e[:,:3].T+e[:,3]
    if (camera[:,2]<=0).any():raise ValueError('Negative depth')
    h=camera@k.T
    return h[:,:2]/h[:,2:]


def main():
    archive=ROOT/'assets/private/closed-experiments/0382-render-conditioned/evidence.zip'
    expected='375f5aada3c2a4526460b3300b2f72dc3c4d74ac525042bf8904e4b94d70ce72'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise ValueError('Archive identity mismatch')
    with zipfile.ZipFile(archive) as z:
        def load(n):return dict(np.load(io.BytesIO(z.read(n)),allow_pickle=False))
        prior,truth,candidate,observed=[load(n) for n in ['prior.npz','truth.npz','candidate.npz','observations.npz']]
    v,f=prior['vertices'],prior['faces'];arrays={};reports={}
    for name in ['outer_upper','outer_lower']:
        ids=np.array(CURVES[name]);source=observed['observed'][ids]
        face,bary=lift_pixels(v,f,truth['E'],truth['K'],source)
        if (face<0).any():raise ValueError(f'Missing generic surface support: {name}')
        points=np.einsum('ni,nij->nj',bary,v[f[face]])
        replay=np.max(abs(project(points,truth['E'],truth['K'])-source))
        if replay>1e-8:raise ValueError('Projection replay failed')
        uv=project(points,candidate['E'],candidate['K'])
        hit,weights=lift_pixels(v,f,candidate['E'],candidate['K'],uv)
        visible=np.zeros(len(ids),bool);valid=hit>=0
        gap=np.full(len(ids),np.inf)
        gap[valid]=np.linalg.norm(np.einsum('ni,nij->nj',weights[valid],v[f[hit[valid]]])-points[valid],axis=1)
        visible[valid]=gap[valid]<1e-8
        target=candidate['semantics'][ids]
        residual,_,segment,fraction,ambiguous=point_to_polyline(uv,target)
        point_error=np.linalg.norm(uv-target,axis=1);curve_error=np.linalg.norm(residual,axis=1)
        arrays.update({name+'_faces':face,name+'_barycentric':bary,name+'_ids':ids})
        reports[name]=dict(source_replay_max=float(replay),visible=visible.tolist(),
            first_hit_gap=gap.tolist(),point_errors=point_error.tolist(),curve_errors=curve_error.tolist(),
            point_p95=float(np.percentile(point_error,95)),curve_p95=float(np.percentile(curve_error,95)),
            segments=segment.tolist(),fractions=fraction.tolist(),ambiguous=ambiguous.tolist())
    out=ROOT/'assets/private/reconstruction-observations-v1/model-lips'
    out.mkdir(exist_ok=False)
    np.savez_compressed(out/'attachments.npz',**arrays)
    report=dict(status='UNVERIFIED',scope='generic two-render transfer; no real camera or anatomy certification',
        source_archive_sha256=expected,attachment_sha256=hashlib.sha256((out/'attachments.npz').read_bytes()).hexdigest(),curves=reports,
        limitations='Source semantic bias remains possible. Barycentric transport does not certify a true vermilion boundary. Do not transfer hidden supports into a fit.')
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({name:{k:v for k,v in r.items() if k in ['source_replay_max','visible','point_p95','curve_p95']} for name,r in reports.items()},indent=2))


def transport_native():
    folder=ROOT/'assets/private/reconstruction-observations-v1/model-lips'
    report=json.loads((folder/'report.json').read_text())
    binding=folder/'attachments.npz'
    if hashlib.sha256(binding.read_bytes()).hexdigest()!=report['attachment_sha256']:
        raise ValueError('Attachment hash mismatch')
    archive=ROOT/'assets/private/closed-experiments/0382-render-conditioned/evidence.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=report['source_archive_sha256']:
        raise ValueError('Source fixture mismatch')
    lock=ROOT/'assets/private/FLAME-2023-Open/expression-v1/expression-lock.json'
    model=FlameExpressionModel.from_lock(lock)
    with zipfile.ZipFile(archive) as z:
        prior=dict(np.load(io.BytesIO(z.read('prior.npz')),allow_pickle=False))
    v=model.identity.template
    center=(v.min(0)+v.max(0))/2;scale=np.linalg.norm(v-center,axis=1).max()
    np.testing.assert_array_equal(model.identity.faces,prior['faces'])
    np.testing.assert_allclose((v-center)/scale,prior['vertices'],atol=1e-12,rtol=0)
    result={}
    with np.load(binding,allow_pickle=False) as z:
        for name in ['outer_upper','outer_lower']:
            triangles=model.identity.faces[z[name+'_faces']];bary=z[name+'_barycentric']
            result[name+'_base']=np.einsum('ni,nij->nj',bary,v[triangles])
            result[name+'_identity']=np.einsum('ni,nijk->njk',bary,model.identity.shape_directions[triangles])
            result[name+'_expression']=np.einsum('ni,nijk->njk',bary,model.expression_directions[triangles])
            # Nonzero algebra control, not an anatomically accepted expression.
            beta=np.zeros(300);beta[0]=.1;expression=np.zeros(100);expression[0]=.1
            direct=np.einsum('ni,nij->nj',bary,model.vertices(beta,expression)[triangles])
            composed=result[name+'_base']+result[name+'_identity']@beta+result[name+'_expression']@expression
            np.testing.assert_allclose(direct,composed,atol=1e-14,rtol=0)
    target=folder/'native-curves.npz'
    if target.exists():raise FileExistsError('Preserve native curve basis')
    np.savez_compressed(target,**result)
    metadata=dict(status='TECHNICAL_CHECK_PASSED',scope='basis transport only; anatomy remains UNVERIFIED',
        expression_lock_sha256=hashlib.sha256(lock.read_bytes()).hexdigest(),
        attachment_sha256=report['attachment_sha256'],array_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        normalized_fixture_center=center.tolist(),normalized_fixture_scale=float(scale))
    (folder/'native-curves.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    print(json.dumps(metadata,indent=2))


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='native':transport_native()
    else:main()
