"""Analytic derivative at frozen cameras/XYZ;no optimizer or priors."""
import cv2
import numpy as np

from short_track_camera import intrinsics,project


def linearize(k,poses,points,observations,anchor,baseline):
    """Match bundle_stationarity's logf/SE3/unit-baseline/XYZ column gauge."""
    k,poses,points,observations=[np.asarray(x,float) for x in (k,poses,points,observations)]
    if (k.shape!=(3,3) or poses.ndim!=3 or poses.shape[1:]!=(4,4) or len(poses)<2
            or points.ndim!=2 or points.shape[1:]!=(3,) or len(points)==0
            or observations.ndim!=2 or observations.shape[1:]!=(4,) or len(observations)==0
            or not all(np.isfinite(x).all() for x in (k,poses,points,observations))
            or not isinstance(anchor,int) or not isinstance(baseline,int)
            or not 0<=anchor<len(poses) or not 0<=baseline<len(poses) or anchor==baseline
            or k[0,0]<=0 or not np.allclose(k,intrinsics(np.log(k[0,0])),atol=1e-10,rtol=0)):
        raise ValueError('finite native square-focal camera/point/observation schema required')
    ids=observations[:,:2].astype(int)
    if (not np.array_equal(ids,observations[:,:2]) or (ids<0).any()
            or (ids[:,0]>=len(poses)).any() or (ids[:,1]>=len(points)).any()
            or not np.allclose(poses[anchor],np.eye(4),atol=1e-10,rtol=0)
            or not np.isclose(np.linalg.norm(poses[baseline,:3,3]),1.,atol=1e-10,rtol=0)
            or not np.allclose(poses[:,3,:],[0,0,0,1],atol=1e-12,rtol=0)
            or not np.allclose(poses[:,:3,:3]@poses[:,:3,:3].transpose(0,2,1),np.eye(3),atol=1e-10,rtol=0)
            or not (np.linalg.det(poses[:,:3,:3])>0).all()):
        raise ValueError('valid IDs,proper SE3,identity anchor and unit baseline required')
    source,depth=project(k,poses,points,observations)
    if (depth<=1e-9).any() or not np.isfinite(source).all():raise ValueError('unclamped positive projection domain required')
    blocks={};offset=1
    for camera in range(len(poses)):
        if camera!=anchor:
            size=5 if camera==baseline else 6;blocks[camera]=slice(offset,offset+size);offset+=size
    jac=np.zeros((2*len(observations),offset+3*len(points)));uv=np.empty((len(observations),2))
    for camera,pose in enumerate(poses):
        slots=np.flatnonzero(ids[:,0]==camera)
        if not len(slots):continue
        selected=points[ids[slots,1]];rotation=pose[:3,:3];translation=pose[:3,3]
        image,derivative=cv2.projectPoints(selected,cv2.Rodrigues(rotation)[0],translation,k,None)
        uv[slots]=image.reshape(-1,2);rows=(2*slots[:,None]+[0,1]).ravel()
        jac[rows,0]=k[0,0]*(derivative[:,6]+derivative[:,7])
        if camera!=anchor:
            camera_jac=derivative[:,:6]
            if camera==baseline:
                theta=np.arctan2(translation[1],translation[0]);phi=np.arctan2(translation[2],np.linalg.norm(translation[:2]))
                chain=np.array([[-np.cos(phi)*np.sin(theta),-np.sin(phi)*np.cos(theta)],
                                [np.cos(phi)*np.cos(theta),-np.sin(phi)*np.sin(theta)],
                                [0,np.cos(phi)]])
                camera_jac=np.column_stack((derivative[:,:3],derivative[:,3:6]@chain))
            block=blocks[camera];jac[np.ix_(rows,np.arange(block.start,block.stop))]=camera_jac
        local=selected@rotation.T+translation
        for slot,point,q in zip(slots,ids[slots,1],local):
            perspective=k[0,0]/q[2]*np.array([[1,0,-q[0]/q[2]],[0,1,-q[1]/q[2]]])
            jac[2*slot:2*slot+2,offset+3*point:offset+3*point+3]=perspective@rotation
    replay=float(np.max(abs(uv-source)))
    if replay>1e-9:raise ValueError('OpenCV/native projection disagreement')
    return (uv-observations[:,2:]).ravel(),jac,replay
