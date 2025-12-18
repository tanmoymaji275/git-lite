import sys
from io import StringIO
from tests.base import BaseTestCase, create_file
from gitlite.commands.commit import cmd_commit
from gitlite.commands.diff import cmd_diff
from gitlite.commands.config import cmd_config

class TestDiff(BaseTestCase):
    def test_diff_basic(self):
        # Config
        cmd_config(["user.name", "Tester"])
        cmd_config(["user.email", "test@test.com"])
        
        # 1. Create and Commit
        create_file("hello.txt", "v1\n")
        
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        try:
            cmd_commit(["-m", "Commit 1"])
        finally:
            sys.stdout = saved_stdout
            
        # 2. Modify
        create_file("hello.txt", "v2\n")
        
        # 3. Diff
        out = StringIO()
        sys.stdout = out
        try:
            cmd_diff([])
        finally:
            sys.stdout = saved_stdout
            
        output = out.getvalue()
        self.assertIn("--- a/hello.txt", output)
        self.assertIn("+++ b/hello.txt", output)
        self.assertIn("-v1", output)
        self.assertIn("+v2", output)
