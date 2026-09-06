import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('extract_xfeat',Path(__file__).resolve().parents[1]/'tools/extract_xfeat.py')
extract=importlib.util.module_from_spec(spec);spec.loader.exec_module(extract)


class XFeatLockTests(unittest.TestCase):
    def test_rights_and_exact_weight_bytes_before_inference(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'weights.pt').write_bytes(b'weights\r\n')
            (root/'source.py').write_bytes(b'# source\r\n')
            (root/'photo.bin').write_bytes(b'photo')
            lock=root/'lock.json'
            lock.write_text(json.dumps({'sha256':{'weights.pt':hashlib.sha256(b'weights\r\n').hexdigest(),
                                                  'source.py':hashlib.sha256(b'# source\n').hexdigest()}}))
            item=dict(id='view',path='photo.bin',sha256=hashlib.sha256(b'photo').hexdigest(),
                      allowed_uses=['local_head_reconstruction_validation'],source='fixture',license_id='fixture',
                      retention_until='test completion',deletion_process='temporary directory cleanup',
                      consent=dict(biometric_processing=True,subject_id='fixture',record_id='fixture',granted_at='2026-09-06'))
            manifest=root/'manifest.json'
            def save():manifest.write_text(json.dumps(dict(purpose='local_head_reconstruction_validation',inputs=[item])))
            save()
            with patch.object(extract,'LOCK_PATH',lock):
                self.assertEqual(len(extract.verify(manifest,root)[1]),1)
                item['consent']['biometric_processing']=False;save()
                with self.assertRaisesRegex(ValueError,'consent'):extract.verify(manifest,root)
                item['consent']['biometric_processing']=True;save()
                (root/'weights.pt').write_bytes(b'weights\n')
                with self.assertRaisesRegex(ValueError,'asset hash'):extract.verify(manifest,root)
