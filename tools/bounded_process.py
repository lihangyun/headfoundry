"""Windows bounded local worker;preserve logs and never restart on timeout."""
import ctypes
import json
import subprocess
import time


def run(command, cwd, env, log_path, record_path, seconds, working_bytes):
    class Memory(ctypes.Structure):
        _fields_ = [('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[
            (name,ctypes.c_size_t) for name in ('peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
    info = Memory()
    info.cb = ctypes.sizeof(info)
    measure = ctypes.windll.psapi.GetProcessMemoryInfo
    measure.argtypes = [ctypes.c_void_p,ctypes.POINTER(Memory),ctypes.c_ulong]
    start = time.monotonic()
    record = {'status':'RUNNING','started_utc':time.time(),'peak_working_set':0}
    with log_path.open('w',encoding='utf8') as log:
        worker = subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        record['pid'] = worker.pid
        record_path.write_text(json.dumps(record,indent=2))
        try:
            while worker.poll() is None:
                if not measure(int(worker._handle),ctypes.byref(info),info.cb):
                    # A process may exit between poll and its final memory read.
                    if worker.poll() is None:
                        record['failure'] = 'working-set measurement unavailable'
                        worker.kill()
                        break
                record['peak_working_set'] = max(record['peak_working_set'],int(info.peak))
                if time.monotonic()-start>seconds or record['peak_working_set']>working_bytes:
                    record['failure'] = 'registered time/memory budget exceeded'
                    worker.kill()
                    break
                time.sleep(.05)
        finally:
            if worker.poll() is None:
                worker.kill()
            worker.wait(timeout=10)
            record.update(status='TECHNICAL_CHECK_PASSED' if worker.returncode==0 and 'failure' not in record else 'REJECT',
                          exit=worker.returncode,seconds=time.monotonic()-start)
            record_path.write_text(json.dumps(record,indent=2))
    return record
