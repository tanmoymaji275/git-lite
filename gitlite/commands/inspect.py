import sys
from ..repo import repo_find, resolve_ref
from ..storage import object_read

def cmd_log(args):
    repo = repo_find()
    
    sha = args[0] if args else "HEAD"
    sha = resolve_ref(repo, sha)

    visited = set()
    queue = [sha]

    while queue:
        sha = queue.pop(0)
        
        if sha in visited:
            continue
        visited.add(sha)
        
        obj = object_read(repo, sha)
        if not obj:
            if len(visited) == 1:
                print(f"fatal: bad object {sha}")
                sys.exit(128)
            continue
            
        if obj.fmt != b'commit':
            print(f"fatal: {sha} is not a commit object")
            sys.exit(128)
            
        print(f"commit {sha}")
        
        author = obj.kvlm.get(b'author')
        if author:
            if isinstance(author, list): author = author[0]
            print(f"Author: {author.decode()}")

        print("")
        msg = obj.kvlm[None].decode()
        for line in msg.splitlines():
            print(f"    {line}")
        print("")
        
        parents = obj.kvlm.get(b'parent')
        if parents:
            if not isinstance(parents, list):
                parents = [parents]
            
            for p in parents:
                queue.append(p.decode())

def cmd_ls_tree(args):
    repo = repo_find()
    
    if len(args) != 1:
        print("usage: gitlite ls-tree <tree-ish>")
        sys.exit(1)
        
    sha = args[0]
    sha = resolve_ref(repo, sha)

    obj = object_read(repo, sha)
    if not obj:
        print(f"fatal: Not a valid object name {sha}", file=sys.stderr)
        sys.exit(128)
        
    if obj.fmt == b'commit':
        sha = obj.kvlm[b'tree'].decode()
        obj = object_read(repo, sha)
    
    if obj.fmt != b'tree':
        print(f"fatal: {sha} is not a tree object", file=sys.stderr)
        sys.exit(128)
        
    for item in obj.items:
        mode = item['mode'].decode()
        type_ = "unknown"
        if mode.startswith("10"): type_ = "blob"
        elif mode.startswith("12"): type_ = "blob"
        elif mode.startswith("04"): type_ = "tree"
        elif mode == "40000": type_ = "tree"
        elif mode.startswith("16"): type_ = "commit"
        
        path = item['path'].decode()
        sha_hex = item['sha']
        
        print(f"{mode.zfill(6)} {type_} {sha_hex}\t{path}")