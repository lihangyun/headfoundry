"""Verify pinned CC0 targets and map source IDs to the head crop."""
import argparse,json
from pathlib import Path
import numpy as np
from headfoundry.manifest import sha256_file
from headfoundry.target_asset import parse_target
from tools.prepare_makehuman_head import extract_head


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_assets',type=Path);parser.add_argument('targets',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--lock',type=Path,help='Explicit reviewed target asset lock; defaults to mouth volume assets')
    args=parser.parse_args();repo=Path(__file__).resolve().parents[1]
    lock=json.loads((args.lock or repo/'examples/makehuman-mouth-target-lock.json').read_text())
    base=json.loads((repo/'examples'/lock['base_asset_lock']).read_text())
    if lock['license_id']!='CC0-1.0' or base['license_id']!='CC0-1.0' or lock['revision']!=base['revision']:
        raise ValueError('incompatible asset license/revision')
    for directory,manifest in [(args.base_assets,base),(args.targets,lock)]:
        for name,digest in manifest['sha256'].items():
            if sha256_file(directory/name)!=digest:raise ValueError('asset/license digest mismatch: '+name)
    text=(args.base_assets/'base.obj').read_text();count=sum(line.startswith('v ') for line in text.splitlines())
    vertices,faces,used=extract_head(text);names=list(lock['sha256']);deltas=[]
    for name in names:
        delta=parse_target((args.targets/name).read_text(),count)
        deltas.append(delta[used]*[1,-1,-1])
    deltas=np.array(deltas);args.output.mkdir(exist_ok=False)
    np.savez(args.output/'targets.npz',vertices=vertices,faces=faces,source_vertex_indices=used,names=np.array(names),deltas=deltas)
    report={'status':'TECHNICAL_CHECK_PASSED','shape_quality':'UNVERIFIED','asset_lock':lock,'base_vertex_count':count,'head_vertex_count':len(vertices),'affected_head_vertices':np.any(deltas!=0,axis=2).sum(1).tolist(),'limitation':'Generic graphical targets, not fitted identity. Target ranges and combinations require visual verification.'}
    (args.output/'report.json').write_text(json.dumps(report,indent=2));print({key:report[key] for key in ['base_vertex_count','head_vertex_count','affected_head_vertices']})


if __name__=='__main__':main()
