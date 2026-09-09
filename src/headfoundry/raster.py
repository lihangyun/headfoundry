"""NumPy CPU rasterizer: z-buffer and perspective-correct texture coordinates.

UV coordinates are texture pixels, origin top left. Cameras use OpenCV axes.
All vertices must be beyond the near plane; near-plane clipping is not supported.
"""
import numpy as np


def lift_pixels(vertices, faces, extrinsic, intrinsic, pixels):
    """Exact visible triangle + 3D barycentric weights; misses are -1/NaN.

    No snapping to nearby surfaces. This proves projection, not that a detected
    pixel denotes the same anatomical feature in another image.
    """
    v=np.asarray(vertices,float);f=np.asarray(faces);e=np.asarray(extrinsic,float)
    k=np.asarray(intrinsic,float);pixels=np.asarray(pixels,float)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or f.ndim!=2 or f.shape[1:]!=(3,)
            or not np.issubdtype(f.dtype,np.integer) or np.any(f<0) or np.any(f>=len(v))
            or e.shape!=(3,4) or k.shape!=(3,3) or pixels.ndim!=2 or pixels.shape[1:]!=(2,)
            or not all(np.isfinite(a).all() for a in (v,e,k,pixels)) or not np.allclose(k[2],[0,0,1])):
        raise ValueError('finite mesh, camera and pixels required')
    cam=v@e[:,:3].T+e[:,3]
    if np.any(cam[:,2]<=1e-6):raise ValueError('near-plane clipping required')
    h=cam@k.T;uv=h[:,:2]/h[:,2:];a,b,c=np.moveaxis(uv[f],1,0)
    den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
    valid=np.abs(den)>1e-12;den=np.where(valid,den,1)
    hit_ids=np.full(len(pixels),-1,int);weights=np.full((len(pixels),3),np.nan)
    for i,(x,y) in enumerate(pixels):
        w0=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den
        w1=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den
        screen=np.c_[w0,w1,1-w0-w1]
        candidates=np.flatnonzero(valid&(screen.min(1)>=-1e-10))
        if not len(candidates):continue
        inverse=screen[candidates]/cam[f[candidates],2]
        index=int(np.argmax(inverse.sum(1)))
        hit_ids[i]=candidates[index];weights[i]=inverse[index]/inverse[index].sum()
    return hit_ids,weights


def render(vertices, faces, extrinsic, intrinsic, size, uv=None, texture=None, *, smooth_shading=False):
    vertices = np.asarray(vertices, float)
    faces = np.asarray(faces)
    e, k = np.asarray(extrinsic, float), np.asarray(intrinsic, float)
    width, height = size
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.isfinite(vertices).all():
        raise ValueError('invalid vertices')
    if faces.ndim != 2 or faces.shape[1] != 3 or not np.issubdtype(faces.dtype, np.integer) or np.any(faces < 0) or np.any(faces >= len(vertices)):
        raise ValueError('invalid triangles')
    if e.shape != (3,4) or k.shape != (3,3) or not np.isfinite(e).all() or not np.isfinite(k).all():
        raise ValueError('invalid cameras')
    if not np.allclose(k[2], [0,0,1]) or min(width,height) <= 0:
        raise ValueError('invalid intrinsic or output size')
    camera = vertices @ e[:,:3].T + e[:,3]
    if np.any(camera[:,2] <= 1e-6):
        raise ValueError('near-plane clipping required')
    h = camera @ k.T
    pixels = h[:,:2] / h[:,2:]
    if (uv is None) != (texture is None):
        raise ValueError('texture and uv must be supplied together')
    if smooth_shading and texture is not None:
        raise ValueError('smooth shading is a clay-only diagnostic')
    normals=None
    if smooth_shading:
        # Area-weighted shared-vertex normals. No geometry smoothing, welding or
        # crease inference: split/hard edges remain a topology responsibility.
        face_normals=np.cross(camera[faces[:,1]]-camera[faces[:,0]],camera[faces[:,2]]-camera[faces[:,0]])
        normals=np.zeros_like(camera)
        for corner in range(3):np.add.at(normals,faces[:,corner],face_normals)
        normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
    if texture is not None:
        uv, texture = np.asarray(uv,float), np.asarray(texture,float)
        if uv.shape != (len(vertices),2) or texture.ndim != 3 or texture.shape[2] != 3 or min(texture.shape[:2]) < 1:
            raise ValueError('invalid texture mapping')
        if not np.isfinite(uv).all() or not np.isfinite(texture).all():
            raise ValueError('non-finite texture')
    image = np.zeros((height,width,3),np.uint8)
    depth = np.full((height,width),np.inf)
    face_ids = np.full((height,width),-1,int)
    light = np.array([-.2,-.4,-1.]); light /= np.linalg.norm(light)
    for face_id, face in enumerate(faces):
        tri = pixels[face]
        lo = np.maximum(np.floor(tri.min(axis=0)).astype(int),[0,0])
        hi = np.minimum(np.ceil(tri.max(axis=0)).astype(int),[width-1,height-1])
        if np.any(lo>hi):
            continue
        a,b,c = tri
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-10:
            continue
        yy,xx = np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        x,y = xx+.5,yy+.5
        w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        w=np.stack([w0,w1,1-w0-w1],axis=-1)
        inverse=w/camera[face,2]
        z=1/np.maximum(inverse.sum(axis=-1),1e-30)
        keep=(w.min(axis=-1)>=-1e-9)&(z<depth[yy,xx])
        if not keep.any():
            continue
        if texture is not None:
            coords=(inverse@uv[face])*z[...,None]
            tx=np.clip(coords[...,0],0,texture.shape[1]-1)
            ty=np.clip(coords[...,1],0,texture.shape[0]-1)
            x0,y0=np.floor(tx).astype(int),np.floor(ty).astype(int)
            x1,y1=np.minimum(x0+1,texture.shape[1]-1),np.minimum(y0+1,texture.shape[0]-1)
            fx,fy=(tx-x0)[...,None],(ty-y0)[...,None]
            color=(texture[y0,x0]*(1-fx)+texture[y0,x1]*fx)*(1-fy)+(texture[y1,x0]*(1-fx)+texture[y1,x1]*fx)*fy
        else:
            normal=np.cross(camera[face[1]]-camera[face[0]],camera[face[2]]-camera[face[0]])
            normal/=max(np.linalg.norm(normal),1e-12)
            if normals is not None:
                interpolated=(inverse@normals[face])*z[...,None]
                lengths=np.linalg.norm(interpolated,axis=-1,keepdims=True)
                normal=np.where(lengths>1e-12,interpolated/np.maximum(lengths,1e-12),normal)
            brightness=.3+.7*abs(normal@light)
            color=np.broadcast_to(np.array([190,198,208])*np.asarray(brightness)[...,None],(*xx.shape,3))
        image[yy[keep],xx[keep]]=np.clip(color[keep],0,255).astype(np.uint8)
        depth[yy[keep],xx[keep]]=z[keep]
        face_ids[yy[keep],xx[keep]]=face_id
    return image,depth,face_ids
