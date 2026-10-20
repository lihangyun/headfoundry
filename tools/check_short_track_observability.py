"""Synthetic local observability counterexample,not a camera/head estimator."""
import json
import cv2
import numpy as np


def skew(x):
    a,b,c=x
    return np.array([[0,-c,b],[c,0,-a],[-b,a,0.]])


def check():
    if not __debug__:raise RuntimeError("Run without -O")
    rng=np.random.default_rng(268)
    points=rng.uniform([-1,-1,4],[1,1,7],(30,3))
    rotvec=np.array([[0,0,0],[.05,.12,-.03],[-.07,.3,.05],[.12,-.2,-.07],[-.06,-.4,.04]])
    rotations=np.array([cv2.Rodrigues(r)[0] for r in rotvec])
    translations=np.array([[0,0,0],[.4,-.1,.1],[1.1,.2,-.1],[1.7,-.25,.3],[2.2,.3,-.2]])
    observations=[(camera,point) for group in range(3) for point in range(10*group,10*(group+1)) for camera in range(group,group+3)]
    assert not any((0,p) in observations and (4,p) in observations for p in range(30))
    columns=114
    def projections(delta,scale=1):
        xyz=(points+delta[24:].reshape(30,3))*scale
        rr=rotations.copy();tt=translations.copy()
        for camera in range(1,5):
            start=1 if camera==1 else 6+(camera-2)*6
            rr[camera]=cv2.Rodrigues(delta[start:start+3])[0]@rotations[camera]
            if camera==1:tt[camera,1:]+=delta[4:6]
            else:tt[camera]+=delta[start+3:start+6]
        tt*=scale
        result=[]
        for camera,point in observations:
            q=rr[camera]@xyz[point]+tt[camera]
            if q[2]<=0:raise ValueError("Nonpositive synthetic depth")
            result.extend(900*np.exp(delta[0])*q[:2]/q[2]+[320,240])
        return np.array(result)
    jacobian=np.zeros((180,columns))
    for i,(camera,point) in enumerate(observations):
        rotated=rotations[camera]@points[point];q=rotated+translations[camera]
        x,y,z=q
        d=900/z*np.array([[1,0,-x/z],[0,1,-y/z]])
        rows=slice(2*i,2*i+2)
        jacobian[rows,0]=900*q[:2]/z
        jacobian[rows,24+3*point:27+3*point]=d@rotations[camera]
        if camera:
            start=1 if camera==1 else 6+(camera-2)*6
            jacobian[rows,start:start+3]=d@(-skew(rotated))
            if camera==1:jacobian[rows,4:6]=d[:,1:]
            else:jacobian[rows,start+3:start+6]=d
    derivative_errors=[]
    for h in [1e-5,1e-6]:
        numerical=np.empty_like(jacobian)
        for col in range(columns):
            delta=np.zeros(columns);delta[col]=h
            numerical[:,col]=(projections(delta)-projections(-delta))/(2*h)
        error=float(np.max(np.abs(numerical-jacobian)));derivative_errors.append(error)
        if error>1e-5:raise AssertionError("Analytic derivative disagrees")
    singular=np.linalg.svd(jacobian,compute_uv=False)
    rank=int((singular>1e-4).sum())
    keep=np.repeat([camera!=4 for camera,point in observations],2)
    negative=np.linalg.svd(jacobian[keep],compute_uv=False)
    negative_rank=int((negative>1e-4).sum())
    delta=np.zeros(columns)
    scale_error=float(np.max(np.abs(projections(delta,scale=2.3)-projections(delta))))
    if rank!=columns or negative_rank>=columns or scale_error>1e-9:
        raise AssertionError("Registered observability/gauge control failed")
    if not all(np.isfinite(singular)) or not np.allclose(np.linalg.det(rotations),1,atol=1e-12):
        raise AssertionError("Invalid finite/proper geometry")
    return dict(status="TECHNICAL_CHECK_PASSED",scope="synthetic_local_counterexample_not_reconstruction",
                cameras=5,points=30,observations=len(observations),parameters=columns,rank=rank,
                smallest_singular_value=float(singular[-1]),disconnected_rank=negative_rank,
                derivative_max_errors=derivative_errors,scale_projection_error_px=scale_error,
                point_visible_first_and_last=False,human_material_read=False)


if __name__=="__main__":print(json.dumps(check()))
