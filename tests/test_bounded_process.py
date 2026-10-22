from pathlib import Path
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
            first = run([sys.executable,'-c','print(307)'],root,env,path/'ok.log',path/'ok.json',5,1024**3)
            self.assertEqual(first['status'],'TECHNICAL_CHECK_PASSED')
            slow = run([sys.executable,'-c','import time;time.sleep(2)'],root,env,path/'slow.log',path/'slow.json',.1,1024**3)
            self.assertEqual(slow['status'],'REJECT')
            self.assertIn('budget',slow['failure'])
