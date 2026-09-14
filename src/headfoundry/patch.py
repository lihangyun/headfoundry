"""Conforming disk triangulation of a simple 2D polygon, preserving its boundary."""
import numpy as np


def improve_diagonals(points, triangles, max_passes=40):
    """Improve worst planar pair quality, preserving vertices/boundary edges.

    Input must be an embedded conforming triangulation with consistent winding.
    Connectivity checks here do not certify absence of geometric overlaps.
    Returns a new face array; no globally optimal quality is guaranteed.
    """
    p=np.asarray(points,float);f=np.asarray(triangles)
    if (p.ndim!=2 or p.shape[1:]!=(2,) or not np.isfinite(p).all()
            or f.ndim!=2 or f.shape[1:]!=(3,) or not len(f)
            or not np.issubdtype(f.dtype,np.integer) or np.any(f<0) or np.any(f>=len(p))
            or not isinstance(max_passes,int) or isinstance(max_passes,bool) or max_passes<1):
        raise ValueError('finite planar triangles and positive integer pass limit required')
    f=f.copy()
    cross=lambda a,b:a[...,0]*b[...,1]-a[...,1]*b[...,0]
    signed=cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
    sign=np.sign(signed[0])
    if np.any(sign*signed<=0):raise ValueError('nondegenerate consistently wound triangles required')
    def quality(faces):
        q=p[faces];area=sign*cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
        return 2*np.sqrt(3)*area/((q-np.roll(q,1,axis=1))**2).sum(axis=(1,2))
    for _ in range(max_passes):
        adjacent={}
        for i,face in enumerate(f):
            for a,b,c in zip(face,np.roll(face,-1),np.roll(face,-2)):
                adjacent.setdefault(tuple(sorted((int(a),int(b)))),[]).append((i,int(a),int(b),int(c)))
        for rows in adjacent.values():
            if len(rows)>2 or (len(rows)==2 and rows[0][1:3]!=rows[1][2:0:-1]):
                raise ValueError('nonmanifold or inconsistently paired edge')
        touched=set();count=0
        for rows in adjacent.values():
            if len(rows)!=2:continue
            (i,a,b,c),(j,_,_,d)=rows
            if i in touched or j in touched or tuple(sorted((c,d))) in adjacent:continue
            candidate=np.array([[c,d,b],[d,c,a]])
            new=quality(candidate)
            if new.min()<=0 or new.min()<=quality(f[[i,j]]).min()+1e-10:continue
            f[[i,j]]=candidate;touched.update([i,j]);count+=1
        if not count:break
    return f


def harmonic_depth(points, triangles, boundary_values):
    """Piecewise-linear FEM Laplace extension of leading-vertex scalar values.

    Requires the optional SciPy geometry dependency. Uses planar triangle
    geometry, not uniform graph degree; affine fields are reproduced exactly.
    """
    import warnings
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve, MatrixRankWarning
    p=np.asarray(points,float);f=np.asarray(triangles);values=np.asarray(boundary_values,float)
    if (p.ndim!=2 or p.shape[1:]!=(2,) or not np.isfinite(p).all()
            or f.ndim!=2 or f.shape[1:]!=(3,) or not len(f) or not np.issubdtype(f.dtype,np.integer)
            or np.any(f<0) or np.any(f>=len(p)) or values.ndim!=1 or not 0<len(values)<=len(p)
            or not np.isfinite(values).all()):raise ValueError('finite planar triangulation and boundary values required')
    q=p[f];den=(q[:,1,0]-q[:,0,0])*(q[:,2,1]-q[:,0,1])-(q[:,1,1]-q[:,0,1])*(q[:,2,0]-q[:,0,0])
    if np.any(abs(den)<1e-14):raise ValueError('degenerate planar triangle')
    delta=np.roll(q,-1,axis=1)-np.roll(q,-2,axis=1)
    gradient=np.stack([delta[:,:,1],-delta[:,:,0]],axis=2)
    stiffness=np.einsum('nik,njk->nij',gradient,gradient)/(2*abs(den[:,None,None]))
    rows=np.broadcast_to(f[:,:,None],stiffness.shape);cols=np.broadcast_to(f[:,None,:],stiffness.shape)
    system=coo_matrix((stiffness.ravel(),(rows.ravel(),cols.ravel())),shape=(len(p),len(p))).tocsr()
    n=len(values);result=np.empty(len(p));result[:n]=values
    if n<len(p):
        rhs=-system[n:,:n]@values
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error',MatrixRankWarning)
                result[n:]=spsolve(system[n:,n:],rhs)
        except MatrixRankWarning as error:raise ValueError('unconstrained or singular patch') from error
        if not np.isfinite(result).all() or not np.allclose(system[n:,n:]@result[n:],rhs,atol=1e-8,rtol=1e-8):
            raise ValueError('harmonic extension failed')
    return result


