"""One authorized fixed-schedule capacity run;never a video/head fitter."""

import ctypes
from ctypes import wintypes
import datetime
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets/private/opend4rt-capacity-0266"
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"src"))
from inspect_opend4rt_checkpoint_0263 import memory_headroom


def registration():
    phase=json.loads((OUT/"phase-start.json").read_text())
    if (phase.get("user_authorized") is not True or phase.get("whole_seconds")!=2400
            or phase.get("schedule")!=512 or phase.get("points")!=2355 or phase.get("frames")!=32
            or phase.get("physical_gates_unchanged") is not True):
        raise ValueError("Missing exact0266 authorization/contract")
    deadline=datetime.datetime.fromisoformat(phase["utc"].replace("Z","+00:00")).timestamp()+2400
    if time.time()>=deadline: raise TimeoutError("Original0266 whole-phase deadline")
    return phase,deadline


def worker():
    registration()
    import check_opend4rt_3d_0264 as capacity
    from headfoundry.manifest import sha256_file
    frozen=ROOT/"assets/private/opend4rt-known3d-0264"
    if (sha256_file(frozen/"input.npz")!="80c765f00a330aa004aea4ecc222e632cf985429f894d9532dd62a193de43415"
            or json.loads((frozen/"model.json").read_text())["flat_sha256"]!="72f6b2f7e5eec64012a94b33c72d8aca8935598685549383cd6c9729a0590551"
            or sha256_file(ROOT/"examples/opend4rt-known3d-0264.asset-lock.json")!="11bb9fda9158f012a45c0eee36b86237fa0f2e3b67b4beff63651c3732b216db"):
        raise ValueError("Changed frozen model/input/scope")
    started=time.perf_counter()
    try: capacity.infer(OUT,batch_diagnostic=True)
    except BaseException as error:
        (OUT/"infer-failure.json").write_text(json.dumps(dict(status="REJECT",error_type=type(error).__name__,error=str(error),seconds=time.perf_counter()-started),indent=2))
        raise


def run():
    phase,deadline=registration()
    started=time.perf_counter();nonce=secrets.token_hex(16)
    # Exclusive marker prevents a second full model launch under this registration.
    with (OUT/"launch-once.json").open("x") as handle:
        json.dump(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_pid=os.getpid(),run_token=nonce),handle)
    os.environ.update(HF0264_RUN_TOKEN=nonce,PYTHONDONTWRITEBYTECODE="1",TMP=str(OUT/"tmp"),TEMP=str(OUT/"tmp"))
    result=dict(status="RUNNING",parent_pid=os.getpid(),run_token=nonce)
    process=None;actual=None;handle=None;peak=0;pressure=0;reason=None
    class Counters(ctypes.Structure):
        _fields_=[("cb",wintypes.DWORD),("faults",wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ["peak","working","paged_peak","paged","nonpaged_peak","nonpaged","pagefile","pagefile_peak"]]
    kernel=ctypes.WinDLL("kernel32",use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    psapi=ctypes.WinDLL("psapi",use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    def stop_owned_tree():
        if process is not None and process.poll() is None:
            stopped=subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],capture_output=True,text=True)
            (OUT/"stop.txt").write_text(stopped.stdout+stopped.stderr)
            process.wait(timeout=30)
    try:
        before=memory_headroom();result["headroom_before"]=before
        if min(before.values())<8_000_000_000:raise RuntimeError("Insufficient8GB RAM/commit headroom")
        limit=min(1200,deadline-time.time()-600);result["worker_limit_seconds"]=limit
        if limit<=0:raise TimeoutError("No original worker time after closeout reserve")
        with (OUT/"stdout.txt").open("w") as stdout,(OUT/"stderr.txt").open("w") as stderr:
            process=subprocess.Popen([str(ROOT/".venv-opend4rt0262/Scripts/python.exe"),str(Path(__file__)),"worker"],cwd=ROOT,stdout=stdout,stderr=stderr)
            result["launcher_pid"]=process.pid
            while process.poll() is None:
                if time.perf_counter()-started>=limit:reason="registered worker/whole deadline";break
                if handle is None and (OUT/"inference-live.json").exists():
                    live=json.loads((OUT/"inference-live.json").read_text())
                    if live["run_token"]==nonce:
                        actual=int(live["pid"]);handle=kernel.OpenProcess(0x0400|0x0010,False,actual)
                        if not handle:raise ctypes.WinError(ctypes.get_last_error())
                if handle:
                    counters=Counters();counters.cb=ctypes.sizeof(counters)
                    if not psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),counters.cb):
                        if process.poll() is None:raise ctypes.WinError(ctypes.get_last_error())
                    else:
                        peak=max(peak,counters.peak)
                        if peak>=7_000_000_000:reason="registered7GB peak working-set bound";break
                headroom=memory_headroom()
                pressure=pressure+1 if headroom["available_ram_bytes"]<1_500_000_000 or headroom["process_commitable_bytes"]<1_000_000_000 else 0
                if pressure>=2:reason="sustained RAM/commit pressure";break
                time.sleep(1)
            if reason:stop_owned_tree()
            result["exit"]=process.wait()
            result["status"]="TECHNICAL_CHECK_PASSED" if result["exit"]==0 and reason is None else "REJECT"
    except BaseException as error:
        stop_owned_tree();result.update(status="REJECT",error_type=type(error).__name__,error=str(error))
        (OUT/"parent-error.txt").write_text(traceback.format_exc())
    finally:
        if handle:kernel.CloseHandle(handle)
        result.update(actual_worker_pid=actual,peak_working_set_bytes=peak,seconds=time.perf_counter()-started,stop_reason=reason,scope="execution_resource_guard_not_accuracy")
        (OUT/"process.json").write_text(json.dumps(result,indent=2))


if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1] not in {"run","worker","evaluate"}:raise SystemExit("run|worker|evaluate required")
    if sys.argv[1]=="worker":worker()
    elif sys.argv[1]=="run":run()
    else:
        registration()
        process=json.loads((OUT/"process.json").read_text())
        if process["status"]!="TECHNICAL_CHECK_PASSED":raise RuntimeError("Complete terminal inference required")
        from headfoundry.manifest import sha256_file
        if sha256_file(ROOT/"assets/private/opend4rt-known3d-0264/evaluation-truth.npz")!="5d6386d828fe12c64f36db6bfbcbbdf089b92ceac33ba29d53873f942c55af27":
            raise ValueError("Changed frozen evaluation truth")
        from check_opend4rt_3d_0264 import evaluate
        evaluate(OUT)
