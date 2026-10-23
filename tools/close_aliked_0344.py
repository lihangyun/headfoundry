"""Explicit ALIKED closeout stages; no action at import and no model execution.

Run prepare, review its private plan/archive, then execute. Retire the seven
tracked candidate tools separately with apply_patch before verify. This is not
a full binary backup: public weights/runtime need a justified fresh download.
"""
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'assets/private'
CLOSED = PRIVATE / 'closed-experiments/0344-aliked'
BASIS = PRIVATE / 'closed-experiments/0337-detector-free/plan.json'
FIXTURE = PRIVATE / 'aliked-physical-0343'
REPLAY = ROOT / 'tools/replay_owned_sparse_fixture.py'
PYTHON = ROOT / '.venv/Scripts/python.exe'
EXECUTED_REF = '53804e2'
SCOPES = tuple(PRIVATE / name for name in (
    'aliked-preflight-0339', 'aliked-assets-0340', 'aliked-matcher-0341',
    'aliked-runtime-0342', 'aliked-real-0344'))
STEMS = (
    'acquire_aliked_matcher_0341', 'prepare_aliked_runtime_0342',
    'aliked_native_0342', 'check_sparse_match_software',
    'score_aliked_pair_0343', 'aliked_real_0344', 'sparse_camera_0344')
SOURCES = tuple(ROOT / f'tools/{name}.py' for name in STEMS)
CACHES = tuple(ROOT / f'tools/__pycache__/{name}.cpython-312.pyc' for name in STEMS)
FIXTURE_NAMES = {
    'domain-worker.json', 'domain.json', 'domain.log', 'domain.npz', 'oracle.json',
    'result.json', 'score-worker.json', 'score.log', 'scores.npz',
    'suite-worker.json', 'suite.log', 'verification.json', 'verify.py'}
WORKERS = {
    'aliked-matcher-0341': ('worker.json',),
    'aliked-runtime-0342': tuple(name + '-worker.json' for name in
        ('setup', 'controls', 'small', 'native', 'suite')),
    'aliked-physical-0343': tuple(name + '-worker.json' for name in ('domain', 'score', 'suite')),
    'aliked-real-0344': tuple(name + '-worker.json' for name in
        ('prepare', 'infer', 'infer-import-repair', 'assemble'))}


def owned(path, missing=False):
    """Check lexical and resolved ownership and every existing ancestor."""
    path = Path(os.path.abspath(path))
    if ROOT != Path('C:/workspace/headfoundry') or not path.is_relative_to(ROOT):
        raise ValueError('not the explicit HeadFoundry workspace: ' + str(path))
    current = path
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            if not missing:
                raise
        else:
            if info.st_file_attributes & 0x400:
                raise ValueError('reparse point refused: ' + str(current))
        if current == ROOT:
            break
        current = current.parent
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('resolved outside workspace: ' + str(path))
    return path


def regular(path):
    path = owned(path)
    info = path.stat()
    if not path.is_file() or info.st_nlink != 1:
        raise ValueError('nonregular or hardlinked candidate file: ' + str(path))
    return path


def files(root):
    pending, found = [owned(root)], []
    while pending:
        path = owned(pending.pop())
        if path.is_dir():
            pending.extend(path.iterdir())
        else:
            found.append(regular(path))
    return sorted(found)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def write_new(name, value):
    path = owned(CLOSED / name, missing=True)
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def identity(path):
    path = regular(path)
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def verify_hashes(rows):
    for row in rows:
        path = Path(row['path'])
        # The inherited list includes external authorized originals: hash only,
        # never enumerate, open for modeling, or use them as deletion targets.
        if path.is_relative_to(ROOT):
            owned(path)
        if not path.is_file() or sha(path) != row['sha256']:
            raise ValueError('protected/recorded identity changed: ' + str(path))


