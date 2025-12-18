import struct
import zlib
from pathlib import Path
from .delta import patch_delta
from ..objects.blob import GitBlob
from ..objects.tree import GitTree
from ..objects.commit import GitCommit
from ..objects.tag import GitTag
from .types import OBJ_COMMIT, OBJ_TREE, OBJ_BLOB, OBJ_TAG, OBJ_OFS_DELTA, OBJ_REF_DELTA
 
class GitPack:
    def __init__(self, path, resolve_base_fn=None):
        if str(path).endswith(".idx") or str(path).endswith(".pack"):
            path = Path(str(path)[:-4])
            
        self.pack_path = path.with_suffix(".pack")
        self.idx_path = path.with_suffix(".idx")
        self.f_idx = None
        self.f_pack = None
        self.fanout = []
        self.total_objects = 0
        self.sha_offset = 0
        self.resolve_base_fn = resolve_base_fn
 
    def load_index(self):
        if self.f_idx:
            return
            
        try:
            self.f_idx = open(self.idx_path, "rb")
        except FileNotFoundError:
            return
        
        magic = self.f_idx.read(4)
        if magic != b'\377tOc':
            raise Exception("Not a git index file")
            
        version = struct.unpack(">I", self.f_idx.read(4))[0]
        if version != 2:
            raise Exception(f"Unsupported index version {version}")
            
        self.fanout = []    # fanout[i] = number of object SHAs whose first byte ≤ i
        for _ in range(256):
            n = struct.unpack(">I", self.f_idx.read(4))[0]
            self.fanout.append(n)
            
        self.total_objects = self.fanout[255]
        self.sha_offset = 4 + 4 + (256 * 4)
 
    def find_offset(self, sha_hex):
        self.load_index()
        if not self.f_idx:
            return None
            
        sha_bytes = bytes.fromhex(sha_hex)
        first_byte = sha_bytes[0]
        
        start = 0 if first_byte == 0 else self.fanout[first_byte - 1]
        end = self.fanout[first_byte]
        
        if start == end:
            return None
            
        lo = start
        hi = end
        
        while lo < hi:
            mid = (lo + hi) // 2
            self.f_idx.seek(self.sha_offset + (mid * 20))
            data = self.f_idx.read(20)
            
            if data < sha_bytes:
                lo = mid + 1
            elif data > sha_bytes:
                hi = mid
            else:
                return self.get_offset_by_index(mid)
                
        return None
 
    def get_offset_by_index(self, idx):
        offset_table_start = self.sha_offset + (self.total_objects * 20) # Skip the SHA table
        offset_table_start += (self.total_objects * 4)  # Skip the CRC32 table
        
        self.f_idx.seek(offset_table_start + (idx * 4)) # Inside the small offset table
        offset = struct.unpack(">I", self.f_idx.read(4))[0]
        
        if offset & 0x80000000:
            large_offset_idx = offset & 0x7FFFFFFF
            large_offset_start = offset_table_start + (self.total_objects * 4)
            self.f_idx.seek(large_offset_start + (large_offset_idx * 8))
            offset = struct.unpack(">Q", self.f_idx.read(8))[0]
            
        return offset

    def read_object(self, offset):
        type_num, data = self.get_raw_object(offset)
        
        if type_num == OBJ_COMMIT: return GitCommit(data)
        if type_num == OBJ_TREE: return GitTree(data)
        if type_num == OBJ_BLOB: return GitBlob(data)
        if type_num == OBJ_TAG: return GitTag(data)
        return None

    def get_raw_object(self, offset):
        if not self.f_pack:
            self.f_pack = open(self.pack_path, "rb")
        
        self.f_pack.seek(offset)
        
        byte = ord(self.f_pack.read(1))         # bit 7        bit 4–6       bit 0–3
        type_num = (byte >> 4) & 7              # +-----------+-------------+-----------+
        size = byte & 15                        # | continue? |  type (3)   | size (4)  |
        shift = 4                               # +-----------+-------------+-----------+
        
        while byte & 128:                       # bit 7        bit 0–6
            byte = ord(self.f_pack.read(1))     # +-----------+-----------+
            size += (byte & 127) << shift       # | continue? | size bits |
            shift += 7                          # +-----------+-----------+
            
        if type_num in [OBJ_COMMIT, OBJ_TREE, OBJ_BLOB, OBJ_TAG]:
            data = self.read_compressed_data()
            return type_num, data
        elif type_num == OBJ_OFS_DELTA:
            return self.read_ofs_delta(offset)
        elif type_num == OBJ_REF_DELTA:
            return self.read_ref_delta()
        else:
            raise Exception(f"Unknown type {type_num}")

    def read_compressed_data(self):
        dobj = zlib.decompressobj() # streaming de-compression
        data = b""
        while True:
            chunk = self.f_pack.read(4096)
            if not chunk: break
            data += dobj.decompress(chunk)
            if dobj.eof:
                break
        return data

    def read_ofs_delta(self, current_offset):
        # Decode OFS_DELTA backward offset.
        # Encoding follows Git pack-file specification:
        # continuation bytes add a bias (+1) before shifting.
        byte = ord(self.f_pack.read(1))
        offset = byte & 127
        while byte & 128:
            byte = ord(self.f_pack.read(1))
            offset += 1
            offset <<= 7
            offset += (byte & 127)
            
        delta_data = self.read_compressed_data()
        
        base_offset = current_offset - offset
        base_type, base_data = self.get_raw_object(base_offset)
        
        return base_type, patch_delta(base_data, delta_data)

    def read_ref_delta(self):
        base_sha = self.f_pack.read(20).hex()
        delta_data = self.read_compressed_data()
        
        if not self.resolve_base_fn:
             raise Exception("Cannot resolve REF_DELTA without resolver function")
             
        base_type, base_data = self.resolve_base_fn(base_sha)
        if base_type is None:
             raise Exception(f"Base object {base_sha} not found for REF_DELTA")
             
        return base_type, patch_delta(base_data, delta_data)