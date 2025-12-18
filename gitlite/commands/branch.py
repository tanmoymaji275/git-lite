import sys
import os
from ..repo import repo_find, resolve_ref

def cmd_branch(args):
    repo = repo_find()
    
    if not args or args[0] == "--list":
        # List branches
        heads_dir = repo.gitdir / "refs" / "heads"
        if not heads_dir.exists():
            return

        # Get current branch
        current = None
        with open(repo.gitdir / "HEAD", "r") as f:
            head_content = f.read().strip()
            if head_content.startswith("ref: refs/heads/"):
                current = head_content[16:]
        
        branches = sorted(os.listdir(heads_dir))
        for branch in branches:
            prefix = "*" if branch == current else " "
            print(f"{prefix} {branch}")
            
    else:
        # Create branch
        # noinspection DuplicatedCode
        name = args[0]
        start_point = args[1] if len(args) > 1 else "HEAD"
        
        sha = resolve_ref(repo, start_point)
        if not sha:
            print(f"fatal: Not a valid object name: '{start_point}'.", file=sys.stderr)
            sys.exit(128)
            
        # Create the ref
        ref_path = repo.gitdir / "refs" / "heads" / name
        
        if ref_path.exists():
            print(f"fatal: A branch named '{name}' already exists.", file=sys.stderr)
            sys.exit(128)
            
        with open(ref_path, "w") as f:
            f.write(sha + "\n")
