from .base import GitObject


def parse_tree(raw):
    pos = 0
    max_len = len(raw)
    ret = []
    while pos < max_len:
        pos_space = raw.find(b' ', pos)
        pos_null = raw.find(b'\x00', pos_space)

        mode = raw[pos:pos_space]
        path = raw[pos_space+1:pos_null]
        # Read 20 bytes for SHA-1
        sha = raw[pos_null+1:pos_null+21]

        ret.append({'mode': mode, 'path': path, 'sha': sha.hex()}) # mode + b' ' + path + b'\x00' + sha_binary

        pos = pos_null + 21
    return ret


def serialize_tree(items):
    ret = b""
    for item in items:
        sha = bytes.fromhex(item['sha'])
        ret += item['mode'] + b' ' + item['path'] + b'\x00' + sha
    return ret


class GitTree(GitObject):
    fmt = b'tree'
 
    def __init__(self, data=None):
        self.items = list()
        super().__init__(data)
 
    def deserialize(self, data):
        self.items = parse_tree(data)
 
    def serialize(self):
        return serialize_tree(self.items)

