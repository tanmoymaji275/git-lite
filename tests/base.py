import unittest
import shutil
import tempfile
import os
from pathlib import Path
from gitlite.repo import GitRepository


def create_file(name, content):
    path = Path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return path


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temp directory
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize repo
        self.repo_path = Path(self.test_dir)
        self.repo = GitRepository(self.repo_path, force=True)
        self.repo.init()
 
    def tearDown(self):
        os.chdir(self.old_cwd)
        # noinspection PyBroadException
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass # Windows sometimes holds file locks
        
