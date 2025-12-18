import sys
from ..repo import repo_find, resolve_ref
from ..storage import object_read
from ..diff import diff_trees
 
def cmd_diff(args):
    repo = repo_find()
    
    target = "HEAD"
    if args:
        target = args[0]
        
    sha = resolve_ref(repo, target)
    if not sha:
        print(f"fatal: bad object {target}")
        sys.exit(128)
        
    obj = object_read(repo, sha)
    if not obj:
        print(f"fatal: bad object {sha}")
        sys.exit(128)
        
    if obj.fmt == b'commit':
        tree_sha = obj.kvlm[b'tree'].decode()
    elif obj.fmt == b'tree':
        tree_sha = sha
    else:
        print(f"fatal: object {target} is not a tree or commit")
        sys.exit(128)
        
    diff_trees(repo, tree_sha, repo.worktree)