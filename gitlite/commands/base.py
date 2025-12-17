import sys
from pathlib import Path
from ..repo import GitRepository, repo_find
from ..storage import object_read, object_write
from ..objects.blob import GitBlob

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