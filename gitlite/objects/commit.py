from .base import GitObject
import collections


def serialize_kvlm(kvlm):
    ret = b""
    for k in kvlm.keys():
        # Skip the message (key None)
        if k is None: continue
        val = kvlm[k]
        # Normalize to list
        if not isinstance(val, list):
            val = [val]

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    ret += b'\n' + kvlm[None]
    return ret


class GitCommit(GitObject):
    fmt = b'commit'

    def __init__(self, data=None):
        self.kvlm = dict()
        super().__init__(data)
 
    def deserialize(self, data):
        self.kvlm = self.parse_kvlm(data)
 
    def serialize(self):
        return serialize_kvlm(self.kvlm)
 
    def parse_kvlm(self, raw, start=0, dct=None):
        if not dct:
            dct = collections.OrderedDict()
 
        spc = raw.find(b' ', start)
        nl = raw.find(b'\n', start)
 
        # If no space or newline is found, or newline comes before space, it means we are at the blank line before the message.
        if (spc < 0) or (nl < spc):
            assert nl == start
            dct[None] = raw[start+1:]
            return dct
 
        key = raw[start:spc]
 
        # Find the end of the value. Continuation lines start with space.
        end = start
        while True:
            end = raw.find(b'\n', end+1)
            if raw[end+1] != ord(' '): break
 
        value = raw[spc+1:end].replace(b'\n ', b'\n')
 
        if key in dct:
            if isinstance(dct[key], list):
                dct[key].append(value)
            else:
                dct[key] = [dct[key], value] # Convert existing single value to a list
        else:
            dct[key] = value
 
        return self.parse_kvlm(raw, start=end+1, dct=dct)
 
