"""Prepare only the pinned CC0 graphical head/neck template, without application code."""
import argparse
import json
from pathlib import Path
import numpy as np
from headfoundry.manifest import sha256_file


def extract_head(text, minimum_y=5.5, include_eye_helpers=False):
    vertices=[];faces=[];group=None
    groups={'body','helper-l-eye','helper-r-eye'} if include_eye_helpers else {'body'}
    seen=set()
    for line in text.splitlines():
        a=line.split()
        if not a:continue
        if a[0]=='v':vertices.append([float(x) for x in a[1:4]])
        elif a[0]=='g':group=a[1]
        elif a[0]=='f' and group in groups:
            seen.add(group)
            indices=[int(x.split('/')[0])-1 for x in a[1:]]
            if len(indices) not in (3,4):raise ValueError('only triangle/quad selected faces supported')
            faces.extend([[indices[0],indices[i],indices[i+1]] for i in range(1,len(indices)-1)])
    if not groups.issubset(seen):raise ValueError('required body/eye groups missing')
    v=np.asarray(vertices,float);f=np.asarray(faces,int)
    if not len(f) or not np.isfinite(v).all() or np.any(f<0) or np.any(f>=len(v)):raise ValueError('invalid body mesh')
    f=f[(v[f,1]>=minimum_y).all(1)]
    if not len(f):raise ValueError('empty head crop')
    used,inverse=np.unique(f,return_inverse=True)
    # MakeHuman y-up / face +z to our y-down / face -z. Rigid, not mirrored.
    return v[used]*[1,-1,-1],inverse.reshape(-1,3),used


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--include-eye-helpers',action='store_true',help='Include generic CC0 eye helper meshes, not subject-specific eyeballs')
    args=parser.parse_args()
    lock=json.loads((Path(__file__).resolve().parents[1]/'examples/makehuman-base-asset-lock.json').read_text())
    if lock['license_id']!='CC0-1.0':raise ValueError('unexpected asset license')
    for name,digest in lock['sha256'].items():
        if sha256_file(args.assets/name)!=digest:raise ValueError('asset/license hash mismatch: '+name)
    v,f,used=extract_head((args.assets/'base.obj').read_text(),include_eye_helpers=args.include_eye_helpers)
    args.output.mkdir(exist_ok=False)
    with (args.output/'template.obj').open('x') as stream:
        stream.write('# CC0 MakeHuman head crop; UNFITTED TEMPLATE, NOT user reconstruction\n')
        for vertex in v:stream.write('v '+' '.join(map(str,vertex))+'\n')
        for face in f:stream.write('f '+' '.join(str(int(x)+1) for x in face)+'\n')
    report=dict(status='UNVERIFIED',asset=lock,vertices=len(v),triangles=len(f),
                minimum_source_y=5.5,source_vertex_indices=used.tolist(),
                include_eye_helpers=args.include_eye_helpers,
                scope='Unfitted generic head/neck template. Open neck crop; no separate teeth. '+
                      ('Includes generic eye helpers, not subject-specific eyes or iris texture.' if args.include_eye_helpers else 'No eye helpers imported.'))
    (args.output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print({'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})


if __name__=='__main__':main()
