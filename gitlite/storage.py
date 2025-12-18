import hashlib
import zlib
from .objects.blob import GitBlob
from .objects.commit import GitCommit
from .objects.tree import GitTree
from .pack.packfile import GitPack
from .pack.types import OBJ_COMMIT, OBJ_TREE, OBJ_BLOB, OBJ_TAG
 
def object_read_raw(repo, sha):

    # 1. Try loose object
    path = repo.gitdir / "objects" / sha[0:2] / sha[2:]
    
    if path.is_file():
        with open(path, "rb") as f:
            raw = zlib.decompress(f.read())
            
        x = raw.find(b' ')
        fmt = raw[0:x]
        y = raw.find(b'\x00', x)
        
        if fmt == b'commit': type_num = OBJ_COMMIT
        elif fmt == b'tree': type_num = OBJ_TREE
        elif fmt == b'blob': type_num = OBJ_BLOB
        elif fmt == b'tag': type_num = OBJ_TAG
        else:
            raise Exception(f"Unknown type {fmt} in loose object")
            
        return type_num, raw[y+1:]
 
    # 2. Try packfiles
    pack_dir = repo.gitdir / "objects" / "pack"
    if pack_dir.is_dir():
        for idx_file in pack_dir.glob("*.idx"):
            pack = GitPack(idx_file, resolve_base_fn=lambda s: object_read_raw(repo, s))
            offset = pack.find_offset(sha)
            if offset is not None:
                return pack.get_raw_object(offset)
                
    return None, None
 
def object_read(repo, sha):
    type_num, data = object_read_raw(repo, sha)
    if type_num is None:
        return None
        
    if type_num == OBJ_COMMIT: return GitCommit(data)
    if type_num == OBJ_TREE: return GitTree(data)
    if type_num == OBJ_BLOB: return GitBlob(data)
    # Tag not implemented fully
    return None
 
def object_write(obj, repo=None):
    """Serialize the object, compute its SHA-1 hash, and optionally write it to the repository."""
    data = obj.serialize()
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    
    sha = hashlib.sha1(result).hexdigest()
 
    if repo:
        path = repo.gitdir / "objects" / sha[0:2] / sha[2:]
        path.parent.mkdir(parents=True, exist_ok=True)
 
        # `x` (Exclusive Creation): create only if it doesn't exist
        try:
            with open(path, "xb") as f:
                f.write(zlib.compress(result))
        except FileExistsError:
            # Object already exists, which is fine (same content = same SHA)
            pass
 
    return sha