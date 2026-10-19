import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tools')]
import fit_bounded_profile_0246 as bounded


class BoundedProfileAcceptanceTests(unittest.TestCase):
    def test_missing_required_view_stays_rejected_even_if_available_projection_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output/'fit').mkdir()
            report = output/'fit/optimization-report.json'
            report.write_text(json.dumps({'head_acceptance': 'UNVERIFIED',
                'profile_projection_status': 'TECHNICAL_CHECK_PASSED', 'limits': 'Available three views only.'}), encoding='utf-8')
            with patch.object(bounded, 'OUT', output), patch.object(bounded.shared, 'fit'), \
                    patch.object(bounded.shared, 'OUT'), patch.object(bounded.shared, 'ORDINALS'):
                bounded.fit()
            result = json.loads(report.read_text(encoding='utf-8'))
            self.assertEqual(result['head_acceptance'], 'REJECT')
            self.assertEqual(result['required_view347_status'], 'REJECT')
            self.assertEqual(result['overall_image_validation_status'], 'REJECT')
