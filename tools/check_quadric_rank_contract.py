"""Necessary rank-three quadric pencil checks,not a camera/head acceptance test."""
import json
import numpy as np
from scipy.linalg import eig


def quadric_candidates(a,b):
    if np.iscomplexobj(a) or np.iscomplexobj(b):
        raise ValueError('real quadric bases required')
    a,b = np.asarray(a,float),np.asarray(b,float)
    if (a.shape!=(4,4) or b.shape!=(4,4) or not np.isfinite(a).all()
            or not np.isfinite(b).all() or not np.allclose(a,a.T,atol=1e-12,rtol=0)
            or not np.allclose(b,b.T,atol=1e-12,rtol=0)):
        raise ValueError('finite symmetric4x4quadric bases required')
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


def check():
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
    for invalid in (np.eye(3),np.full((4,4),np.nan),np.triu(np.ones((4,4)))):
        try:
            quadric_candidates(invalid,b)
        except ValueError:
            pass
        else:
            raise ValueError('invalid basis was not rejected')
    return {'status':'TECHNICAL_CHECK_PASSED','positive_rank_three':len(first),'roots':records}


if __name__ == '__main__':
    print(json.dumps(check()))

