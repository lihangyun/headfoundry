"""Plane sections retaining triangle barycentric support for surface constraints."""
import numpy as np


def section_segments(vertices, faces, axis, value):
    """Return triangle ids, endpoint barycentrics and endpoint coordinates.

    Coplanar faces are ambiguous and rejected. Point-only tangencies are omitted;
    on-plane edges may appear twice, once for each supporting triangle. Callers
    select/connect curves explicitly; this function assigns no anatomical labels.
    """
    v=np.asarray(vertices,float); f=np.asarray(faces)
    if (v.ndim!=2 or v.shape[1:]!=(3,) or not len(v)
            or f.ndim!=2 or f.shape[1:]!=(3,)
            or not np.issubdtype(f.dtype,np.integer)
            or np.any(f<0) or np.any(f>=len(v))
            or not np.isfinite(v).all() or not np.isscalar(value)
            or not np.isfinite(value) or isinstance(axis,(bool,np.bool_))
            or not isinstance(axis,(int,np.integer)) or axis not in (0,1,2)):
        raise ValueError('finite mesh, integer triangles and valid plane required')
    triangles=[]; endpoints=[]
    for index,face in enumerate(f):
        distance=v[face,axis]-value
        if np.all(distance==0): raise ValueError('coplanar face has ambiguous section')
        hits=[np.eye(3)[i] for i in np.flatnonzero(distance==0)]
        for i,j in [(0,1),(1,2),(2,0)]:
            if (distance[i]<0<distance[j]) or (distance[j]<0<distance[i]):
                t=distance[i]/(distance[i]-distance[j])
                weight=np.zeros(3); weight[i]=1-t; weight[j]=t; hits.append(weight)
        if len(hits)==2:
            triangles.append(index); endpoints.append(hits)
    triangles=np.asarray(triangles,dtype=int)
    weights=np.asarray(endpoints,float).reshape(-1,2,3)
    points=np.einsum('nij,njk->nik',weights,v[f[triangles]])
    return triangles,weights,points


def section_paths(points, tolerance=1e-9):
    """Order section endpoints into paths; retain (segment, endpoint) references.

    Coincident endpoints are merged within tolerance. Duplicate edges collapse;
    ambiguous branching is rejected. Closed paths repeat their first reference.
    This orders geometric sections, not anatomical curves.
    """
    p=np.asarray(points,float)
    if (p.ndim!=3 or p.shape[1:]!=(2,3) or not np.isfinite(p).all()
            or not np.isfinite(tolerance) or tolerance<=0):
        raise ValueError('finite segments and positive tolerance required')
    nodes=[]; references=[]; neighbors=[]
    for segment,line in enumerate(p):
        edge=[]
        for endpoint,point in enumerate(line):
            matches=[i for i,q in enumerate(nodes) if np.linalg.norm(point-q)<=tolerance]
            if len(matches)>1: raise ValueError('ambiguous endpoint merge')
            if matches: node=matches[0]
            else:
                node=len(nodes); nodes.append(point); references.append((segment,endpoint)); neighbors.append(set())
            edge.append(node)
        u,v=edge
        if u==v: raise ValueError('degenerate section segment')
        neighbors[u].add(v); neighbors[v].add(u)
    if any(len(adj)>2 for adj in neighbors): raise ValueError('branching section')
    unseen=set(range(len(nodes))); paths=[]
    while unseen:
        ends=[i for i in sorted(unseen) if len(neighbors[i])==1]
        start=ends[0] if ends else min(unseen)
        path=[start]; unseen.remove(start); previous=None; current=start
        while True:
            following=sorted(neighbors[current]-({previous} if previous is not None else set()))
            if not following: break
            nxt=following[0]
            if nxt==start:
                path.append(start); break
            if nxt not in unseen: raise ValueError('inconsistent section connectivity')
            path.append(nxt); unseen.remove(nxt); previous,current=current,nxt
        paths.append(np.asarray([references[i] for i in path],dtype=int))
    return paths