def triangulate_disk(boundary, spacing):
    """Ear-clip then refine interior edges; never split supplied boundary edges.

    No holes or intersecting/touching boundary segments. Long boundary edges
    impose a local spacing floor on their endpoints. Not a 3D collision test.
    """
    p=np.asarray(boundary,float)
    if (p.ndim!=2 or p.shape[1:]!=(2,) or len(p)<3 or not np.isfinite(p).all()
            or not np.isscalar(spacing) or not np.isfinite(spacing) or spacing<=0):
        raise ValueError('finite 2D boundary and positive spacing required')
    n=len(p);scale=max(float(np.ptp(p,axis=0).max()),1.);eps=1e-12*scale**2
    cross=lambda a,b:a[...,0]*b[...,1]-a[...,1]*b[...,0]
    if len(np.unique(p,axis=0))!=n:raise ValueError('duplicate boundary points')
    def on_segment(a,b,q):
        return abs(cross(b-a,q-a))<=eps and np.dot(q-a,q-b)<=eps
    for i in range(n):
        a,b=p[i],p[(i+1)%n]
        for j in range(i+1,n):
            if j==i+1 or (i==0 and j==n-1):continue
            c,d=p[j],p[(j+1)%n]
            ab=cross(b-a,c-a)*cross(b-a,d-a);cd=cross(d-c,a-c)*cross(d-c,b-c)
            if (ab<0 and cd<0) or any((on_segment(a,b,c),on_segment(a,b,d),on_segment(c,d,a),on_segment(c,d,b))):
                raise ValueError('self-intersecting or touching boundary')
    signed=float(cross(p,np.roll(p,-1,axis=0)).sum())
    if abs(signed)<=eps:raise ValueError('zero area polygon')
    orientation=np.sign(signed);remaining=list(range(n));faces=[]
    while len(remaining)>3:
        for index,b in enumerate(remaining):
            a,c=remaining[index-1],remaining[(index+1)%len(remaining)]
            if orientation*cross(p[b]-p[a],p[c]-p[a])<=eps:continue
            other=p[[i for i in remaining if i not in (a,b,c)]]
            inside=np.ones(len(other),bool)
            for u,v in [(a,b),(b,c),(c,a)]:inside &= orientation*cross(p[v]-p[u],other-p[u])>=-eps
            if inside.any():continue
            faces.append([a,b,c]);remaining.pop(index);break
        else:raise ValueError('polygon cannot be triangulated without degeneracy')
    faces.append(remaining);faces=np.asarray(faces,int)
    lengths=np.linalg.norm(p-np.roll(p,-1,axis=0),axis=1)
    limits=np.maximum(lengths,np.roll(lengths,1))
    for _ in range(16):
        all_edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
        edges,counts=np.unique(all_edges,axis=0,return_counts=True)
        threshold=np.maximum(spacing,limits[edges].max(1))
        marked=edges[(counts==2)&(np.linalg.norm(p[edges[:,1]]-p[edges[:,0]],axis=1)>threshold*(1+1e-10))]
        if not len(marked):return p,faces
        midpoint={tuple(edge):len(p)+i for i,edge in enumerate(marked)}
        p=np.r_[p,p[marked].mean(1)];limits=np.r_[limits,np.zeros(len(marked))];refined=[]
        for face in faces:
            mids=[midpoint.get(tuple(sorted((int(a),int(b))))) for a,b in zip(face,np.roll(face,-1))]
            count=sum(m is not None for m in mids)
            if count==0:refined.append(face.tolist());continue
            if count==3:
                a,b,c=face;x,y,z=mids
                refined.extend([[a,x,z],[x,b,y],[z,y,c],[x,y,z]]);continue
            start=next(i for i in range(3) if mids[i] is not None and (count==1 or mids[(i+1)%3] is not None))
            a,b,c=np.roll(face,-start);x=mids[start]
            if count==1:refined.extend([[a,x,c],[x,b,c]])
            else:
                y=mids[(start+1)%3];refined.extend([[x,b,y],[a,x,c],[x,y,c]])
        faces=np.asarray(refined,int)
    raise ValueError('interior refinement did not converge')
