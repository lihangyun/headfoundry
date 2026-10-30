"""Extract expression directions from the already admitted FLAME Open source."""
import argparse
import json
import os
from pathlib import Path
import numpy as np
from prepare_flame_open import restricted_load
from headfoundry.flame import FlameIdentityModel
from headfoundry.flame_expression import CONVERSION_ID,FlameExpressionModel
from headfoundry.manifest import sha256_file


def convert(identity_lock, output):
    identity_lock,output=Path(identity_lock).resolve(),Path(output).resolve()
    if output.exists():raise FileExistsError('Preserve existing conversion')
    original=json.loads(identity_lock.read_text(encoding='utf8'))
    identity=FlameIdentityModel.from_asset_record(original,identity_lock.parent)
    source=restricted_load((identity_lock.parent/original['model_path']).read_bytes())
    metadata=source.get('supr_expression_metadata',{})
    if metadata.get('expr_components')!='last_100' or metadata.get('n_expr')!=100:
        raise ValueError('Source expression semantics not established')
    directions=np.asarray(source['shapedirs'],float)
    if directions.shape!=(*identity.template.shape,400):raise ValueError('Unexpected source basis')
    np.testing.assert_array_equal(directions[:,:,:300],identity.shape_directions)
    model=FlameExpressionModel(identity,directions[:,:,300:]);model.validate()
    beta=np.zeros(300);beta[0]=.1
    np.testing.assert_array_equal(model.vertices(beta,np.zeros(100)),identity.neutral_vertices(beta))
    output.mkdir(parents=True)
    asset=output/'expression-directions.npy';np.save(asset,model.expression_directions,allow_pickle=False)
    record=dict(conversion_id=CONVERSION_ID,expression_components='last_100',
        identity_lock=Path(os.path.relpath(identity_lock,output)).as_posix(),
        identity_lock_sha256=sha256_file(identity_lock),source_model_sha256=original['model_sha256'],
        path=asset.name,sha256=sha256_file(asset),source_metadata=metadata,
        attribution=original['attribution']+' Additional conversion: original last 100 expression directions; no articulation.',
        scope='Neutral-pose additive expression only; no jaw/neck articulation or safety certification')
    lock=output/'expression-lock.json';lock.write_text(json.dumps(record,indent=2),encoding='utf8')
    loaded=FlameExpressionModel.from_lock(lock)
    np.testing.assert_array_equal(loaded.expression_directions,source['shapedirs'][:,:,300:])
    np.testing.assert_array_equal(loaded.vertices(beta,np.zeros(100)),identity.neutral_vertices(beta))
    print(json.dumps(dict(status='TECHNICAL_CHECK_PASSED',vertices=len(identity.template),
        expression_dimensions=100,zero_expression_max_error=0.,lock=str(lock)),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('identity_lock',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();convert(args.identity_lock,args.output)
