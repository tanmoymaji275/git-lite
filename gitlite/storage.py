import hashlib
import zlib
from .objects.blob import GitBlob
from .objects.commit import GitCommit
from .objects.tree import GitTree
 
def object_read(repo, sha):
    path = repo.gitdir / "objects" / sha[0:2] / sha[2:]
 
    if not path.is_file():
        return None
 
    with open(path, "rb") as f:
        raw = zlib.decompress(f.read()) # b'<type> <size>\x00<payload>
 
    # Read object type
    x = raw.find(b' ')
    fmt = raw[0:x]
 
    # Read and validate object size
    y = raw.find(b'\x00', x)
    size = int(raw[x+1:y].decode("ascii"))
    if size != len(raw)-y-1:
        raise Exception(f"Malformed object {sha}: bad length")
 
    # Pick constructor
    OBJECT_TYPES = {
        b'blob': GitBlob,
        b'commit': GitCommit,
        b'tree': GitTree
    }

    if fmt in OBJECT_TYPES:
        c = OBJECT_TYPES[fmt]
    else:
        # Other object types can be added later
        raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")
 
    # Call constructor
    return c(raw[y+1:])
 
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