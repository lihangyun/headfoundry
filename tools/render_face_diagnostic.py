"""Render an existing OBJ with a supplied camera, without accepting its quality."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from headfoundry.raster import render


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh',type=Path)
    parser.add_argument('cameras',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--view',type=int,default=0)
    parser.add_argument('--size',type=int,nargs=2,default=[1254,1254],metavar=('WIDTH','HEIGHT'))
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError('choose a new output path')
    vertices=[];triangles=[]
    for line in args.mesh.read_text(encoding='utf-8').splitlines():
        parts=line.split()
        if not parts:continue
        if parts[0]=='v':vertices.append([float(x) for x in parts[1:4]])
        elif parts[0]=='f':
            if len(parts)!=4:raise ValueError('only triangulated meshes supported')
            indices=[int(x.split('/')[0]) for x in parts[1:]]
            if min(indices)<=0:raise ValueError('positive OBJ indices required')
            triangles.append([x-1 for x in indices])
    cameras=json.loads(args.cameras.read_text(encoding='utf-8'))
    rgb,_,ids=render(np.array(vertices),np.array(triangles),cameras['extrinsics'][args.view],
                     cameras['intrinsics'][args.view],args.size)
    rgba=np.dstack([rgb,(ids>=0).astype(np.uint8)*255])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(rgba).save(args.output)
    print(json.dumps({'status':'UNVERIFIED','camera_status':cameras.get('status','UNVERIFIED'),
                      'rendered_pixels':int((ids>=0).sum())}))


if __name__=='__main__':main()
