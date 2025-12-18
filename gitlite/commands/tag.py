import os
import sys
from ..repo import repo_find, resolve_ref
from ..storage import object_read, object_write
from ..objects.tag import GitTag
from ..utils import get_signature
 
def cmd_tag(args):
    repo = repo_find()
    
    if not args:
        # List tags
        tags_dir = repo.gitdir / "refs" / "tags"
        if not tags_dir.exists():
            return
 
        tags = sorted(os.listdir(tags_dir))
        for tag in tags:
            print(tag)
        return
 
    # Parse args
    annotated = False
    message = None
    name = None
    target = "HEAD"
    
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "-a":
            annotated = True
        elif arg == "-m":
            idx += 1
            if idx < len(args):
                message = args[idx]
                annotated = True # -m implies -a
            else:
                print("error: option -m needs an argument")
                sys.exit(129)
        elif name is None:
            name = arg
        elif target == "HEAD":
            target = arg
        idx += 1
        
    if not name:
        print("usage: gitlite tag [-a] [-m msg] <name> [object]")
        sys.exit(1)
 
    sha = resolve_ref(repo, target)
    if not sha:
        print(f"fatal: Failed to resolve '{target}' as a valid ref.")
        sys.exit(128)
        
    obj = object_read(repo, sha)
    if not obj:
        print(f"fatal: Failed to read object '{sha}'.")
        sys.exit(128)
        
    if annotated:
        tag = GitTag()
        # Headers: object, type, tag, tagger
        
        type_str = obj.fmt.decode()
        tagger_str = get_signature(repo)
        
        if not message:
            message = "Tag " + name
            
        tag.kvlm = {
            b'object': sha.encode(),
            b'type': type_str.encode(),
            b'tag': name.encode(),
            b'tagger': tagger_str.encode(),
            None: message.encode() + b'\n'
        }
        
        tag_sha = object_write(tag, repo)
        ref_sha = tag_sha
    else:
        ref_sha = sha
        
    # Write ref
    ref_path = repo.gitdir / "refs" / "tags" / name
    if ref_path.exists():
        print(f"fatal: tag '{name}' already exists")
        sys.exit(128)
        
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ref_path, "w") as f:
        f.write(ref_sha + "\n")