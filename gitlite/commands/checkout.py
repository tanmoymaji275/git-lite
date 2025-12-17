import sys
from ..repo import repo_find, resolve_ref
from ..storage import object_read
from ..checkout import checkout_tree
 
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
