"""Windows worker-tree budgets;venv launchers are not the computational payload."""
import ctypes
import json
import os
import subprocess
import time


def descendant_ids(rows, root, not_before):
    """Windows PPIDs outlive their parent; reject reused-PID ancestral links."""
    eligible = [(pid, parent) for pid, parent, born in rows if born >= not_before]
    found = {root}
    while True:
        expanded = found | {pid for pid, parent in eligible if parent in found}
        if expanded == found:
            return found
        found = expanded


def run(command, cwd, env, log_path, record_path, seconds, working_bytes):
    class Memory(ctypes.Structure):
        _fields_ = [('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[
            (name,ctypes.c_size_t) for name in ('peak','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile')]
    class Entry(ctypes.Structure):
        _fields_ = [('size',ctypes.c_ulong),('usage',ctypes.c_ulong),('pid',ctypes.c_ulong),
                    ('heap',ctypes.c_size_t),('module',ctypes.c_ulong),('threads',ctypes.c_ulong),
                    ('parent',ctypes.c_ulong),('priority',ctypes.c_long),('flags',ctypes.c_ulong),('name',ctypes.c_wchar*260)]
    kernel = ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [ctypes.c_ulong,ctypes.c_ulong]
    kernel.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    kernel.Process32FirstW.argtypes = kernel.Process32NextW.argtypes = [ctypes.c_void_p,ctypes.POINTER(Entry)]
    kernel.OpenProcess.argtypes = [ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_ulonglong)] * 4
    kernel.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    measure = ctypes.windll.psapi.GetProcessMemoryInfo
    measure.argtypes = [ctypes.c_void_p,ctypes.POINTER(Memory),ctypes.c_ulong]

    def descendants(pid):
        snapshot = kernel.CreateToolhelp32Snapshot(2,0)
        if snapshot==ctypes.c_void_p(-1).value:
            raise OSError('process snapshot unavailable')
        entry = Entry()
        entry.size = ctypes.sizeof(entry)
        rows = []
        try:
            ok = kernel.Process32FirstW(snapshot,ctypes.byref(entry))
            if not ok:
                raise OSError('process inventory unavailable')
            while ok:
                handle = kernel.OpenProcess(0x1000,False,entry.pid)
                if handle:
                    try:
                        times = [ctypes.c_ulonglong() for _ in range(4)]
                        if kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
                            rows.append((int(entry.pid),int(entry.parent),times[0].value))
                    finally:
                        kernel.CloseHandle(handle)
                ok = kernel.Process32NextW(snapshot,ctypes.byref(entry))
        finally:
            kernel.CloseHandle(snapshot)
        return descendant_ids(rows, pid, not_before)

    def kill_tree(worker):
        if worker.poll() is None:
            # Do not let taskkill /T follow stale parent IDs into unrelated apps.
            for pid in sorted(descendants(worker.pid) - {worker.pid}):
                handle = kernel.OpenProcess(0x1001, False, pid)
                if handle:
                    try:
                        times = [ctypes.c_ulonglong() for _ in range(4)]
                        if kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)) and times[0].value >= not_before:
                            kernel.TerminateProcess(handle, 1)
                    finally:
                        kernel.CloseHandle(handle)
            if worker.poll() is None:
                worker.kill()

    start = time.monotonic()
    peaks = {}
    record = {'status':'RUNNING','started_utc':time.time(),'peak_working_set':0,
              'measurement_scope':'conservative sum of observed worker-tree historical process peaks'}
    with log_path.open('w',encoding='utf8') as log:
        not_before = int((time.time() + 11644473600) * 10000000)
        worker = subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        record['pid'] = worker.pid
        record_path.write_text(json.dumps(record,indent=2))
        last_write = start
        try:
            while worker.poll() is None:
                measured = 0
                for pid in descendants(worker.pid):
                    handle = kernel.OpenProcess(0x410,False,pid)
                    if not handle:
                        continue
                    try:
                        info = Memory()
                        info.cb = ctypes.sizeof(info)
                        if measure(handle,ctypes.byref(info),info.cb):
                            measured += 1
                            peaks[pid] = max(peaks.get(pid,0),int(info.peak))
                    finally:
                        kernel.CloseHandle(handle)
                if not measured and worker.poll() is None:
                    raise OSError('live worker-tree memory measurement unavailable')
                record.update(peak_working_set=sum(peaks.values()),observed_process_peaks={str(k):v for k,v in peaks.items()})
                if time.monotonic()-start>seconds or record['peak_working_set']>working_bytes:
                    record['failure'] = 'registered time/memory budget exceeded'
                    kill_tree(worker)
                    break
                if time.monotonic()-last_write>=1:
                    record_path.write_text(json.dumps(record,indent=2))
                    last_write = time.monotonic()
                time.sleep(.05)
        except Exception as error:
            record['failure'] = type(error).__name__+':'+str(error)
            kill_tree(worker)
        finally:
            kill_tree(worker)
            worker.wait(timeout=10)
            record.update(status='TECHNICAL_CHECK_PASSED' if worker.returncode==0 and 'failure' not in record else 'REJECT',
                          exit=worker.returncode,seconds=time.monotonic()-start)
            record_path.write_text(json.dumps(record,indent=2))
    return record
