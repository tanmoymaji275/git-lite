import sys
import os
import time
from ..repo import repo_find, resolve_ref
from ..storage import object_read, object_write
from ..objects.commit import GitCommit
from ..staging import write_tree_recursive

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
        
    # 1. Create Tree
    tree_sha = write_tree_recursive(repo, repo.worktree)
    
    # 2. Get Parent (HEAD)
    parent = resolve_ref(repo, "HEAD")
    parents = []
    
    if object_read(repo, parent):
        parents.append(parent)
    
    # 3. Create Commit
    name = os.environ.get("GIT_AUTHOR_NAME", "Anonymous")
    email = os.environ.get("GIT_AUTHOR_EMAIL", "anonymous@example.com")
    author = f"{name} <{email}>"
    
    timestamp = int(time.time())
    
    offset = -time.timezone if (time.localtime().tm_isdst == 0) else -time.altzone
    offset_hours = offset // 3600
    offset_minutes = (offset % 3600) // 60
    timezone = f"{offset_hours:+03d}{offset_minutes:02d}"
    
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
    
    # 4. Update HEAD
    with open(repo.gitdir / "HEAD", "r") as f:
        head_data = f.read().strip()
        
    if head_data.startswith("ref: "):
        ref_path = repo.gitdir / head_data[5:]
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        with open(ref_path, "w") as f:
            f.write(commit_sha + "\n")
        print(f"[{head_data[5:]} {commit_sha}] {message}")
    else:
        with open(repo.gitdir / "HEAD", "w") as f:
            f.write(commit_sha + "\n")
        print(f"[detached HEAD {commit_sha}] {message}")