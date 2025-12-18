import sys
from io import StringIO
from tests.base import BaseTestCase
from gitlite.commands.config import cmd_config
 
class TestConfig(BaseTestCase):
    def test_config_set_get(self):
        cmd_config(["user.name", "My Name"])
        
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        try:
            cmd_config(["user.name"])
        finally:
            sys.stdout = saved_stdout
            
        self.assertEqual(out.getvalue().strip(), "My Name")