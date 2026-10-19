"""One fixed-objective hard-feasibility oracle; no video inference or refit ICP."""
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.optimize import LinearConstraint, minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from headfoundry.flame import FlameIdentityModel
from headfoundry.manifest import sha256_file, validate_input_assets
from scan_surface_metric_0237 import apply_similarity
from anatomical_capacity_0239 import mesh_guard
from mesh_feasibility_0240 import constraints, violated_faces

PILOT = ROOT / 'assets/private/real-capture-pilot-v1'
PARENT = PILOT / 'anatomical-capacity-0239-numerical-replay'
REFERENCE = PILOT / 'fixed-scan-reference-0237-interface-replay'
LOCK = ROOT / 'assets/private/FLAME-2023-Open/converted-v1/flame-2023-open-lock.json'
OUT = PILOT / 'hard-mesh-feasibility-0240'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve first hard-mesh feasibility experiment')
    started = time.perf_counter()
    manifest = json.loads((PILOT / 'manifest.json').read_text(encoding='utf-8'))
    parent = json.loads((PARENT / 'controls.json').read_text(encoding='utf-8'))
    reference = json.loads((REFERENCE / 'contract.json').read_text(encoding='utf-8'))
    if (validate_input_assets(manifest, PILOT) or manifest['purpose'] != 'local_head_reconstruction_validation'
            or reference['manifest_sha256'] != sha256_file(PILOT / 'manifest.json')
            or reference['confirmation_sha256'] != sha256_file(PILOT / 'provenance-confirmation.json')
            or parent['reference_contract_sha256'] != sha256_file(REFERENCE / 'contract.json')
            or parent['asset_lock_sha256'] != sha256_file(LOCK)):
        raise ValueError('Frozen case001 source rights/reference/model changed')
    model = FlameIdentityModel.from_asset_record(json.loads(LOCK.read_text(encoding='utf-8')), LOCK.parent)
    packet = np.load(PARENT / 'fit-step-04.npz', allow_pickle=False)
    replay = np.load(PARENT / 'replay.npz', allow_pickle=False)
    damage = np.load(PARENT / 'damage-localization.npz', allow_pickle=False)
    h, g = packet['hessian'], packet['linear']
    transform, base, faces = replay['frozen_model_to_scan'], replay['prior'], replay['faces']
    if not np.array_equal(faces, model.faces) or abs(apply_similarity(model.template, transform) - base).max() > 1e-9:
        raise ValueError('Original basis,neutral geometry,pose or topology changed')
    directions = np.einsum('ij,vjk->vik', transform[:3, :3], model.shape_directions)
    active = damage['bad_face_ids'].copy()
    if len(active) != 39 or not np.array_equal(np.unique(active), active):
        raise ValueError('Frozen whole-mesh failure identities changed')
    scale = float(max(1., abs(g).max()))
    p = np.linalg.solve(np.linalg.cholesky(h).T, np.eye(300)) * np.sqrt(scale)
    if not np.allclose(p.T @ h @ p / scale, np.eye(300), atol=1e-8, rtol=0):
        raise ValueError('Exact fixed-objective whitening failed')
    linear = p.T @ g / scale
    OUT.mkdir()
    prereg = ROOT / 'docs/experiment-0240-hard-mesh-feasibility.md'
    (OUT / 'executed-preregistration.md').write_bytes(prereg.read_bytes())
    controls = {'role': 'SCAN_ORACLE_NOT_VIDEO_RECONSTRUCTION',
        'parent_controls_sha256': sha256_file(PARENT / 'controls.json'),
        'objective_sha256': sha256_file(PARENT / 'fit-step-04.npz'),
        'replay_sha256': sha256_file(PARENT / 'replay.npz'),
        'reference_contract_sha256': sha256_file(REFERENCE / 'contract.json'),
        'asset_lock_sha256': sha256_file(LOCK), 'producer_sha256': sha256_file(Path(__file__)),
        'constraint_helper_sha256': sha256_file(ROOT / 'tools/mesh_feasibility_0240.py'),
        'preregistration_sha256': sha256_file(prereg), 'objective_positive_scale': scale,
        'coefficient_box_margin': 1e-8, 'constraint_arithmetic_tolerance': 1e-7,
        'max_rounds': 5, 'max_iterations_per_round': 200, 'ftol': 1e-9,
        'runtime_seconds': 180, 'source_used_for_fit': True, 'video_or_case002_used': False}
    (OUT / 'controls.json').write_text(json.dumps(controls, indent=2), encoding='utf-8')
    np.savez_compressed(OUT / 'fixed-objective.npz', hessian=h, linear=g,
        whitening=p, normalized_linear=linear, prior=base, directions=directions, faces=faces, frozen_model_to_scan=transform)
    history, success, coefficients = [], False, np.zeros(300)
    for round_index in range(5):
        triangles, fields = base[faces[active]], directions[faces[active]]
        cache = {'z': None}

        def check_time():
            if time.perf_counter() - started > 180:
                raise TimeoutError('Single hard-feasibility process budget exhausted')

        def physical(z):
            check_time()
            if cache['z'] is None or not np.array_equal(cache['z'], z):
                c, j = constraints(p @ z, triangles, fields)
                cache.update(z=z.copy(), value=c, jacobian=j @ p)
            return cache['value'], cache['jacobian']

        iterations = []

        def callback(z):
            check_time()
            c, _ = physical(z)
            record = {'iteration': len(iterations) + 1, 'normalized_objective': float(.5 * z @ z - linear @ z),
                'minimum_active_constraint': float(c.min())}
            iterations.append(record)
            if len(iterations) % 20 == 0:
                print(json.dumps({'round': round_index, **record}), flush=True)

        result = minimize(lambda z: .5 * z @ z - linear @ z, np.zeros(300),
            jac=lambda z: z - linear, method='SLSQP',
            constraints=[LinearConstraint(p, -3 + 1e-8, 3 - 1e-8),
                {'type': 'ineq', 'fun': lambda z: physical(z)[0], 'jac': lambda z: physical(z)[1]}],
            callback=callback, options={'maxiter': 200, 'ftol': 1e-9, 'disp': False})
        coefficients = p @ result.x
        c, j = physical(result.x)
        vertices = base + np.einsum('vck,k->vc', directions, coefficients)
        guard = mesh_guard(vertices, base, faces)
        bad = violated_faces(vertices, base, faces)
        bound_ok = bool((abs(coefficients) <= 3).all())
        record = {'round': round_index, 'optimizer_success': bool(result.success),
            'message': str(result.message), 'iterations': int(result.nit), 'constrained_faces': len(active),
            'minimum_active_constraint': float(c.min()), 'all_face_violations': len(bad),
            'coefficient_bound_passed': bound_ok, 'mesh_guard': guard, 'iteration_trace': iterations}
        history.append(record)
        np.savez_compressed(OUT / f'round-{round_index:02d}.npz', coefficients=coefficients,
            whitened=result.x, constrained_faces=active, all_violating_faces=bad,
            final_constraint_values=c, final_constraint_jacobian=j,
            normalized_objective_gradient=result.x - linear,
            approximate_QP_multipliers=np.asarray(getattr(result, 'multipliers', [])))
        print(json.dumps({k: v for k, v in record.items() if k != 'iteration_trace'}), flush=True)
        if not result.success or c.min() < -1e-7 or not bound_ok:
            break
        if not len(bad) and guard['passed']:
            success = True
            break
        updated = np.union1d(active, bad)
        if len(updated) == len(active):
            break
        active = updated
    report = {'execution_status': 'TECHNICAL_CHECK_PASSED',
        'mesh_feasibility_status': 'TECHNICAL_CHECK_PASSED' if success else 'REJECT',
        'head_acceptance': 'UNVERIFIED', 'role': controls['role'], 'history': history,
        'elapsed_seconds': time.perf_counter() - started,
        'limits': 'One fixed scan-derived quadratic, local constrained optimum only; not scan-free video inference or complete head acceptance.'}
    if success:
        native_replay = apply_similarity(model.neutral_vertices(coefficients), transform)
        if abs(native_replay - vertices).max() > 1e-9:
            raise ValueError('Constrained identity/pose replay failed')
        np.savez_compressed(OUT / 'feasible-SCAN-ORACLE-NOT-VIDEO.npz', vertices=vertices, faces=faces,
            coefficients=coefficients, prior=base, frozen_model_to_scan=transform)
    (OUT / 'optimization-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'mesh_feasibility_status': report['mesh_feasibility_status'],
        'elapsed_seconds': report['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'failure.json').exists():
            (OUT / 'failure.json').write_text(json.dumps({'status': 'REJECT', 'error': str(error)}, indent=2), encoding='utf-8')
        raise
