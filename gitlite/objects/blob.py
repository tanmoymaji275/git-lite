from .base import GitObject
 
class GitBlob(GitObject):
    fmt = b'blob'

    def __init__(self, data=None):
        self.blobdata = b""
        super().__init__(data)
 
    def serialize(self):
        return self.blobdata
 
    def deserialize(self, data):
        self.blobdata = data