def protected():
    base = read(BASIS)['protected']
    if len(base) != 96:
        raise ValueError('expected exact inherited 96-file protection basis')
    verify_hashes(base)
    fixture_files = files(FIXTURE)
    if {path.name for path in fixture_files} != FIXTURE_NAMES:
        raise ValueError('successful 0343 fixture is not the immutable 13-file set')
    bound = read(FIXTURE / 'verification.json')['files_sha256']
    if set(bound) != FIXTURE_NAMES - {'verification.json'}:
        raise ValueError('incomplete successful-fixture identities')
    verify_hashes([{'path': str(FIXTURE / name), 'sha256': digest} for name, digest in bound.items()])
    extra = [PRIVATE / 'pairwise-physical-0336' / name for name in
             ('verify.py', 'retained-fixture-verification.json')]
    rows = base + [identity(path) for path in extra + fixture_files + [REPLAY]]
    unique = {}
    for row in rows:
        key = str(Path(row['path']))
        if key in unique and unique[key]['sha256'] != row['sha256']:
            raise ValueError('conflicting protected identity: ' + key)
        unique[key] = row
    if len(unique) != 112:
        raise ValueError('expected 96 + 2 + 13 + shared replay protected files')
    return list(unique.values())


def inventory():
    result = [identity(path) for root in SCOPES for path in files(root)]
    cache_dir = ROOT / 'tools/__pycache__'
    if cache_dir.exists():
        for path in owned(cache_dir).iterdir():
            if any(path.name.startswith(stem + '.') for stem in STEMS) and path.suffix == '.pyc':
                if path not in CACHES:
                    raise ValueError('unconfirmed candidate bytecode variant: ' + str(path))
                result.append(identity(path))
    return sorted(result, key=lambda row: row['path'])


