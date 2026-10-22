"""Opt-in image-only patch refinement;no asset,truth,medical or default entry."""
import time

import cv2
import numpy as np
from scipy import sparse
from scipy.optimize import least_squares

from direct_patch_camera import residual
from short_track_camera import intrinsics,project,write


OFFSETS=np.array([[0,0],[-2,0],[2,0],[0,-2],[0,2],[-1,-1],[1,1],[-1,1]])


def refine(images,queries,k,poses,points,train,held,folder):
    start_time=time.monotonic()
    origin=poses[0].copy()
    points=points@origin[:3,:3].T+origin[:3,3]
    rotations=poses[:,:3,:3]@origin[:3,:3].T
    translations=poses[:,:3,3]-np.einsum('nij,j->ni',rotations,origin[:3,3])
    baseline=int(np.argmax(np.linalg.norm(translations,axis=1)))
    length=np.linalg.norm(translations[baseline])
    if baseline==0 or length<=1e-9 or (points[:,2]<=0).any():
        raise ValueError('invalid estimated depth/baseline gauge')
    points/=length;translations/=length
    variables=[float(np.log(k[0,0]))];blocks={};sizes={}
    for camera in range(1,len(images)):
        block=cv2.Rodrigues(rotations[camera])[0].ravel().tolist()
        t=translations[camera]
        if camera==baseline:
            block.extend([float(np.arctan2(t[1],t[0])),float(np.arctan2(t[2],np.linalg.norm(t[:2])))])
        else:
            block.extend(t.tolist())
        blocks[camera]=len(variables);sizes[camera]=len(block)
        variables.extend(block)
    depth_offset=len(variables);variables.extend(np.log(1/points[:,2]))
    exposure_offset=len(variables);variables.extend(np.zeros(2*(len(images)-1)))
    seed=np.asarray(variables)
    lower,upper=seed.copy(),seed.copy()
    lower[0],upper[0]=np.log(640.),np.log(5120.)
    for camera,index in blocks.items():
        lower[index:index+3]-=.1;upper[index:index+3]+=.1
        n=sizes[camera]-3;delta=.1 if camera==baseline else .2
        lower[index+3:index+3+n]-=delta;upper[index+3:index+3+n]+=delta
    lower[depth_offset:exposure_offset]-=.3;upper[depth_offset:exposure_offset]+=.3
    lower[exposure_offset:]=np.tile([-.3,-.05],len(images)-1)
    upper[exposure_offset:]=np.tile([.3,.05],len(images)-1)
    pixels=queries[:,None,:]+OFFSETS
    selected=np.zeros((len(images)-1,len(points),len(OFFSETS)),bool)
    for camera,point,_,_ in train:
        if camera>0:selected[int(camera)-1,int(point)]=True
    if not selected.any():raise ValueError('no target training patches')
    row_indices=np.argwhere(selected)
    pattern=sparse.lil_matrix((len(row_indices),len(seed)),dtype=int)
    for row,(camera,point,_) in enumerate(row_indices):
        camera=int(camera)+1
        pattern[row,0]=1
        pattern[row,blocks[camera]:blocks[camera]+sizes[camera]]=1
        pattern[row,depth_offset+int(point)]=1
        pattern[row,exposure_offset+2*(camera-1):exposure_offset+2*camera]=1
    pattern=pattern.tocsr()

    def unpack(values):
        result=np.repeat(np.eye(4)[None],len(images),axis=0)
        for camera,index in blocks.items():
            result[camera,:3,:3]=cv2.Rodrigues(values[index:index+3])[0]
            if camera==baseline:
                theta,phi=values[index+3:index+5]
                result[camera,:3,3]=[np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)]
            else:result[camera,:3,3]=values[index+3:index+6]
        exposure=np.zeros((len(images),2));exposure[1:]=values[exposure_offset:].reshape(-1,2)
        return result,np.exp(values[depth_offset:exposure_offset]),exposure

    calls=0;invalid_trials=0

    def evaluate(values,allow_invalid=False):
        nonlocal calls,invalid_trials
        calls+=1
        pp,rho,exposure=unpack(values)
        try:
            rr,_=residual(images,pixels,rho,pp,exposure[:,0],exposure[:,1],values[0])
        except ValueError as error:
            domains=('all rays must','query outside complete bilinear interpolation domain','affine exposure outside')
            if not allow_invalid or not str(error).startswith(domains):raise
            invalid_trials+=1
            return np.full(int(selected.sum()),np.inf)
        return rr[selected]

    initial=evaluate(seed)
    omission=0.
    # ponytail:tiny fixed problem;one full column check instead of a Jacobian framework.
    for index in range(len(seed)):
        perturbed=seed.copy();perturbed[index]+=1e-6
        difference=(evaluate(perturbed)-initial)/1e-6
        excluded=pattern[:,index].toarray().ravel()==0
        if excluded.any():omission=max(omission,float(np.abs(difference[excluded]).max()))
    if omission>1e-10:raise ValueError('sparse Jacobian omitted a nonzero dependency')
    write(folder/'direct-before.json',{'baseline':baseline,'variables':len(seed),'residual_rows':len(initial),
          'sparse_omission_max':omission,'initial_rms':float(np.sqrt(np.mean(initial**2)))})
    fit=least_squares(lambda x:evaluate(x,True),seed,bounds=(lower,upper),jac_sparsity=pattern,
          loss='soft_l1',f_scale=.01,max_nfev=200,x_scale='jac',ftol=1e-8,xtol=1e-8,gtol=1e-8)
    final=evaluate(fit.x)
    poses,rho,exposure=unpack(fit.x);k=intrinsics(fit.x[0])
    points=np.c_[queries,np.ones(len(queries))]@np.linalg.inv(k).T/rho[:,None]
    held_uv,z=project(k,poses,points,held)
    np.savez_compressed(folder/'direct.npz',K=k,poses=poses,points=points,train=train,held=held,
          log_gain=exposure[:,0],bias=exposure[:,1],rho=rho,seed=seed,optimized=fit.x,
          lower=lower,upper=upper,held_errors=np.linalg.norm(held_uv-held[:,2:],axis=1),held_depth=z,
          selected=selected,initial_residual=initial,final_residual=final)
    write(folder/'direct.json',{'status':'TECHNICAL_CHECK_PASSED' if fit.success else 'REJECT',
          'scope':'numerical termination only;physical evaluator required','success':bool(fit.success),
          'nfev':fit.nfev,'calls':calls,'invalid_trials':invalid_trials,'message':fit.message,
          'initial_rms':float(np.sqrt(np.mean(initial**2))),'final_rms':float(np.sqrt(np.mean(final**2))),
          'focal_px':float(k[0,0]),'active_bounds':np.flatnonzero(fit.active_mask).tolist(),
          'worker_seconds':time.monotonic()-start_time})
