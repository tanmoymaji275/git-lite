import sys
from io import StringIO
from unittest.mock import MagicMock
from tests.base import BaseTestCase, create_file
from gitlite.commands.base import cmd_hash_object, cmd_cat_file
from gitlite.storage import object_read
 
class TestCore(BaseTestCase):
    def test_hash_object(self):
        create_file("test.txt", "hello")
        
        # Capture output
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        
        try:
            cmd_hash_object(["-w", "test.txt"])
        finally:
            sys.stdout = saved_stdout
            
        sha = out.getvalue().strip()
        self.assertEqual(len(sha), 40)
        
        # Verify object exists in DB
        obj = object_read(self.repo, sha)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.blobdata, b"hello")
 
    def test_cat_file(self):
        create_file("test.txt", "world")
        
        # Hash it first
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        try:
            cmd_hash_object(["-w", "test.txt"])
        finally:
            sys.stdout = saved_stdout
        sha = out.getvalue().strip()
        
        # Mock sys.stdout to handle buffer.write
        mock_stdout = MagicMock()
        mock_buffer = MagicMock()
        mock_stdout.buffer = mock_buffer
        sys.stdout = mock_stdout
        
        try:
            cmd_cat_file(["blob", sha])
        finally:
            sys.stdout = saved_stdout
            
        # Verify it wrote the correct content
        mock_buffer.write.assert_called_with(b"world")