def terminal():
    """Fail closed for original live jobs; inspect PID creation, never kill."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_ulonglong)] * 4
    kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]

    def image_name(pid):
        class Entry(ctypes.Structure):
            _fields_ = [('size', ctypes.c_ulong), ('usage', ctypes.c_ulong), ('pid', ctypes.c_ulong),
                ('heap', ctypes.c_size_t), ('module', ctypes.c_ulong), ('threads', ctypes.c_ulong),
                ('parent', ctypes.c_ulong), ('priority', ctypes.c_long), ('flags', ctypes.c_ulong),
                ('name', ctypes.c_wchar * 260)]
        kernel.CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong, ctypes.c_ulong]
        kernel.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        kernel.Process32FirstW.argtypes = kernel.Process32NextW.argtypes = [ctypes.c_void_p, ctypes.POINTER(Entry)]
        snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
        if snapshot == ctypes.c_void_p(-1).value:
            raise OSError('process snapshot unavailable')
        entry = Entry()
        entry.size = ctypes.sizeof(entry)
        try:
            ok = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
            if not ok:
                raise OSError('process inventory unavailable')
            while ok:
                if entry.pid == pid:
                    return str(entry.name)
                ok = kernel.Process32NextW(snapshot, ctypes.byref(entry))
            return None
        finally:
            kernel.CloseHandle(snapshot)

    reports = []
    for directory, names in WORKERS.items():
        folder = PRIVATE / directory
        actual = {path.name for path in owned(folder).iterdir()
                  if path.name.endswith('-worker.json') or path.name == 'worker.json'}
        if actual != set(names):
            raise ValueError('unclassified or missing worker receipts: ' + directory)
        for name in names:
            path = regular(folder / name)
            record = read(path)
            if record['status'] == 'RUNNING' or 'exit' not in record:
                raise ValueError('worker receipt is not terminal: ' + str(path))
            start, duration = record['started_utc'], record['seconds']
            if not all(math.isfinite(v) for v in (start, duration)) or duration < 0:
                raise ValueError('invalid recorded worker timing')
            pids = set(map(int, record['observed_process_peaks'])) | {int(record['pid'])}
            for pid in sorted(pids):
                handle = kernel.OpenProcess(0x1000, False, pid)
                row = {'receipt': str(path), 'pid': pid}
                if handle:
                    try:
                        values = [ctypes.c_ulonglong() for _ in range(4)]
                        code = ctypes.c_ulong()
                        if not kernel.GetProcessTimes(handle, *[ctypes.byref(v) for v in values]) or not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                            raise OSError('process identity unavailable')
                        created = values[0].value / 1e7 - 11644473600
                        original = start - 2 <= created <= start + duration + 2
                        if code.value == 259 and original:
                            raise ValueError('original candidate worker still running')
                        row.update(created_utc=created, same_recorded_job=original,
                                   exit_code=code.value, state='terminated or unrelated reused PID; untouched')
                    finally:
                        kernel.CloseHandle(handle)
                else:
                    error = ctypes.get_last_error()
                    if error == 87:
                        row['state'] = 'absent'
                    elif error == 5:
                        image = image_name(pid)
                        if image is not None and image.lower() in ('python.exe', 'pythonw.exe'):
                            raise OSError('Python PID identity unavailable: ' + str(pid))
                        row.update(state='absent or confirmed unrelated reused executable; untouched', image=image)
                    else:
                        raise OSError(f'PID liveness unavailable: {pid}, winerror={error}')
                reports.append(row)
    return reports


def git(*args, binary=False):
    result = subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, timeout=30)
    return result.stdout if binary else result.stdout.decode('utf8').strip()


def sources():
    head = git('rev-parse', 'HEAD')
    executed = git('rev-parse', EXECUTED_REF + '^{commit}')
    rows = []
    for path in (*SOURCES, Path(__file__), REPLAY):
        row = identity(path)
        relative = path.relative_to(ROOT).as_posix()
        if hashlib.sha256(git('show', head + ':' + relative, binary=True)).hexdigest() != row['sha256']:
            raise ValueError('source must be committed and identical to HEAD: ' + relative)
        row['git_blob'] = git('rev-parse', head + ':' + relative)
        rows.append(row)
    return {'archival_source_ref': head, 'actual_neural_source_ref': executed, 'files': rows}


def reject_gate():
    gate = read(SCOPES[-1] / 'coverage.json')
    if not (gate['status'] == 'REJECT' and gate['complete_patch_supported'] == 22
            and gate['minimum'] == 48 and gate['physical_material_precision'] == 'UNVERIFIED'):
        raise ValueError('expected recorded real-video support failure, not a new experiment')
    if sha(SCOPES[-1] / 'raw-observations.npz') != gate['raw_sha256']:
        raise ValueError('raw failed observation identity changed')
    return gate


def archive_selection():
    selected = []
    for index, root in enumerate(SCOPES):
        for path in files(root):
            relative = path.relative_to(root)
            top = len(relative.parts) == 1
            if index == 0:
                keep = True
            elif index in (1, 2):
                keep = top and path.suffix in ('.json', '.log', '.py')
            elif index == 3:
                keep = (relative.parts[0] in ('source', 'notices', 'metadata') or
                        top and (path.suffix in ('.json', '.log', '.py', '.txt') or path.name.endswith('LICENSE')))
            else:
                keep = top and (path.suffix in ('.json', '.log', '.npz') or path.name in ('inputs.png', 'tracks.png'))
                if top and path.suffix == '.png' and path.name not in {
                        'inputs.png', 'tracks.png', 'cue.png', *(f'{prefix}{i}.png' for prefix in ('rgb-view-', 'view-') for i in range(3))}:
                    raise ValueError('unclassified real-video image: ' + path.name)
            if keep:
                selected.append((path, root.name + '/' + relative.as_posix()))
    selected += [(path, 'successful-0343/' + path.name) for path in files(FIXTURE)]
    selected += [(path, 'recovery-source/' + path.name) for path in (*SOURCES, Path(__file__), REPLAY)]
    return selected


def verify_archive(plan):
    path = regular(CLOSED / 'evidence.zip')
    if sha(path) != plan['archive_sha256'] or path.stat().st_size != plan['archive_bytes']:
        raise ValueError('compact archive changed')
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('archive CRC failure')
        if archive.namelist() != [row['member'] for row in plan['members']]:
            raise ValueError('archive member set/order changed')
        for row in plan['members']:
            data = archive.read(row['member'])
            if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('archive member identity failure: ' + row['member'])


def load_plan():
    plan = read(regular(CLOSED / 'plan.json'))
    if plan['cleanup_scope'] != [str(path) for path in SCOPES] or plan['protection_basis_sha256'] != sha(BASIS):
        raise ValueError('closeout scope or inherited protection basis changed')
    expected = {row['path']: row['sha256'] for row in read(BASIS)['protected']}
    recorded = {row['path']: row['sha256'] for row in plan['protected']}
    extra = {str(PRIVATE / 'pairwise-physical-0336' / name) for name in ('verify.py', 'retained-fixture-verification.json')}
    extra |= {str(FIXTURE / name) for name in FIXTURE_NAMES} | {str(REPLAY)}
    if len(recorded) != 112 or set(recorded) != set(expected) | extra or any(recorded[key] != value for key, value in expected.items()):
        raise ValueError('incomplete or changed protected list')
    verify_hashes(plan['protected'])
    verify_archive(plan)
    return plan


def prepare():
    if CLOSED.exists():
        raise ValueError('fresh closeout directory required; inspect any prior attempt manually')
    owned(CLOSED, missing=True)
    gate, protected_rows, jobs = reject_gate(), protected(), terminal()
    source, targets = sources(), inventory()
    selected = archive_selection()
    CLOSED.mkdir()
    members = []
    archive_path = CLOSED / 'evidence.zip'
    with zipfile.ZipFile(archive_path, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, member in selected:
            row = identity(path)
            archive.write(path, member)
            members.append({'source': row['path'], 'member': member, 'bytes': row['bytes'], 'sha256': row['sha256']})
    plan = {'status': 'PREPARED_ONLY_NO_DELETION', 'created_utc': time.time(),
        'cleanup_scope': [str(path) for path in SCOPES], 'targets': targets,
        'protected': protected_rows, 'protection_basis_sha256': sha(BASIS),
        'members': members, 'archive_sha256': sha(archive_path), 'archive_bytes': archive_path.stat().st_size,
        'source': source, 'terminal_jobs': jobs, 'failed_gate': gate,
        'tracked_source_retirement': 'separate root-reviewed apply_patch, not this script',
        'recovery_limits': 'No public weights, isolated env/cache, full frames/cue/tmp or dense native features. Redownload/rerun only with a new justified authorization; no automatic route restoration.'}
    verify_archive(plan)
    verify_hashes(protected_rows)
    if inventory() != targets or sources() != source:
        raise ValueError('candidate files/source changed while archiving')
    write_new('plan.json', plan)
    return {'status': plan['status'], 'candidate_files': len(targets),
        'candidate_bytes': sum(row['bytes'] for row in targets), 'protected_files': len(protected_rows),
        'archive_members': len(members), 'archive_bytes': plan['archive_bytes'],
        'archive_sha256': plan['archive_sha256']}


def execute():
    if (CLOSED / 'receipt.json').exists():
        raise ValueError('deletion already recorded; no automatic rerun')
    plan = load_plan()
    jobs = terminal()
    if inventory() != plan['targets'] or sources() != plan['source']:
        raise ValueError('exact candidate inventory/source changed since reviewed prepare')
    # Validate the complete list before the first unlink. Tracked Python source
    # is intentionally excluded; root retires it through apply_patch afterward.
    for row in plan['targets']:
        path = regular(row['path'])
        if path not in CACHES and not any(path.is_relative_to(root) for root in SCOPES):
            raise ValueError('not a positively scoped deletion target')
    for row in plan['targets']:
        path = regular(row['path'])
        if sha(path) != row['sha256']:
            raise ValueError('target changed immediately before deletion')
        path.unlink()
    for root in SCOPES:
        for directory, _dirs, _remaining in os.walk(owned(root), topdown=False, followlinks=False):
            directory = owned(directory)
            if any(directory.iterdir()):
                raise ValueError('unexpected remaining content; stop without widening scope')
            directory.rmdir()
    verify_hashes(plan['protected'])
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'removed_files': len(plan['targets']),
        'removed_logical_bytes': sum(row['bytes'] for row in plan['targets']),
        'protected_files': len(plan['protected']), 'terminal_jobs': jobs,
        'completed_utc': time.time(), 'archive_sha256': plan['archive_sha256'],
        'source_retirement': 'pending separate apply_patch; verify must still run'}
    write_new('receipt.json', result)
    return result


def verify():
    plan = load_plan()
    if read(regular(CLOSED / 'receipt.json'))['status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('private asset deletion receipt required')
    if any(os.path.lexists(path) for path in (*SCOPES, *SOURCES, *CACHES)):
        raise ValueError('candidate directory/source/exact bytecode remains')
    cache_dir = ROOT / 'tools/__pycache__'
    if cache_dir.exists() and any(any(path.name.startswith(stem + '.') for stem in STEMS)
            and path.suffix == '.pyc' for path in owned(cache_dir).iterdir()):
        raise ValueError('candidate bytecode remains; do not delete unconfirmed variants')
    outputs = ('verification.json', 'fixture-replay.log', 'fixture-replay-worker.json',
               'fixture-replay.json', 'suite.log', 'suite-worker.json', 'main-runtime.json')
    if any((CLOSED / name).exists() for name in outputs):
        raise ValueError('fresh verification only; do not overwrite recorded checks')
    # Shared bounded runner executes only saved-fixture math and retained tests.
    from bounded_process import run
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4')
    replay = run([str(PYTHON), '-B', str(REPLAY)], str(ROOT), env,
                 CLOSED / 'fixture-replay.log', CLOSED / 'fixture-replay-worker.json', 60, 1024 ** 3)
    if replay['status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('retained fixture replay failed; see new private log')
    replay_report = read(CLOSED / 'fixture-replay.log')
    if replay_report['status'] != 'TECHNICAL_CHECK_PASSED' or replay_report['models_loaded'] is not False:
        raise ValueError('model-free replay did not establish its declared scope')
    write_new('fixture-replay.json', replay_report)
    suite = run([str(PYTHON), '-B', '-m', 'unittest', 'discover', '-s', 'tests'], str(ROOT), env,
                CLOSED / 'suite.log', CLOSED / 'suite-worker.json', 120, 1024 ** 3)
    if suite['status'] != 'TECHNICAL_CHECK_PASSED':
        raise ValueError('remaining shared suite failed; see private log')
    absent = subprocess.run([str(PYTHON), '-B', '-c',
        "import importlib.util; assert importlib.util.find_spec('torch') is None; print('main Torch absent')"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=30, check=True)
    write_new('main-runtime.json', {'status': 'TECHNICAL_CHECK_PASSED', 'stdout': absent.stdout})
    verify_hashes(plan['protected'])
    verify_archive(plan)
    result = {'status': 'TECHNICAL_CHECK_PASSED', 'completed_utc': time.time(),
        'protected_files': len(plan['protected']), 'fixture_replay': replay_report,
        'suite': suite, 'archive_sha256': plan['archive_sha256'],
        'scope': 'cleanup and saved numerical fixture integrity only; real-video support REJECT; head/medical precision UNVERIFIED'}
    write_new('verification.json', result)
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('prepare', 'execute', 'verify'):
        raise SystemExit('usage: close_aliked_0344.py prepare|execute|verify')
    print(json.dumps(globals()[sys.argv[1]](), indent=2, allow_nan=False))
