import sys
from pathlib import Path
import contextlib
import io
import json
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from scan_surface_metric_0237 import apply_similarity, summary
import scan_surface_metric_0237 as metric
from headfoundry.manifest import sha256_file


class ScanSurfaceProtocolTests(unittest.TestCase):
    def test_single_positive_similarity_and_rejected_axis_stretch(self):
        points = np.array([[1., 2., 3.], [-1., 3., 2.]])
        matrix = np.array([[0., -2., 0., 4.], [2., 0., 0., -5.], [0., 0., 2., 6.], [0., 0., 0., 1.]])
        np.testing.assert_array_equal(apply_similarity(points, matrix), points @ matrix[:3, :3].T + matrix[:3, 3])
        for bad in (np.diag([1., 2., 1., 1.]), np.diag([-1., 1., 1., 1.]),
                np.diag([0., 0., 0., 1.]), np.diag([1., 1., 1., 2.])):
            with self.assertRaises(ValueError):
                apply_similarity(points, bad)

    def test_coverage_preserves_large_errors_and_refuses_nonfinite(self):
        distances = np.r_[np.zeros(90), np.full(10, 20.)]
        report = summary(distances)
        self.assertEqual(report['count'], 100)
        self.assertEqual(report['p95_mm'], 20.)
        self.assertEqual(report['fraction_within_2mm'], .9)
        for invalid in ([], [0., np.nan], [0., np.inf], [-.1]):
            with self.assertRaises(ValueError):
                summary(invalid)

    def test_bound_entrypoint_keeps_both_directions_and_rejects_reference_substitution(self):
        # Exact distance math is checked in Blender; here exercise the full
        # provenance/transform/report path without copying a real subject.
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / 'tmp') as directory:
            root = Path(directory)
            private = root / 'assets/private'
            pilot = private / 'real-capture-pilot-v1'
            reference = private / 'reference'
            pilot.mkdir(parents=True)
            reference.mkdir()
            source = private / 'fixture.stl'
            source.write_bytes(b'unit fixture only')
            manifest = {'inputs': [{'id': 'real-case-001-video', 'sha256': 'v' * 64},
                {'id': 'real-case-001-skin', 'path': str(source), 'sha256': sha256_file(source)}]}
            (pilot / 'manifest.json').write_text(json.dumps(manifest))
            (pilot / 'provenance-confirmation.json').write_text('{}')
            vertices = np.array([[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]])
            faces = np.array([[0, 1, 2]])
            geometry = private / 'candidate.npz'
            np.savez_compressed(geometry, vertices=vertices, faces=faces)
            np.savez_compressed(reference / 'regions.npz', sample_points_mm=vertices,
                sample_group=np.array([0, 1, 1]), face_region=np.array([1]))
            review = {'status': 'TECHNICAL_CHECK_PASSED', 'regions_sha256': sha256_file(reference / 'regions.npz')}
            (reference / 'review.json').write_text(json.dumps(review))
            contract = {'review_status': 'TECHNICAL_CHECK_PASSED', 'units': 'millimeter',
                'backend_versions': {'blender': 'unit_fixture', 'numpy': np.__version__},
                'sampler_sha256': sha256_file(Path(metric.__file__).with_name('scan_motion_truth_0230.py')),
                'review_sha256': sha256_file(reference / 'review.json'),
                'measurement_entrypoint_sha256': sha256_file(Path(metric.__file__)),
                'manifest_sha256': sha256_file(pilot / 'manifest.json'),
                'confirmation_sha256': sha256_file(pilot / 'provenance-confirmation.json'),
                'source_path': str(source), 'source_sha256': sha256_file(source),
                'regions_sha256': review['regions_sha256'], 'numerical_center_mm': [0, 0, 0],
                'sample_groups': ['full_source', 'nose'], 'face_regions': ['outside', 'nose'],
                'uncertainty': {'status': 'UNVERIFIED'}}
            contract_path = reference / 'contract.json'
            contract_path.write_text(json.dumps(contract))
            record = {'role': 'VIDEO_DERIVED_CANDIDATE', 'scan_geometry_used_for_inference': False,
                'units_after_transform': 'millimeter', 'reference_contract_sha256': sha256_file(contract_path),
                'video_sha256': 'v' * 64, 'alignment_basis': 'synthetic unit fixture, not real reconstruction',
                'geometry_path': geometry.name, 'geometry_sha256': sha256_file(geometry),
                'candidate_to_scan_4x4': [[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 3], [0, 0, 0, 1]]}
            record_path = private / 'candidate.json'
            record_path.write_text(json.dumps(record))
            output = private / 'out'
            with patch.object(metric, 'ROOT', root), patch.object(sys, 'argv', ['metric', '--', str(reference), str(record_path), str(output)]), \
                    patch('headfoundry.manifest.validate_input_assets', return_value=[]), \
                    patch.object(metric, 'read_binary_stl', return_value=(vertices, faces)), \
                    patch.object(metric, 'backend_versions', return_value=contract['backend_versions']), \
                    patch.object(metric, 'triangle_tree') as build, \
                    patch.object(metric, 'nearest_triangles', side_effect=[(np.array([1., 2., 20.]), np.zeros(3, int)),
                        (np.full(5000, 20.), np.zeros(5000, int))]) as nearest, contextlib.redirect_stdout(io.StringIO()):
                metric.main()
                np.testing.assert_array_equal(build.call_args_list[1].args[0], vertices * 2 + [0, 0, 3])
                report = json.loads((output / 'report.json').read_text())
                self.assertEqual(report['entire_candidate_to_full_source']['count'], 5000)
                self.assertEqual(report['entire_candidate_to_full_source']['p95_mm'], 20.)
                self.assertFalse(report['diagnostic_p95_2mm_targets']['nose'])
                self.assertEqual(report['head_acceptance'], 'UNVERIFIED')
                # Rejected provenance must fail before any new geometry query.
                nearest.reset_mock()
                for invalid_kind in ('scan_input', 'wrong_source', 'unreviewed'):
                    changed = dict(record)
                    altered = dict(contract)
                    if invalid_kind == 'scan_input':
                        changed['scan_geometry_used_for_inference'] = True
                    elif invalid_kind == 'wrong_source':
                        altered['source_path'] = str(private / 'unconsented.stl')
                    else:
                        altered['review_status'] = 'UNVERIFIED'
                    contract_path.write_text(json.dumps(altered))
                    changed['reference_contract_sha256'] = sha256_file(contract_path)
                    record_path.write_text(json.dumps(changed))
                    with patch.object(sys, 'argv', ['metric', '--', str(reference), str(record_path), str(private / invalid_kind)]):
                        with self.assertRaises(ValueError):
                            metric.main()
                nearest.assert_not_called()


if __name__ == '__main__':
    unittest.main()
