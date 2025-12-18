from .base import GitObject
from .kvlm import kvlm_parse, kvlm_serialize
 
class GitTag(GitObject):
    fmt = b'tag'
 
    def __init__(self, data=None):
        self.kvlm = dict()
        super().__init__(data)
 
    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)
 
    def serialize(self):
        return kvlm_serialize(self.kvlm)