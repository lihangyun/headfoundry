"""Small pure-NumPy geometry helpers for a known-scan diagnostic, not a fitter."""
import numpy as np


def look_at_origin(center):
    center=np.asarray(center,float)
    if center.shape!=(3,) or not np.isfinite(center).all() or np.linalg.norm(center)<1e-8:
        raise ValueError('Finite nonzero camera center required')
    forward=-center/np.linalg.norm(center)
    right=np.cross(forward,[0.,1,0])
    if np.linalg.norm(right)<1e-8:
        raise ValueError('Camera direction parallel to up')
    right/=np.linalg.norm(right)
    rotation=np.stack([right,np.cross(forward,right),forward])
    return np.c_[rotation,-rotation@center]


def sample_surface(vertices,faces,count=5000,seed=230):
    vertices,faces=np.asarray(vertices,float),np.asarray(faces)
    if (vertices.ndim!=2 or vertices.shape[1:]!=(3,) or not np.isfinite(vertices).all()
            or faces.ndim!=2 or faces.shape[1:]!=(3,) or not len(faces)
            or not np.issubdtype(faces.dtype,np.integer) or (faces<0).any() or (faces>=len(vertices)).any()
            or not isinstance(count,int) or count<=0):
        raise ValueError('Finite triangular mesh and positive point count required')
    triangles=vertices[faces]
    area=np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)/2
    if (area<=0).any():
        raise ValueError('Degenerate source triangle')
    rng=np.random.default_rng(seed)
    ids=rng.choice(len(faces),count,p=area/area.sum())
    uv=rng.random((count,2))
    root=np.sqrt(uv[:,0])
    bary=np.c_[1-root,root*(1-uv[:,1]),root*uv[:,1]]
    return np.einsum('ni,nij->nj',bary,triangles[ids]),ids,bary


def fundamental_from_cameras(intrinsic,first,second):
    k=np.asarray(intrinsic,float)
    a,b=np.asarray(first,float),np.asarray(second,float)
    if k.shape!=(3,3) or a.shape!=(3,4) or b.shape!=(3,4) or not all(np.isfinite(x).all() for x in (k,a,b)):
        raise ValueError('Finite camera matrices required')
    relative_rotation=b[:,:3]@a[:,:3].T
    t=b[:,3]-relative_rotation@a[:,3]
    skew=np.array([[0.,-t[2],t[1]],[t[2],0.,-t[0]],[-t[1],t[0],0.]])
    inverse=np.linalg.inv(k)
    matrix=inverse.T@skew@relative_rotation@inverse
    if np.linalg.norm(matrix)<1e-12:
        raise ValueError('No stereo baseline')
    return matrix/np.linalg.norm(matrix)
