import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from headfoundry.da3 import depth_to_world, original_intrinsics

spec=importlib.util.spec_from_file_location('run_da3',Path(__file__).resolve().parents[1]/'tools/run_da3.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


class DA3Tests(unittest.TestCase):
    def test_depth_roundtrip_with_camera_translation_rotation_and_resize(self):
        angle=.4;c,s=np.cos(angle),np.sin(angle)
        r=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        e=np.array([np.c_[r,[.2,-.1,.3]],np.c_[np.eye(3),[-.3,.1,0]]])
        k=np.array([[[100.,0,1],[0,120,1],[0,0,1]]]*2)
        depth=np.arange(12,dtype=float).reshape(2,2,3)/10+2
        world=depth_to_world(depth,e,k)
        camera=np.einsum('vij,vhwj->vhwi',e[:,:,:3],world)+e[:,None,None,:,3]
        np.testing.assert_allclose(camera[...,2],depth)
        pixels=np.einsum('vij,vhwj->vhwi',k,camera)
        y,x=np.mgrid[:2,:3];expected=np.stack([x,y],axis=-1)
        np.testing.assert_allclose(pixels[...,:2]/pixels[...,2:],np.broadcast_to(expected,(2,2,3,2)),atol=1e-12)
        scaled=original_intrinsics(k,[2,3],[[20,30],[4,9]])
        np.testing.assert_allclose(scaled[0],np.diag([10,10,1])@k[0])
        np.testing.assert_allclose(scaled[1],np.diag([3,2,1])@k[1])
        with self.assertRaises(ValueError):depth_to_world(-depth,e,k)
        with self.assertRaises(ValueError):depth_to_world(depth,e[:,:2],k)
        bad=e.copy();bad[:,0,:3]*=-1
        with self.assertRaises(ValueError):depth_to_world(depth,bad,k)
        with self.assertRaises(ValueError):original_intrinsics(k,[0,3],[[2,3],[2,3]])

    def test_asset_lock_and_consent_fail_before_model_imports(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'src/depth_anything_3';source.mkdir(parents=True)
            (source/'core.py').write_bytes(b'# fixture\r\n')
            (root/'LICENSE').write_bytes(b'license');(root/'model.safetensors').write_bytes(b'weights')
            manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(purpose='local_head_reconstruction_validation')))
            lock=dict(asset_id='depth-anything/DA3-BASE',license_id='Apache-2.0',runtime={},
                      source_tree_sha256=runner.source_digest(root),
                      source_license_sha256_lf=hashlib.sha256(b'license').hexdigest(),
                      model_sha256={'model.safetensors':hashlib.sha256(b'weights').hexdigest()})
            path=root/'lock.json';path.write_text(json.dumps(lock))
            with patch.object(runner,'LOCK_PATH',path):
                with self.assertRaisesRegex(ValueError,'input rights'):runner.verify(manifest,root,root)
                with patch.object(runner,'validate_input_assets',return_value=[]),patch.object(runner,'validate_multiview',return_value={'status':'TECHNICAL_CHECK_PASSED'}):
                    self.assertEqual(runner.verify(manifest,root,root)[1]['asset_id'],'depth-anything/DA3-BASE')
                    (source/'core.py').write_bytes(b'# altered')
                    with self.assertRaisesRegex(ValueError,'source/license hash'):runner.verify(manifest,root,root)
                    (root/'model.safetensors').write_bytes(b'different weights')
                    with self.assertRaisesRegex(ValueError,'model asset hash'):runner.verify(manifest,root,root)
                    lock['asset_id']='depth-anything/DA3-LARGE';path.write_text(json.dumps(lock))
                    with self.assertRaisesRegex(ValueError,'only the reviewed'):runner.verify(manifest,root,root)
