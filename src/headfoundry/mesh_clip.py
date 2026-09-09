"""Exact axis-plane triangle clipping with shared intersection vertices; no cap."""
import numpy as np


def clip_below(vertices, faces, axis, limit):
    """Keep coordinates <= limit. Return mesh and original vertex IDs (-1=new)."""
    v=np.asarray(vertices,float);f=np.asarray(faces)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or not np.isfinite(v).all()
            or f.ndim!=2 or f.shape[1:]!=(3,) or not np.issubdtype(f.dtype,np.integer)
            or np.any(f<0) or np.any(f>=len(v)) or axis not in (0,1,2) or not np.isfinite(limit)):
        raise ValueError('finite triangle mesh and axis plane required')
    points=v.tolist();source=list(range(len(v)));cache={};triangles=[]
    def intersection(a,b):
        if v[a,axis]==limit:return int(a)
        if v[b,axis]==limit:return int(b)
        key=tuple(sorted((int(a),int(b))))
        if key not in cache:
            t=(limit-v[a,axis])/(v[b,axis]-v[a,axis])
            point=v[a]+t*(v[b]-v[a]);point[axis]=limit
            cache[key]=len(points);points.append(point.tolist());source.append(-1)
        return cache[key]
    for face in f:
        polygon=[]
        for a,b in zip(face,np.roll(face,-1)):
            inside_a=v[a,axis]<=limit;inside_b=v[b,axis]<=limit
            if inside_a:polygon.append(int(a))
            if inside_a!=inside_b:polygon.append(intersection(a,b))
        polygon=list(dict.fromkeys(polygon))
        for i in range(1,len(polygon)-1):
            tri=[polygon[0],polygon[i],polygon[i+1]];p=np.array([points[j] for j in tri])
            if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))>1e-14:triangles.append(tri)
    if not triangles:raise ValueError('empty clipped surface')
    used,inverse=np.unique(triangles,return_inverse=True)
    return np.asarray(points)[used],inverse.reshape(-1,3),np.asarray(source)[used]
