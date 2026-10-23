"""One-off explicit archive/integrity closeout;never a reconstruction worker."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

ROOT=Path('C:/workspace/headfoundry')
RAW=ROOT/'assets/private/world-light-information-0345'
CLOSED=ROOT/'assets/private/closed-experiments/0345-room-light'
PRIOR=ROOT/'assets/private/closed-experiments/0344-aliked/plan.json'
PRIOR_SHA='275fc10f129ae4b5300454edb3e29976ae3623c3c6d438a16c09d7d51ce6f7a4'
DEADLINE=1792759579.
sys.dont_write_bytecode=True


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))


def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(name,data):
    with (CLOSED/name).open('x',encoding='utf8') as stream:json.dump(data,stream,indent=2,allow_nan=False)


def safe(path,exists=True):
    path=Path(path)
    if not path.is_absolute() or not path.resolve().is_relative_to(ROOT.resolve()) or path.resolve()==ROOT.resolve():
        raise ValueError('exact repository descendant only')
    for part in (path,*path.parents):
        if part==ROOT.parent:break
        if part.exists() and getattr(part.lstat(),'st_file_attributes',0)&1024:raise ValueError('reparse path')
    if exists and not path.exists():raise ValueError('missing exact path')
    if path.is_file() and path.stat().st_nlink!=1:raise ValueError('hardlink not allowed')
    return path


def protected():
    if digest(PRIOR)!=PRIOR_SHA:raise ValueError('inherited protection plan changed')
    records=read(PRIOR)['protected']
    if len(records)!=112 or len({str(Path(i['path']).resolve()).casefold() for i in records})!=112:
        raise ValueError('complete unique112identity protection basis required')
    for item in records:
        path=Path(item['path'])
        if digest(path)!=item['sha256']:raise ValueError('protected identity changed:'+str(path))
    return len(records)


def terminal():
    import ctypes
    record=read(RAW/'worker.json')
    if record['status'] not in ('REJECT','TECHNICAL_CHECK_PASSED') or not isinstance(record.get('exit'),int):
        raise ValueError('explicit terminal worker receipt required')
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    kernel.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(ctypes.c_ulonglong)]*4)]
    rows=[]
    for pid in {record['pid'],*[int(p) for p in record.get('observed_process_peaks',{})]}:
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:rows.append({'pid':pid,'state':'absent or inaccessible,not killed'});continue
        try:
            created,exited,kernel_time,user_time=[ctypes.c_ulonglong() for _ in range(4)]
            if not kernel.GetProcessTimes(handle,*map(ctypes.byref,(created,exited,kernel_time,user_time))):
                raise OSError('process identity unavailable')
            created_utc=created.value/1e7-11644473600
            same=record['started_utc']-.25<=created_utc<=record['started_utc']+record['seconds']+.25
            if same and exited.value==0:raise ValueError('owned worker still alive')
            rows.append({'pid':pid,'created_utc':created_utc,'same_recorded_job':same,
                'state':'terminal or unrelated PID reuse,not killed'})
        finally:kernel.CloseHandle(handle)
    return rows


def summarize():
    result=read(RAW/'result.json')
    print(json.dumps({name:{key:value for key,value in score.items() if key in
        ('rank','nuisance_rank','relative_profile_contrast','sigma_logf_under_declared_noise','off_sensor_samples')}
        for name,score in result['scores'].items()},indent=2))
    checks=read(RAW/'derivative-controls.json')
    print(json.dumps({'normal':read(RAW/'normal-controls.json'),'derivative_maxima':
        [row['maximum'] for row in checks['full_column_controls']],
        'pixel_replay':checks['OpenCV_pixel_replay_max'],'prior_keys':list(read(PRIOR)),
        'prior_plan_sha256':digest(PRIOR)},indent=2))


def archive():
    safe(CLOSED,False);CLOSED.mkdir(exist_ok=False)
    count=protected();jobs=terminal();safe(RAW)
    files=sorted(safe(p) for p in RAW.rglob('*') if p.is_file())
    if any(p.is_dir() for p in RAW.iterdir()):raise ValueError('unexpected nested raw output')
    entries={str(p.relative_to(RAW)).replace('\\','/'):p.read_bytes() for p in files}
    sources=['tools/audit_world_light_0345.py','tools/mesh_normal_jacobian.py',
             'tools/close_world_light_0345.py','tests/test_mesh_normal_jacobian.py',
             'docs/audit-0345-fixed-room-light-information.md']
    for source in sources:entries['source/'+source]=safe(ROOT/source).read_bytes()
    manifests=[{'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in entries.items()]
    archive_path=CLOSED/'evidence.zip'
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED) as target:
        for name,data in entries.items():target.writestr(name,data)
    with zipfile.ZipFile(archive_path) as target:
        if target.testzip() is not None or sorted(target.namelist())!=sorted(entries):raise ValueError('archive CRC/member set')
        for entry in manifests:
            if hashlib.sha256(target.read(entry['name'])).hexdigest()!=entry['sha256']:raise ValueError('archive member hash')
    targets=[{'path':str(p),'bytes':len(entries[str(p.relative_to(RAW)).replace('\\','/')]),
        'sha256':hashlib.sha256(entries[str(p.relative_to(RAW)).replace('\\','/')]).hexdigest()} for p in files]
    for item in targets:
        if digest(item['path'])!=item['sha256'] or Path(item['path']).stat().st_size!=item['bytes']:
            raise ValueError('raw source changed since archived snapshot')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    plan={'prepared_utc':time.time(),'source_recovery':head,'archive_bytes':archive_path.stat().st_size,
        'archive_sha256':digest(archive_path),'archive_members':manifests,'protected_count':count,
        'targets':targets,'terminal_jobs':jobs,'inherited_protection_plan_sha256':PRIOR_SHA,
        'raw_directory':str(RAW),'source_retirement':'root-reviewed apply_patch for two one-off tools only',
        'no_weights_environments_patient_images_installed':True}
    write('plan.json',plan);print(json.dumps({k:v for k,v in plan.items() if k not in ('targets','archive_members')},indent=2))


def retire():
    plan=read(CLOSED/'plan.json');archive_path=safe(CLOSED/'evidence.zip')
    if digest(archive_path)!=plan['archive_sha256']:raise ValueError('archive hash changed')
    with zipfile.ZipFile(archive_path) as target:
        if target.testzip() is not None:raise ValueError('archive CRC')
        for entry in plan['archive_members']:
            if hashlib.sha256(target.read(entry['name'])).hexdigest()!=entry['sha256']:raise ValueError('archive member hash')
    jobs=terminal();protected();safe(RAW)
    actual={str(safe(p)) for p in RAW.iterdir()}
    if actual!={item['path'] for item in plan['targets']}:raise ValueError('raw path inventory changed')
    for item in plan['targets']:
        path=safe(item['path'])
        if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('target changed')
    for item in plan['targets']:Path(item['path']).unlink()
    RAW.rmdir()
    write('receipt.json',{'removed_files':len(plan['targets']),'removed_logical_bytes':sum(i['bytes'] for i in plan['targets']),
        'protected_count_after':protected(),'raw_absent':not RAW.exists(),'finished_utc':time.time(),
        'generic_normal_math_retained':True,'patient_or_shared_files_deleted':False,'terminal_jobs':jobs})
    print((CLOSED/'receipt.json').read_text())


def suite():
    from bounded_process import run
    env=dict(os.environ);env.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4')
    record=run([sys.executable,'-B','-m','unittest','discover','-s','tests'],str(ROOT),env,
        CLOSED/'suite.log',CLOSED/'suite-worker.json',120,1024**3)
    print(json.dumps(record,indent=2))
    if record['status']!='TECHNICAL_CHECK_PASSED':raise ValueError('shared suite failure')
    write('verification.json',{'protected_count_after_suite':protected(),'raw_absent':not RAW.exists(),
        'suite':record,'generic_normal_sha256':digest(ROOT/'tools/mesh_normal_jacobian.py'),
        'test_sha256':digest(ROOT/'tests/test_mesh_normal_jacobian.py'),'verified_utc':time.time()})


if __name__=='__main__':
    if Path.cwd().resolve()!=ROOT.resolve() or time.time()>DEADLINE:raise ValueError('cwd/deadline')
    action={'summary':summarize,'archive':archive,'retire':retire,'suite':suite}.get(sys.argv[1] if len(sys.argv)==2 else '')
    if action is None:raise SystemExit('explicit closeout phase required')
    action()
