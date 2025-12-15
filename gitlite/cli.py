import sys
from pathlib import Path
from .repo import GitRepository
 
def main():
    if len(sys.argv) < 2:
        print("usage: gitlite init [path]")
        sys.exit(1)
 
    if sys.argv[1] != "init":
        print(f"unknown command: {sys.argv[1]}")
        sys.exit(1)
 
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
 
    try:
        repo = GitRepository(target, force=True)
        repo.init()
        print(f"Initialized empty Git repository in {repo.gitdir}")
    except Exception as e:
        print(f"gitlite init: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()