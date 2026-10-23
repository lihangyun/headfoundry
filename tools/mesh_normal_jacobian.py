"""Area-weighted vertex normals and full XYZ derivatives for tiny owned meshes."""
import numpy as np


def _skew(v):
    x,y,z=v
    return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])


def normals(vertices,faces,derivatives=True):
    if np.iscomplexobj(vertices):raise ValueError('real finite vertices required')
    vertices=np.asarray(vertices,float);faces=np.asarray(faces)
    if (vertices.ndim!=2 or vertices.shape[1]!=3 or len(vertices)<3 or not np.isfinite(vertices).all()
            or faces.ndim!=2 or faces.shape[1]!=3 or not len(faces)
            or not np.issubdtype(faces.dtype,np.integer) or (faces<0).any() or (faces>=len(vertices)).any()):
        raise ValueError('finite Nx3vertices and nonempty integral in-range Mx3faces required')
    faces=faces.astype(np.intp,copy=False)
    if (np.bincount(faces.ravel(),minlength=len(vertices))==0).any():raise ValueError('unused vertex')
    u=vertices[faces[:,1]]-vertices[faces[:,0]];v=vertices[faces[:,2]]-vertices[faces[:,0]]
    with np.errstate(over='ignore',invalid='ignore'):
        cross=np.cross(u,v);areas=np.linalg.norm(cross,axis=1)
    if not np.isfinite(areas).all() or (areas<=0).any():raise ValueError('nonfinite or degenerate face')
    summed=np.zeros_like(vertices)
    np.add.at(summed,faces.ravel(),np.repeat(cross,3,axis=0))
    lengths=np.linalg.norm(summed,axis=1)
    if not np.isfinite(lengths).all() or (lengths<=0).any():raise ValueError('cancelled/nonfinite vertex normal')
    unit=summed/lengths[:,None]
    if not derivatives:return unit,None
    # ponytail:dense XYZ Jacobian is for small information fixtures,not full heads.
    jac=np.zeros((len(vertices),3,3*len(vertices)))
    for ids,a,b in zip(faces,u,v):
        blocks=(_skew(b)-_skew(a),-_skew(b),_skew(a))
        for receiver in ids:
            for source,block in zip(ids,blocks):jac[receiver,:,3*source:3*source+3]+=block
    normalization=(np.eye(3)-unit[:,:,None]*unit[:,None,:])/lengths[:,None,None]
    jac=np.einsum('nij,njk->nik',normalization,jac)
    if not np.isfinite(jac).all():raise ValueError('nonfinite normal derivative')
    return unit,jac


def check():
    triangle=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
    one=np.array([[0,1,2]]);n,j=normals(triangle,one)
    expected=np.zeros((3,9));expected[0,[2,5]]=[1,-1];expected[1,[2,8]]=[1,-1]
    if not np.array_equal(n,np.tile([0.,0.,1.],(3,1))) or not np.array_equal(j,np.tile(expected,(3,1,1))):
        raise AssertionError('independent single-triangle normal/derivative fails')
    flipped,flipped_j=normals(triangle,one[:,::-1])
    if not np.array_equal(flipped,-n) or not np.array_equal(flipped_j,-j):raise AssertionError('face-winding sign lost')
    x,y=np.meshgrid(np.linspace(-.4,.4,3),np.linspace(-.5,.5,3))
    vertices=np.c_[x.ravel(),y.ravel(),(.2*x*x+.15*x*y+.1*y*y+.025*np.sin(4*x+y)).ravel()]
    faces=np.array([[a,b,c] for a in (0,1,3,4) for b,c in ((a+1,a+4),(a+4,a+3))])
    unit,jac=normals(vertices,faces);columns=jac.reshape(-1,vertices.size);relative=[]
    for step in (1e-6,5e-7):
        worst=0.
        for index,value in enumerate(vertices.ravel()):
            h=step*max(1.,abs(value));plus=vertices.copy();minus=vertices.copy()
            plus.flat[index]+=h;minus.flat[index]-=h
            numerical=((normals(plus,faces,False)[0]-normals(minus,faces,False)[0])/(2*h)).ravel()
            worst=max(worst,float(np.linalg.norm(numerical-columns[:,index])/max(1.,np.linalg.norm(columns[:,index]))))
        if worst>1e-6:raise AssertionError('complete normal-Jacobian central-difference control fails')
        relative.append(worst)
    moved,_=normals(vertices+[.3,-.2,.7],faces,False);scaled,scaled_j=normals(2*vertices,faces)
    translation=float(np.max(abs(columns@np.tile(np.eye(3),(len(vertices),1)))))
    scale=float(np.max(abs(columns@vertices.ravel())))
    if max(np.max(abs(moved-unit)),np.max(abs(scaled-unit)),np.max(abs(2*scaled_j-jac)),translation,scale)>1e-12:
        raise AssertionError('translation/positive-scale invariance fails')
    bad_vertices=triangle.copy();bad_vertices[0,0]=np.nan
    invalid=[(bad_vertices,one),(triangle,one.astype(float)),(triangle,np.array([[0,1,3]])),
        (triangle,np.array([[0,1,1]])),(np.r_[triangle,[[2.,2.,2.]]],one),
        (triangle,np.r_[one,one[:,::-1]])]
    for a,b in invalid:
        try:normals(a,b)
        except ValueError:pass
        else:raise AssertionError('invalid/unused/cancelled geometry accepted')
    return {'status':'TECHNICAL_CHECK_PASSED','central_steps':[1e-6,5e-7],
        'per_column_relative_max':relative,'translation_null_max':translation,'scale_null_max':scale,
        'invalid_cases_rejected':len(invalid),'scope':'owned normal/derivative math only,no camera/head information claim'}


if __name__=='__main__':
    import json
    print(json.dumps(check(),indent=2))
