import sys
from pathlib import Path
from .repo import GitRepository, repo_find
from .storage import object_read, object_write
from .objects.blob import GitBlob
 
def cmd_init(args):
    target = Path(args[0]) if args else Path.cwd()
    repo = GitRepository(target, force=True)
    repo.init()
    print(f"Initialized empty Git repository in {repo.gitdir}")
 
def cmd_cat_file(args):
    if len(args) != 2:
        print("usage: gitlite cat-file <type> <object>")
        sys.exit(1)
    
    type_ = args[0]
    sha = args[1]
    
    repo = repo_find()
    
    obj = object_read(repo, sha)
    if not obj:
        print(f"fatal: Not a valid object name {sha}", file=sys.stderr)
        sys.exit(128)
 
    if obj.fmt.decode() != type_:
        print(f"fatal: git cat-file: object is of type {obj.fmt.decode()} but {type_} was specified", file=sys.stderr)
        sys.exit(128)
        
    sys.stdout.buffer.write(obj.serialize())

def cmd_hash_object(args):
    if not args:
        print("usage: gitlite hash-object [-w] <file>")
        sys.exit(1)
    
    write = False
    if args[0] == "-w":
        write = True
        args.pop(0)
    
    path = Path(args[0])
    if not path.is_file():
        print(f"fatal: Cannot open '{path}': No such file or directory", file=sys.stderr)
        sys.exit(128)
        
    with open(path, "rb") as f:
        data = f.read()
    
    obj = GitBlob(data)
    
    repo = None
    if write:
        repo = repo_find()
    
    sha = object_write(obj, repo)
    print(sha)

def cmd_log(args):
    repo = repo_find()
    
    sha = args[0] if args else "HEAD"

    if sha == "HEAD":
        # Resolve HEAD
        with open(repo.gitdir / "HEAD", "r") as f:
            head_ref = f.read().strip()
        if head_ref.startswith("ref: "):
            ref_path = repo.gitdir / head_ref[5:]
            if ref_path.exists():
                with open(ref_path, "r") as f:
                    sha = f.read().strip()
            else:
                print("HEAD points to an unborn branch (no history yet).")
                return
        else:
            sha = head_ref

    visited = set()

    while True:
        if sha in visited:
            break
        visited.add(sha)
        
        obj = object_read(repo, sha)
        if not obj:
            print(f"fatal: bad object {sha}")
            sys.exit(128)
            
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
            if isinstance(parents, list):
                sha = parents[0].decode() # Single parent path at-least for now
            else:
                sha = parents.decode()
        else:
            break

def cmd_ls_tree(args):
    repo = repo_find()
    
    if len(args) != 1:
        print("usage: gitlite ls-tree <tree-ish>")
        sys.exit(1)
        
    sha = args[0]
    
    # Resolve logic
    if sha == "HEAD":
         with open(repo.gitdir / "HEAD", "r") as f:
            head_ref = f.read().strip()
            if head_ref.startswith("ref: "):
                ref_path = repo.gitdir / head_ref[5:]
                if ref_path.exists():
                    with open(ref_path, "r") as _f:
                        sha = _f.read().strip()
                else:
                    print("HEAD points to an unborn branch.")
                    return
            else:
                sha = head_ref

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
 
commands = {
    "init": cmd_init,
    "cat-file": cmd_cat_file,
    "hash-object": cmd_hash_object,
    "log": cmd_log,
    "ls-tree": cmd_ls_tree
}
 
def main():
    if len(sys.argv) < 2:
        print("usage: gitlite <command> [<args>]")
        sys.exit(1)
 
    cmd = sys.argv[1]
    if cmd in commands:
        try:
            commands[cmd](sys.argv[2:])
        except Exception as e:
            print(f"gitlite {cmd}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)
 
if __name__ == "__main__":
    main()