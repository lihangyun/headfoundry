"""Bounded projective VarPro hypothesis;not an accepted camera or head."""
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import zipfile
import numpy as np
from scipy.linalg import qr, rq, eig
from scipy.optimize import least_squares, minimize
from scipy.sparse import lil_matrix
from scipy.spatial.transform import Rotation
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from headfoundry.manifest import validate_input_assets
OUT = ROOT/'assets/private/rank-quadric-0284'
REPORT = {'status':'REJECT','head':'UNVERIFIED','surface_mm':None}


def checkpoint(label, stage, details):
    REPORT[label][stage] = details
    (OUT/'progress.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
    print(json.dumps({'label':label,'stage':stage,**details}), flush=True)


def pose_varpro(y, mask, label):
    v, n = mask.shape
    uv = (y-[360,640])/1500
    rng = np.random.default_rng(283)
    p = np.zeros((v,3,4))
    p[:,:2,:3] = rng.normal(0,.1,(v,2,3))
    p[:,2,:3] = rng.normal(0,.01,(v,3))
    p[:,2,3] = 1
    for i in range(v):
        p[i,:2,3] = uv[i,mask[i]].mean(0)
    p[0] = [[1,0,0,0],[0,1,0,0],[0,0,0,1]]
    visible = [np.flatnonzero(mask[:,j]) for j in range(n)]
    sw, sa = np.sqrt(.95), np.sqrt(.05)
    started = time.monotonic()

    def reduced(theta, with_points=False):
        if time.monotonic()-started > 180:
            raise TimeoutError('pOSE180s cap')
        cams = np.concatenate([p[:1],theta.reshape(v-1,3,4)])
        grad = np.zeros_like(cams)
        points = np.empty((n,3))
        cost = 0.
        for j, views in enumerate(visible):
            c, u = cams[views], uv[views,j]
            a = np.concatenate([sw*(c[:,:2,:3]-u[:,:,None]*c[:,2:3,:3]),
                                sa*c[:,:2,:3]],axis=1).reshape(-1,3)
            b = np.concatenate([sw*(c[:,:2,3]-u*c[:,2,3,None]),
                                sa*(c[:,:2,3]-u)],axis=1).ravel()
            x, _, rank, _ = np.linalg.lstsq(a,-b,rcond=None)
            if rank < 3:
                raise ValueError('rank-deficient conditional point')
            points[j] = x
            residual = (a@x+b).reshape(-1,4)
            cost += float(np.sum(residual**2))
            xh = np.r_[x,1.]
            g = np.zeros_like(c)
            g[:,:2] = 2*(sw*residual[:,:2]+sa*residual[:,2:])[:,:,None]*xh
            g[:,2] = -2*sw*np.sum(residual[:,:2]*u,axis=1)[:,None]*xh
            np.add.at(grad,views,g)
        if with_points:
            return points,cams
        return cost,grad[1:].ravel()

    initial = p[1:].ravel()
    if label == 'control':
        _, analytic = reduced(initial)
        indices = np.random.default_rng(283).choice(len(initial),20,replace=False)
        differences = []
        for k in indices:
            delta = np.zeros_like(initial)
            delta[k] = 1e-6
            numeric = (reduced(initial+delta)[0]-reduced(initial-delta)[0])/2e-6
            absolute = abs(numeric-analytic[k])
            relative = absolute/max(abs(numeric),abs(analytic[k]),1e-12)
            differences.append((absolute,relative))
            if absolute > 1e-6 and relative > 1e-4:
                raise ValueError('reduced analytic gradient check failed')
        checkpoint(label,'gradient_control',{'max_absolute':max(a for a,b in differences),
                                             'max_relative':max(b for a,b in differences)})
    sol = minimize(reduced,initial,jac=True,method='L-BFGS-B',
                   options={'maxiter':400,'maxfun':1000,'ftol':1e-12,'gtol':1e-8})
    x,p = reduced(sol.x,with_points=True)
    checkpoint(label,'pOSE',{'optimizer_success':bool(sol.success),'message':str(sol.message),
                             'iterations':sol.nit,'evaluations':sol.nfev,'objective':float(sol.fun),
                             'seconds':time.monotonic()-started})
    return x,p


def projective_refine(y,mask,x0,p0,label):
    v,n = mask.shape
    vi,pi = np.where(mask)
    _,r,piv = qr(np.c_[x0,np.ones(n)].T,mode='economic',pivoting=True)
    if np.min(np.abs(np.diag(r)[:4])) < 1e-12:
        raise ValueError('four-point gauge rank failure')
    fixed_points = piv[:4]
    point_free = np.delete(np.arange(n*3),fixed_points*3+2)
    camera_free = np.ones(p0.size,bool)
    camera_free[:12] = False
    for i in range(1,v):
        camera_free[i*12+np.argmax(np.abs(p0[i]))] = False
    camera_free = np.flatnonzero(camera_free)
    offset = len(point_free)
    theta = np.r_[x0.ravel()[point_free],p0.ravel()[camera_free]]
    normalized = (y[vi,pi]-[360,640])/1500
    started = time.monotonic()

    def unpack(z):
        x,p = x0.ravel().copy(),p0.ravel().copy()
        x[point_free] = z[:offset]
        p[camera_free] = z[offset:]
        return x.reshape(n,3),p.reshape(v,3,4)

    def residual(z):
        if time.monotonic()-started > 180:
            raise TimeoutError('projectiveBA180s cap')
        x,p = unpack(z)
        c = np.einsum('nij,nj->ni',p[vi],np.c_[x[pi],np.ones(len(pi))])
        return np.r_[(1500*(c[:,:2]/np.maximum(c[:,2:3],.001)-normalized)).ravel(),
                     100*np.minimum(c[:,2]-.001,0)]

    m = len(vi)
    jac = lil_matrix((m*3,len(theta)),dtype=np.int8)
    pointcols = np.full(n*3,-1)
    pointcols[point_free] = np.arange(offset)
    camcols = np.full(v*12,-1)
    camcols[camera_free] = np.arange(len(camera_free))+offset
    for row,(view,point) in enumerate(zip(vi,pi)):
        cols = np.r_[pointcols[point*3:point*3+3],camcols[view*12:view*12+12]]
        cols = cols[cols>=0]
        for rr in (row*2,row*2+1,m*2+row):
            jac[rr,cols] = 1
    sol = least_squares(residual,theta,jac_sparsity=jac.tocsr(),loss='soft_l1',
                        f_scale=2,max_nfev=60,x_scale='jac')
    x,p = unpack(sol.x)
    c = np.einsum('nij,nj->ni',p[vi],np.c_[x[pi],np.ones(len(pi))])
    errors = np.linalg.norm(1500*(c[:,:2]/c[:,2:3]-normalized),axis=1)
    checkpoint(label,'projective_BA',{'optimizer_success':bool(sol.success),'message':str(sol.message),
                   'nfev':sol.nfev,'seconds':time.monotonic()-started,
                   'training_p95_px':float(np.percentile(errors,95)),
                   'nonpositive_denominators':int((c[:,2]<=0).sum()),
                   'fixed_gauge_points':fixed_points.tolist()})
    np.savez_compressed(OUT/(label+'-projective.npz'),shape=x,cameras=p)
    if not np.isfinite(x).all() or not np.isfinite(p).all() or np.any(c[:,2]<=0):
        raise ValueError('invalid projective refinement')
    return x,p


def quadric_candidates(a,b):
    pairs = eig(a,-b,right=False,homogeneous_eigvals=True)
    candidates,records = [],[]
    for index,pair in enumerate(pairs.T):
        rec = {'root':index,'alpha':[float(pair[0].real),float(pair[0].imag)],
               'beta':[float(pair[1].real),float(pair[1].imag)]}
        records.append(rec)
        magnitude = float(np.max(np.abs(pair)))
        if magnitude == 0:
            raise ValueError('singular quadric pencil:zero/zero root')
        if not np.isfinite(magnitude):
            rec['reject'] = 'nonfinite eigenpair'
            continue
        pivot = pair[np.argmax(np.abs(pair))]
        normalized = pair*np.exp(-1j*np.angle(pivot))/magnitude
        if np.max(np.abs(normalized.imag)) > 1e-7:
            rec['reject'] = 'nonreal root'
            continue
        alpha,beta = normalized.real
        q = beta*a+alpha*b
        norm = np.linalg.norm(q)
        if not np.isfinite(norm) or norm <= np.finfo(float).tiny:
            rec['reject'] = 'zero/nonfinite quadric'
            continue
        q = (q+q.T)/(2*norm)
        if np.trace(q)<0:
            q = -q
        values = np.linalg.eigvalsh(q)
        tolerance = 1e-10*np.max(np.abs(values))
        rec['eigenvalues'] = values.tolist()
        rec['positive_modes'] = int((values>tolerance).sum())
        rec['null_modes'] = int((np.abs(values)<=tolerance).sum())
        if rec['positive_modes']!=3 or rec['null_modes']!=1:
            rec['reject'] = 'not rank-three positive semidefinite'
            continue
        rec['rank_three'] = True
        candidates.append((index,q))
    return candidates,records


def pencil_self_check():
    a,b = np.diag([1.,1.,1.,0.]),np.diag([0.,0.,0.,1.])
    first,records = quadric_candidates(a,b)
    second,_ = quadric_candidates(2*a,3*b)
    if len(first)!=1 or len(second)!=1 or not np.allclose(first[0][1],a/np.sqrt(3)):
        raise ValueError('rank-three/rank-one pencil control failed')
    if not np.allclose(first[0][1],second[0][1]):
        raise ValueError('quadric basis-scaling control failed')
    try:
        quadric_candidates(np.diag([1.,1.,0.,0.]),b)
    except ValueError:
        pass
    else:
        raise ValueError('singular pencil was not rejected')
    return {'status':'TECHNICAL_CHECK_PASSED','positive_rank_three':len(first),'roots':records}


def metric_upgrade(x,p,mask,label,pixels):
    def bilinear(a,b):
        return [a[i]*b[j]+(a[j]*b[i] if i!=j else 0) for i in range(4) for j in range(i,4)]
    constraints = []
    for c in p/np.linalg.norm(p,axis=(1,2))[:,None,None]:
        a,b,d = c
        constraints += [bilinear(a,b),bilinear(a,d),bilinear(b,d),
                        (np.asarray(bilinear(a,a))-bilinear(b,b)).tolist()]
    _,sv,vh = np.linalg.svd(np.asarray(constraints),full_matrices=False)
    matrices = []
    for vector in vh[-2:][::-1]:
        q = np.zeros((4,4))
        k = 0
        for i in range(4):
            for j in range(i,4):
                q[i,j] = q[j,i] = vector[k]
                k += 1
        matrices.append(q)
    quadrics,roots = quadric_candidates(*matrices)
    diagnostic = {'constraint_singular_values':sv.tolist(),'roots':roots,
                  'rank_three_candidates':len(quadrics),'metric_candidates':[]}
    checkpoint(label,'metric_upgrade',diagnostic)
    eligible = []
    for index,q in quadrics:
        values,u = np.linalg.eigh(q)
        spatial = u[:,1:]*np.sqrt(values[1:])
        for sign in (1,-1):
            rec = {'root':index,'last_column_sign':sign,'eligible':False}
            diagnostic['metric_candidates'].append(rec)
            try:
                h = np.c_[spatial,sign*u[:,0]]
                xh = np.linalg.solve(h,np.c_[x,np.ones(len(x))].T).T
                if np.any(np.abs(xh[:,3])<1e-12):
                    raise ValueError('point at infinity')
                xm = xh[:,:3]/xh[:,3:4]
                rotations,translations,intrinsics = [],[],[]
                for m in p@h:
                    if np.linalg.det(m[:,:3])<0:
                        m = -m
                    kk,rr = rq(m[:,:3])
                    d = np.diag(np.sign(np.diag(kk)))
                    kk,rr = kk@d,d@rr
                    if np.min(np.abs(np.diag(kk)))<1e-12 or np.linalg.det(rr)<0:
                        raise ValueError('degenerate RQ camera')
                    translations.append(np.linalg.solve(kk,m[:,3]))
                    intrinsics.append(kk/kk[2,2])
                    rotations.append(rr)
                rr,tt,kk = np.asarray(rotations),np.asarray(translations),np.asarray(intrinsics)
                depth = np.einsum('vij,nj->vni',rr,xm)+tt[:,None]
                positive = int((depth[...,2][mask]>0).sum())
                f = float(1500*np.median(np.r_[kk[:,0,0],kk[:,1,1]]))
                rec.update(training_positive_depths=positive,focal_px=f,
                           principal_max_px=float(1500*np.max(np.abs(kk[:,:2,2]))),
                           skew_max_px=float(1500*np.max(np.abs(kk[:,0,1]))),
                           fx_fy_minmax_px=[float(1500*np.min(kk[:,[0,1],[0,1]])),
                                           float(1500*np.max(kk[:,[0,1],[0,1]]))])
                if positive!=int(mask.sum()) or not 400<f<4000:
                    raise ValueError('cheirality/focal')
                predicted = f*depth[...,:2]/depth[...,2:3]+[360,640]
                errors = np.linalg.norm((predicted-pixels)[mask],axis=1)
                if not np.isfinite(errors).all() or not np.isfinite(xm).all():
                    raise ValueError('nonfinite metric prediction')
                mse = float(np.mean(errors**2))
                rec.update(eligible=True,training_mse_px2=mse,
                           training_p95_px=float(np.percentile(errors,95)))
                eligible.append((mse,index,-sign,(xm,rr,tt,f)))
            except (ValueError,np.linalg.LinAlgError) as error:
                rec['reject'] = str(error)
    if not eligible:
        checkpoint(label,'metric_upgrade',diagnostic)
        raise ValueError('no rank-three metric candidate passes training eligibility')
    mse,index,negative_sign,chosen = min(eligible,key=lambda a:a[:3])
    diagnostic.update(chosen_root_before_held=index,chosen_sign_before_held=-negative_sign,
                      chosen_training_mse_px2=mse)
    checkpoint(label,'metric_upgrade',diagnostic)
    return chosen


def solve(y,mask,ids,label):
    train = ids%5!=0
    REPORT[label] = {'training_ids':int(train.sum()),'held_ids':int((~train).sum())}
    if label == 'control':
        checkpoint(label,'pencil_control',pencil_self_check())
        archive = ROOT/'assets/private/closed-experiments/0283-projective-varpro/evidence.zip'
        if hashlib.sha256(archive.read_bytes()).hexdigest()!='45636fc9c2d9cb1a534e5ce5f60b0f5865709d5d00ea1377f0fbf497bfd2014f':
            raise ValueError('frozen control prefix hash mismatch')
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError('prefix archive CRC')
            saved = np.load(io.BytesIO(z.read('control-projective.npz')),allow_pickle=False)
            xt,pt = saved['shape'],saved['cameras']
        if xt.shape!=(int(train.sum()),3) or pt.shape!=(len(y),3,4):
            raise ValueError('frozen prefix shape mismatch')
        vi,pi = np.where(mask[:,train])
        projected = np.einsum('nij,nj->ni',pt[vi],np.c_[xt[pi],np.ones(len(pi))])
        predicted = 1500*projected[:,:2]/projected[:,2:3]+[360,640]
        replay = float(np.percentile(np.linalg.norm(predicted-y[:,train][vi,pi],axis=1),95))
        checkpoint(label,'prefix',{'mode':'FROZEN_PREFIX_NEW_UPGRADE','replay_training_p95_px':replay,
                                   'archive_sha256':'45636fc9c2d9cb1a534e5ce5f60b0f5865709d5d00ea1377f0fbf497bfd2014f'})
        if not np.isfinite(replay) or replay>.001 or np.any(projected[:,2]<=0):
            raise ValueError('frozen prefix replay failed')
    else:
        xt,pt = pose_varpro(y[:,train],mask[:,train],label)
        xt,pt = projective_refine(y[:,train],mask[:,train],xt,pt,label)
    init = metric_upgrade(xt,pt,mask[:,train],label,y[:,train])
    cams,ba = bundle(y[:,train],mask[:,train],init[:3],init[3])
    checkpoint(label,'perspective',ba)
    held,errors,rows = held_score(y[:,~train],mask[:,~train],cams)
    checkpoint(label,'held',held)
    np.savez_compressed(OUT/(label+'-evaluation.npz'),errors=errors,views=rows,
                        rotations=cams[1],translations=cams[2],focal=cams[3])
    return cams,held


def bundle(y, mask, initial, initial_f):
    x0, r0, t0 = initial
    v, n = mask.shape
    vi, pi = np.where(mask)
    xy = y[vi, pi]
    # Fix one point coordinate to remove scale,not a shape prior.
    center0 = -r0[0].T @ t0[0]
    axis = int(np.argmax(np.abs(x0[0]-center0)))
    fixed = axis
    free = np.delete(np.arange(n*3), fixed)
    offset = len(free)
    camcount = (v-1)*6
    theta = np.r_[x0.ravel()[free],
                  np.c_[Rotation.from_matrix(r0[1:]).as_rotvec(), t0[1:]].ravel(), np.log(initial_f)]

    def unpack(z):
        xx = x0.ravel().copy()
        xx[free] = z[:offset]
        cams = z[offset:offset+camcount].reshape(-1, 6)
        rr = np.concatenate([r0[:1], Rotation.from_rotvec(cams[:, :3]).as_matrix()])
        tt = np.vstack([t0[0], cams[:, 3:]])
        return xx.reshape(n, 3), rr, tt, np.exp(z[-1])

    started = time.monotonic()

    def residual(z):
        if time.monotonic()-started > 180:
            raise TimeoutError('perspectiveBA180s cap')
        xx, rr, tt, f = unpack(z)
        cc = np.einsum('nij,nj->ni', rr[vi], xx[pi])+tt[vi]
        uv = f*cc[:, :2]/np.maximum(cc[:, 2:3], 1e-4)+[360, 640]
        return np.r_[(uv-xy).ravel(), 100*np.minimum(cc[:, 2]-.001, 0)]

    m = len(vi)
    jac = lil_matrix((m*3, len(theta)), dtype=np.int8)
    pointcols = np.full(n*3, -1)
    pointcols[free] = np.arange(offset)
    for k, (view, point) in enumerate(zip(vi, pi)):
        cols = pointcols[point*3:point*3+3]
        cols = cols[cols >= 0].tolist()
        if view:
            cols += list(range(offset+(view-1)*6, offset+view*6))
        cols += [len(theta)-1]
        for row in (k*2, k*2+1, m*2+k):
            jac[row, cols] = 1
    lower = np.full(len(theta), -np.inf)
    upper = -lower
    lower[-1], upper[-1] = np.log(400), np.log(4000)
    sol = least_squares(residual, theta, jac_sparsity=jac.tocsr(),
                        loss='soft_l1', f_scale=2, max_nfev=60,
                        x_scale='jac', bounds=(lower, upper))
    xx, rr, tt, f = unpack(sol.x)
    cc = np.einsum('nij,nj->ni', rr[vi], xx[pi])+tt[vi]
    errors = np.linalg.norm(f*cc[:, :2]/cc[:, 2:3]+[360, 640]-xy, axis=1)
    diag = {'optimizer_success': bool(sol.success), 'message': sol.message,
            'nfev': sol.nfev, 'focal_px': float(f), 'seconds': time.monotonic()-started,
            'train_p95_px': float(np.percentile(errors, 95)),
            'nonpositive_training_depths': int((cc[:, 2] <= 0).sum()),
            'rotation_determinant_max_error': float(np.max(np.abs(np.linalg.det(rr)-1)))}
    return (xx, rr, tt, f), diag


def held_score(y, mask, cameras):
    _, rr, tt, f = cameras
    k = np.array([[f, 0, 360], [0, f, 640], [0, 0, 1.]])
    p = k @ np.concatenate([rr, tt[..., None]], axis=2)
    centers = -np.einsum('vji,vj->vi', rr, tt)
    errors, frame_rows = [], []
    invalid = weak = 0
    for j in range(mask.shape[1]):
        visible = np.flatnonzero(mask[:, j])
        for target in visible:
            anchors = visible[visible != target]
            rows = np.concatenate([y[a, j, 0]*p[a, 2:3]-p[a, 0:1]
                                   for a in anchors] +
                                  [y[a, j, 1]*p[a, 2:3]-p[a, 1:2] for a in anchors])
            _, sv, vh = np.linalg.svd(rows, full_matrices=False)
            h = vh[-1]
            err = np.inf
            if sv[-2] > 1e-10 and abs(h[3]) > 1e-10:
                x = h[:3]/h[3]
                depth = np.einsum('vij,j->vi', rr[visible], x)+tt[visible]
                rays = x-centers[anchors]
                rays /= np.linalg.norm(rays, axis=1)[:, None]
                angle = np.rad2deg(np.arccos(np.clip(np.min(rays @ rays.T), -1, 1)))
                weak += int(angle < 1)
                if np.isfinite(depth).all() and np.all(depth[:, 2] > 0) and angle >= 1:
                    pred = p[target] @ np.r_[x, 1]
                    err = float(np.linalg.norm(pred[:2]/pred[2]-y[target, j]))
            invalid += int(not np.isfinite(err))
            errors.append(err)
            frame_rows.append(target)
    errors, frame_rows = np.asarray(errors), np.asarray(frame_rows)
    # Do not silently exclude invalid points from percentile or denominator.
    def percentile(e):
        return float(np.sort(e)[int(np.ceil(.95*len(e)))-1]) if len(e) else np.inf
    per = [{'view': i, 'count': int((frame_rows == i).sum()),
            'p95_px': percentile(errors[frame_rows == i])} for i in range(len(rr))]
    diag = {'count': len(errors), 'invalid': invalid, 'weak_anchor_angle': weak,
            'p95_px': percentile(errors), 'per_view': per,
            'threshold_passed': bool(not invalid and percentile(errors) <= 3 and
                 all(a['count'] >= 30 and a['p95_px'] <= 3 for a in per))}
    return diag, errors, frame_rows


def control():
    rng = np.random.default_rng(280)
    x = rng.uniform(-1, 1, (600, 3))*[.8, 1, .6]
    r = Rotation.from_euler('yx', np.c_[[-35, -17, 0, 19, 37], [-8, 5, 0, -4, 7]], degrees=True).as_matrix()
    cc = np.einsum('vij,nj->vni', r, x)+[0, 0, 10]
    y = 1500*cc[..., :2]/cc[..., 2:3]+[360, 640]
    ids = np.arange(600)
    mask = np.arange(5)[:, None] != ((ids//5) % 5)[None]
    cams, held = solve(y, mask, ids, 'control')
    bad = y.copy()
    bad[:, :, 0] += 17*np.arange(5)[:, None]**2
    negative, _, _ = held_score(bad[:, ids % 5 == 0], mask[:, ids % 5 == 0], cams)
    REPORT['control']['negative_p95_px'] = negative['p95_px']
    if not held['threshold_passed'] or held['p95_px'] >= .1 or negative['p95_px'] <= 3:
        raise ValueError('control failed;patient solve not started')
    REPORT['control']['status'] = 'TECHNICAL_CHECK_PASSED'


def patient():
    manifest = ROOT/'assets/private/real-capture-pilot-v1/manifest.json'
    doc = json.loads(manifest.read_text(encoding='utf-8'))
    case = next(c for c in doc['cases'] if c['id'] == 'real-case-001')
    selected = [a for a in doc['inputs'] if case['files']['video'] in (a.get('id'), a.get('path'), a.get('source'))]
    if len(selected) != 1:
        raise ValueError('ambiguous video manifest')
    errors = validate_input_assets({**doc, 'inputs': selected}, manifest.parent)
    if errors:
        raise ValueError(errors)
    archive = ROOT/'assets/private/closed-experiments/0267-native-dense-video/evidence.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != '54aa2b303e4fa6f0599628f677bf359e4125dccd1df867ea70f8b9e19154c612':
        raise ValueError('observation archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if n.endswith('/observations.npz')]
        if len(names) != 1:
            raise ValueError('ambiguous observations')
        data = np.load(io.BytesIO(z.read(names[0])), allow_pickle=False)
        frame, ids, xy = data['frame'], data['ids'], data['xy']
    take = (frame >= 0) & (frame <= 876) & (frame % 12 == 0)
    frame, ids, xy = frame[take], ids[take], xy[take]
    unique, counts = np.unique(ids, return_counts=True)
    unique = unique[counts >= np.where(unique % 5 == 0, 4, 3)]
    y = np.zeros((74, len(unique), 2))
    mask = np.zeros(y.shape[:2], bool)
    index = {int(n): i for i, n in enumerate(unique)}
    for fr, ident, point in zip(frame, ids, xy):
        if int(ident) not in index:
            continue
        vi, pi = int(fr//12), index[int(ident)]
        if mask[vi, pi] or not np.isfinite(point).all():
            raise ValueError('duplicate/nonfinite observation')
        y[vi, pi], mask[vi, pi] = point, True
    REPORT['actual_data'] = {'frames': 74, 'component': [0, 876],
                             'rows': int(mask.sum()), 'video_sha256': selected[0]['sha256']}
    cams, held = solve(y, mask, unique, 'patient')
    ba = REPORT['patient']['perspective']
    valid = (ba['optimizer_success'] and ba['nonpositive_training_depths'] == 0
             and ba['train_p95_px'] <= 3 and 400 < cams[3] < 4000)
    REPORT['status'] = 'PARTIAL_SUCCESS' if valid and held['threshold_passed'] else 'REJECT'


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        control()
        patient()
    except Exception as exc:
        REPORT['failure'] = type(exc).__name__+':'+str(exc)
    finally:
        REPORT['seconds'] = time.monotonic()-start
        (OUT/'report.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')
        print(json.dumps(REPORT))


