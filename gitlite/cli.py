import sys
from pathlib import Path
from .repo import GitRepository, repo_find, resolve_ref
from .storage import object_read, object_write
from .objects.blob import GitBlob
from .objects.commit import GitCommit
from .checkout import checkout_tree
from .staging import write_tree_recursive
import time
 
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

def cmd_write_tree(args):
    if args:
        print("usage: gitlite write-tree")
        sys.exit(1)
    repo = repo_find()
    sha = write_tree_recursive(repo, repo.worktree)
    print(sha)

def cmd_commit(args):
    repo = repo_find()
    
    message = "No message"
    if len(args) >= 2 and args[0] == "-m":
        message = args[1]
    else:
        print("usage: gitlite commit -m <message>")
        sys.exit(1)
        
    tree_sha = write_tree_recursive(repo, repo.worktree)
    
    parent = resolve_ref(repo, "HEAD")
    parents = []
    
    # Check if parent resolves to a valid object (i.e., not unborn)
    if object_read(repo, parent):
        parents.append(parent)
    
    # Create Commit
    # TODO: Simple hardcoded author to be changed later
    author = "User <user@example.com>"
    timestamp = int(time.time())
    timezone = "+0530"
    author_str = f"{author} {timestamp} {timezone}"
    
    commit = GitCommit()
    commit.kvlm = {
        b'tree': tree_sha.encode(),
        b'parent': [p.encode() for p in parents],
        b'author': author_str.encode(),
        b'committer': author_str.encode(),
        None: message.encode() + b'\n'
    }
    
    commit_sha = object_write(commit, repo)
    
    # Update HEAD
    with open(repo.gitdir / "HEAD", "r") as f:
        head_data = f.read().strip()
        
    if head_data.startswith("ref: "):
        # Update the branch ref
        ref_path = repo.gitdir / head_data[5:]
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ref_path, "w") as f:
            f.write(commit_sha + "\n")
        print(f"[{head_data[5:]} {commit_sha}] {message}")
    else:
        # Detached HEAD
        with open(repo.gitdir / "HEAD", "w") as f:
            f.write(commit_sha + "\n")
        print(f"[detached HEAD {commit_sha}] {message}")
 
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
            # If we reached an unborn branch or bad ref
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

def cmd_checkout(args):
    repo = repo_find()
    
    if len(args) < 1:
        print("usage: gitlite checkout <commit>")
        sys.exit(1)
        
    target = args[0]
    sha = resolve_ref(repo, target)
    
    obj = object_read(repo, sha)
    if not obj:
        print(f"fatal: reference {target} not found")
        sys.exit(128)
        
    # If it's a commit, get the tree
    if obj.fmt == b'commit':
        tree_sha = obj.kvlm[b'tree'].decode()
        obj = object_read(repo, tree_sha)
        
    if obj.fmt != b'tree':
        print(f"fatal: {target} does not point to a tree or commit")
        sys.exit(128)
        
    # Restore files
    checkout_tree(repo, obj, repo.worktree)
    
    # Update HEAD
    ref_path = repo.gitdir / "refs" / "heads" / target
    head_path = repo.gitdir / "HEAD"
    
    if ref_path.exists():
        with open(head_path, "w") as f:
            f.write(f"ref: refs/heads/{target}\n")
        print(f"Switched to branch '{target}'")
    else:
        with open(head_path, "w") as f:
            f.write(sha + "\n")
        print(f"Note: checking out '{sha}'.")
        print("You are in 'detached HEAD' state.")

commands = {
    "init": cmd_init,
    "cat-file": cmd_cat_file,
    "hash-object": cmd_hash_object,
    "write-tree": cmd_write_tree,
    "commit": cmd_commit,
    "log": cmd_log,
    "ls-tree": cmd_ls_tree,
    "checkout": cmd_checkout
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