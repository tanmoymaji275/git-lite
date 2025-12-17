import sys
import os
from ..repo import repo_find, resolve_ref

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
            
    else:
        # Create tag
        # noinspection DuplicatedCode
        name = args[0]
        start_point = args[1] if len(args) > 1 else "HEAD"
        
        sha = resolve_ref(repo, start_point)
        if not sha:
            print(f"fatal: Not a valid object name: '{start_point}'.", file=sys.stderr)
            sys.exit(128)
            
        # Create the ref
        ref_path = repo.gitdir / "refs" / "tags" / name
        
        if ref_path.exists():
            print(f"fatal: tag '{name}' already exists", file=sys.stderr)
            sys.exit(128)
            
        # Ensure directory exists
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(ref_path, "w") as f:
            f.write(sha + "\n")