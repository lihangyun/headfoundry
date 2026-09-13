"""One Catmull-Clark refinement of an oriented manifold polygon cage.

Smooth cubic boundary rule; no creases, UVs, limit evaluation or collision repair.
This changes geometry, unlike interpolating shading normals.
"""
import numpy as np


def catmull_clark(vertices, polygons):
    v=np.asarray(vertices,float)
    if v.ndim!=2 or v.shape[1:]!=(3,) or not len(v) or not np.isfinite(v).all():
        raise ValueError('finite nonempty vertices required')
    faces=[];edges={};incident=[set() for _ in v];neighbors=[set() for _ in v]
    for index,polygon in enumerate(polygons):
        face=np.asarray(polygon)
        if (face.ndim!=1 or len(face)<3 or not np.issubdtype(face.dtype,np.integer)
                or np.any(face<0) or np.any(face>=len(v)) or len(set(face))!=len(face)):
            raise ValueError('simple integer polygon indices required')
        faces.append(face)
        for a,b in zip(face,np.roll(face,-1)):
            key=tuple(sorted((int(a),int(b))));item=edges.setdefault(key,[])
            if len(item)>=2 or (item and item[0][1]==int(a)):
                raise ValueError('nonmanifold or inconsistent edge orientation')
            item.append((index,int(a)))
            incident[a].add(index);neighbors[a].add(int(b));neighbors[b].add(int(a))
    if not faces or any(not x for x in incident):raise ValueError('empty mesh or isolated vertices')
    face_points=np.array([v[f].mean(0) for f in faces])
    keys=list(edges);edge_ids={key:len(v)+i for i,key in enumerate(keys)}
    edge_points=[];boundary=[[] for _ in v];links=[{} for _ in v]
    for (a,b),items in edges.items():
        if len(items)==1:
            edge_points.append((v[a]+v[b])/2);boundary[a].append(b);boundary[b].append(a)
        else:
            first,second=items[0][0],items[1][0]
            edge_points.append((v[a]+v[b]+face_points[first]+face_points[second])/4)
            for vertex in (a,b):
                links[vertex].setdefault(first,set()).add(second)
                links[vertex].setdefault(second,set()).add(first)
    updated=np.empty_like(v)
    for index in range(len(v)):
        # Reject disconnected face fans even when each edge alone is manifold.
        visited=set();pending=[next(iter(incident[index]))]
        while pending:
            face=pending.pop()
            if face not in visited:
                visited.add(face);pending.extend(links[index].get(face,set())-visited)
        if visited!=incident[index] or len(boundary[index]) not in (0,2):
            raise ValueError('nonmanifold vertex fan')
        if boundary[index]:
            updated[index]=.75*v[index]+.125*v[boundary[index]].sum(0)
        else:
            n=len(neighbors[index])
            if n!=len(incident[index]):raise ValueError('invalid interior fan')
            average_faces=face_points[sorted(incident[index])].mean(0)
            average_midpoints=(v[index]+v[sorted(neighbors[index])]).mean(0)/2
            updated[index]=(average_faces+2*average_midpoints+(n-3)*v[index])/n
    quads=[];offset=len(v)+len(edges)
    for index,face in enumerate(faces):
        for corner,a in enumerate(face):
            b=face[(corner+1)%len(face)];previous=face[corner-1]
            quads.append([int(a),edge_ids[tuple(sorted((int(a),int(b))))],offset+index,
                          edge_ids[tuple(sorted((int(previous),int(a))))]])
    return np.concatenate([updated,np.asarray(edge_points),face_points]),np.asarray(quads,int)
