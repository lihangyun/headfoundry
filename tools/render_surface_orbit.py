"""Offline common-frame orbit of observed OBJ surfaces. No alignment or fusion."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from headfoundry.raster import render
from headfoundry.manifest import sha256_file
from headfoundry.depth_surface import write_observed_obj


def largest_component(vertices, faces):
    """Keep largest vertex-connected surface; do not alter retained positions."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    edges=np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]])
    graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),
                     shape=(len(vertices),len(vertices)))
    _,labels=connected_components(graph,directed=False)
    label=np.bincount(labels).argmax()
    retained=faces[(labels[faces]==label).all(axis=1)]
    used,inverse=np.unique(retained,return_inverse=True)
    return vertices[used],inverse.reshape(-1,3)


def read_surface(path):
    vertices, faces = [], []
    for line in path.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if not parts or parts[0] == '#':
            continue
        if parts[0] == 'v' and len(parts) == 4:
            vertices.append([float(x) for x in parts[1:]])
        elif parts[0] == 'f' and len(parts) == 4:
            faces.append([int(x)-1 for x in parts[1:]])
        else:
            raise ValueError('only plain triangular observed OBJ supported')
    v, f = np.asarray(vertices, float), np.asarray(faces, int)
    if (v.ndim != 2 or v.shape[1:] != (3,) or not np.isfinite(v).all()
            or f.ndim != 2 or f.shape[1:] != (3,)
            or np.any(f < 0) or np.any(f >= len(v))):
        raise ValueError('invalid or empty mesh')
    return v, f


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('meshes', type=Path, nargs='+')
    parser.add_argument('--largest-component',action='store_true')
    args = parser.parse_args()
    meshes = [read_surface(p) for p in args.meshes]
    original_counts=[len(v) for v,f in meshes]
    if args.largest_component:
        meshes=[largest_component(v,f) for v,f in meshes]
    vertices = np.concatenate([v for v, f in meshes])
    offsets = np.cumsum([0]+[len(v) for v, f in meshes])
    faces = np.concatenate([f+offsets[i] for i, (v, f) in enumerate(meshes)])
    center = (vertices.max(0)+vertices.min(0))/2
    # One shared display transform preserves relative scale and misalignment.
    radius = np.linalg.norm(vertices-center, axis=1).max()
    if radius <= 1e-12:
        raise ValueError('mesh has no spatial extent')
    args.output.mkdir(exist_ok=False)
    write_observed_obj(args.output/'surface-union.obj',vertices,faces)
    vertices = (vertices-center)/radius
    frames=[]
    angles=list(range(-90, 91, 30))
    for angle in angles:
        theta=np.deg2rad(angle); c,s=np.cos(theta),np.sin(theta)
        rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        e=np.column_stack([rotation,[0,0,3]])
        k=np.array([[330,0,128],[0,330,128],[0,0,1]])
        rgb,_,_=render(vertices,faces,e,k,(256,256))
        frame=Image.fromarray(rgb)
        ImageDraw.Draw(frame).text((6,6),f'UNVERIFIED / orbit {angle:+d}',fill='white')
        frames.append(frame)
    sheet=Image.new('RGB',(256*len(frames),256))
    for i,frame in enumerate(frames):sheet.paste(frame,(256*i,0))
    sheet.save(args.output/'orbit.png')
    sequence=frames+frames[-2:0:-1]
    sequence[0].save(args.output/'orbit.gif',save_all=True,append_images=sequence[1:],duration=450,loop=0)
    record={'status':'UNVERIFIED','operation':'unaltered common-frame surface union; NOT fusion',
            'largest_component_only':args.largest_component,
            'original_vertex_counts':original_counts,
            'retained_vertex_counts':[len(v) for v,f in meshes],
            'sources':[{'name':p.name,'sha256':sha256_file(p)} for p in args.meshes],
            'vertices':len(vertices),'triangles':len(faces),'angles_degrees':angles,
            'display_center':center.tolist(),'display_radius':float(radius),
            'limitations':'Original DA3 cameras fail validation. Overlapping sheets retained. Unseen back is absent. No geometry improvement claimed.'}
    (args.output/'report.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':main()
