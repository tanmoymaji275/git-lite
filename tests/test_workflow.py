import sys
from io import StringIO
from tests.base import BaseTestCase, create_file
from gitlite.commands.commit import cmd_commit
from gitlite.commands.inspect import cmd_log, cmd_ls_tree
from gitlite.commands.branch import cmd_branch
from gitlite.commands.checkout import cmd_checkout
from gitlite.commands.config import cmd_config
from gitlite.commands.tag import cmd_tag
 
class TestWorkflow(BaseTestCase):
    def test_full_workflow(self):
        # 1. Config
        cmd_config(["user.name", "Tester"])
        cmd_config(["user.email", "test@test.com"])
        
        # 2. Create file & Commit
        create_file("hello.txt", "v1")
        
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        try:
            cmd_commit(["-m", "Commit 1"])
        finally:
            sys.stdout = saved_stdout
            
        with open(".git/HEAD", "r") as f:
            ref = f.read().strip()
        self.assertTrue(ref.startswith("ref: refs/heads/master"))
        
        # 3. Modify & Commit again
        create_file("hello.txt", "v2")
        
        out = StringIO()
        sys.stdout = out
        try:
            cmd_commit(["-m", "Commit 2"])
        finally:
            sys.stdout = saved_stdout
            
        # 4. Log
        out = StringIO()
        sys.stdout = out
        try:
            cmd_log([])
        finally:
            sys.stdout = saved_stdout
        
        log_output = out.getvalue()
        self.assertIn("Commit 1", log_output)
        self.assertIn("Commit 2", log_output)
        self.assertIn("Tester <test@test.com>", log_output)
        
        # 5. Branch
        cmd_branch(["feature"])
        self.assertTrue((self.repo.gitdir / "refs/heads/feature").exists())
        
        # 6. Checkout branch
        cmd_checkout(["feature"])
        with open(".git/HEAD", "r") as f:
            head = f.read().strip()
        self.assertEqual(head, "ref: refs/heads/feature")

    def test_tag(self):
        create_file("f", "c")
        
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            cmd_commit(["-m", "msg"])
            cmd_tag(["-a", "-m", "tm", "v1"])
        finally:
            sys.stdout = saved_stdout
            
        self.assertTrue((self.repo.gitdir / "refs/tags/v1").exists())

    def test_ignore(self):
        create_file(".gitignore", "*.tmp")
        create_file("a.tmp", "x")
        create_file("b.txt", "y")
        
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            cmd_commit(["-m", "ignore"])
        finally:
            sys.stdout = saved_stdout
            
        # Verify ls-tree
        out = StringIO()
        sys.stdout = out
        try:
            cmd_ls_tree(["HEAD"])
        finally:
            sys.stdout = saved_stdout
            
        output = out.getvalue()
        self.assertIn("b.txt", output)
        self.assertIn(".gitignore", output)
        self.assertNotIn("a.tmp", output)

    def test_subdir(self):
        create_file("subdir/sub.txt", "z")
        
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            cmd_commit(["-m", "subdir"])
        finally:
            sys.stdout = saved_stdout
            
        # Verify ls-tree
        out = StringIO()
        sys.stdout = out
        try:
            cmd_ls_tree(["HEAD"])
        finally:
            sys.stdout = saved_stdout
            
        output = out.getvalue()
        self.assertIn("subdir", output)
        self.assertIn("tree", output)