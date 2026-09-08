"""Experimental projective distance fusion; unknown space is never filled."""
import numpy as np
from .da3 import depth_to_world


def _sample_depth(depth, mask, uv, bilinear):
    """Return supported query indices and depth; bilinear needs four valid pixels."""
    h,w=depth.shape
    xy=np.floor(uv).astype(int) if bilinear else np.rint(uv).astype(int)
    valid=(xy[:,0]>=0)&(xy[:,1]>=0)&(xy[:,0]<w-int(bilinear))&(xy[:,1]<h-int(bilinear))
    indices=np.flatnonzero(valid); x,y=xy[indices].T
    supported=mask[y,x]
    if bilinear:supported=supported&mask[y,x+1]&mask[y+1,x]&mask[y+1,x+1]
    indices=indices[supported]; x,y=xy[indices].T
    if not bilinear:return indices,depth[y,x]
    fx,fy=(uv[indices]-xy[indices]).T
    sampled=(depth[y,x]*(1-fx)+depth[y,x+1]*fx)*(1-fy)+(depth[y+1,x]*(1-fx)+depth[y+1,x+1]*fx)*fy
    return indices,sampled


def fuse_grid(depth, extrinsics, intrinsics, masks, lower, upper, resolution=80, truncation=.02, *, free_space=False, bilinear=False):
    depth=np.asarray(depth,float); masks=np.asarray(masks)
    extrinsics=np.asarray(extrinsics,float); intrinsics=np.asarray(intrinsics,float)
    depth_to_world(depth,extrinsics,intrinsics)  # shared camera/depth validation
    lower,upper=np.asarray(lower,float),np.asarray(upper,float)
    if (masks.shape!=depth.shape or masks.dtype!=bool or lower.shape!=(3,)
            or upper.shape!=(3,) or not np.isfinite([lower,upper]).all()
            or np.any(upper<=lower) or not isinstance(resolution,int)
            or not 3<=resolution<=256 or not np.isfinite(truncation) or truncation<=0
            or not isinstance(free_space,bool) or not isinstance(bilinear,bool)):
        raise ValueError('invalid grid, masks or truncation')
    axes=[np.linspace(a,b,resolution) for a,b in zip(lower,upper)]
    xyz=np.stack(np.meshgrid(*axes,indexing='ij'),-1)
    points=xyz.reshape(-1,3); total=np.zeros(len(points)); count=np.zeros(len(points),int)
    for d,e,k,m in zip(depth,extrinsics,intrinsics,masks):
        cam=points@e[:,:3].T+e[:,3]; projected=cam@k.T
        forward=np.flatnonzero(cam[:,2]>0)
        uv=projected[forward,:2]/projected[forward,2:]
        selected,sampled=_sample_depth(d,m,uv,bilinear)
        indices=forward[selected]
        signed=sampled-cam[indices,2]
        # Neither mode observes farther than one band behind a depth hit.
        # Optional free-space evidence extends toward the camera, not behind it.
        keep=(signed>=-truncation) if free_space else (np.abs(signed)<=truncation)
        total[indices[keep]]+=np.minimum(signed[keep]/truncation,1); count[indices[keep]]+=1
    values=np.divide(total,count,out=np.zeros_like(total),where=count>0)
    return xyz,values.reshape(xyz.shape[:3]),count.reshape(xyz.shape[:3])


def extract_surface(xyz, values, known):
    """Marching tetrahedra with shared edge vertices and positive-distance normals."""
    xyz=np.asarray(xyz,float); values=np.asarray(values,float); known=np.asarray(known)
    if (xyz.shape!=values.shape+(3,) or values.ndim!=3 or min(values.shape)<2
            or known.shape!=values.shape or known.dtype!=bool
            or not np.isfinite(xyz).all() or not np.isfinite(values).all()):
        raise ValueError('finite grid and boolean known mask required')
    nodes=np.arange(values.size).reshape(values.shape)
    corners=[nodes[i:values.shape[0]-1+i,j:values.shape[1]-1+j,k:values.shape[2]-1+k].ravel()
             for i,j,k in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
    cubes=np.stack(corners,1); cubes=cubes[known.ravel()[cubes].all(1)]
    p=xyz.reshape(-1,3); v=values.ravel(); edge_groups=[]; directions=[]
    for tet in [[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6],[0,5,1,6]]:
        ids=cubes[:,tet]; negative=v[ids]<0
        codes=negative@np.array([1,2,4,8])
        for code in range(1,15):
            rows=ids[codes==code]
            if not len(rows):continue
            inside=[i for i in range(4) if code&(1<<i)]; outside=[i for i in range(4) if i not in inside]
            if len(inside)==1 or len(outside)==1:
                one,many=(inside,outside) if len(inside)==1 else (outside,inside)
                patterns=[[(one[0],j) for j in many]]
            else:
                a,b=inside; c,d=outside
                patterns=[[(a,c),(a,d),(b,c)],[(a,d),(b,d),(b,c)]]
            direction=p[rows[:,outside]].mean(1)-p[rows[:,inside]].mean(1)
            for pattern in patterns:
                edge_groups.append(np.stack([rows[:,pair] for pair in pattern],1))
                directions.append(direction)
    if not edge_groups:return np.empty((0,3)),np.empty((0,3),int)
    edges=np.sort(np.concatenate(edge_groups).reshape(-1,2),axis=1)
    unique,inverse=np.unique(edges,axis=0,return_inverse=True)
    a,b=unique.T; t=v[a]/(v[a]-v[b]); vertices=p[a]+t[:,None]*(p[b]-p[a])
    faces=inverse.reshape(-1,3)
    normals=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
    flip=(normals*np.concatenate(directions)).sum(1)<0
    faces[flip]=faces[flip][:,[0,2,1]]
    keep=np.linalg.norm(normals,axis=1)>1e-12
    used,remap=np.unique(faces[keep],return_inverse=True)
    return vertices[used],remap.reshape(-1,3)
