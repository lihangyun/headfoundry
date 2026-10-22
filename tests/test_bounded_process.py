from pathlib import Path
import ctypes
import os
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from bounded_process import run


@unittest.skipUnless(sys.platform=='win32','Windows worker-budget contract')
class BoundedWorkerTest(unittest.TestCase):
    def test_success_and_one_terminal_timeout_without_restart(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'tmp') as folder:
            path = Path(folder)
            env = os.environ.copy()
            env.update(TEMP=str(path),TMP=str(path),PYTHONDONTWRITEBYTECODE='1')
            first = run([sys.executable,'-c','import time;blob=bytearray(60*1024**2);time.sleep(.4);print(307)'],root,env,path/'ok.log',path/'ok.json',5,1024**3)
            self.assertEqual(first['status'],'TECHNICAL_CHECK_PASSED')
            self.assertGreater(first['peak_working_set'],50*1024**2)
            self.assertGreater(max(first['observed_process_peaks'].values()),50*1024**2)
            slow = run([sys.executable,'-c','import time;time.sleep(2)'],root,env,path/'slow.log',path/'slow.json',.1,1024**3)
            self.assertEqual(slow['status'],'REJECT')
            self.assertIn('budget',slow['failure'])
            limited = run([sys.executable,'-c','import time;blob=bytearray(60*1024**2);time.sleep(2)'],root,env,path/'memory.log',path/'memory.json',5,30*1024**2)
            self.assertEqual(limited['status'],'REJECT')
            self.assertGreater(limited['peak_working_set'],30*1024**2)
            kernel = ctypes.WinDLL('kernel32',use_last_error=True)
            kernel.OpenProcess.argtypes = [ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
            kernel.OpenProcess.restype = ctypes.c_void_p
            kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p,ctypes.c_ulong]
            kernel.CloseHandle.argtypes = [ctypes.c_void_p]
            for record in [slow,limited]:
                for pid in record['observed_process_peaks']:
                    handle = kernel.OpenProcess(0x100400,False,int(pid))
                    if handle:
                        try:
                            self.assertEqual(kernel.WaitForSingleObject(handle,0),0)
                        finally:
                            kernel.CloseHandle(handle)
