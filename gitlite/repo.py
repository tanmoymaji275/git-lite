from pathlib import Path

class GitRepository:

    def __init__(self, path: Path, force: bool = False):
        self.worktree = path
        self.gitdir = path / ".git"
 
        if not force and not self.gitdir.is_dir():
            raise Exception(f"Not a Git repository {path}")
 
    def init(self):
        self.worktree.mkdir(parents=True, exist_ok=True)
        self.gitdir.mkdir(parents=True, exist_ok=True)
 
        # Create subdirectories
        for dir_name in ["branches", "objects", "refs/tags", "refs/heads"]:
            (self.gitdir / dir_name).mkdir(parents=True, exist_ok=True)
 
        # Create HEAD file
        with open(self.gitdir / "HEAD", "w") as f:
            f.write("ref: refs/heads/master\n")
 
        return self

def repo_find(path: Path = Path("."), required: bool = True):
    path = path.resolve()
    if (path / ".git").is_dir():
        return GitRepository(path)
 
    parent = path.parent
    if parent == path:
        if required:
            raise Exception("No git directory.")
        return None
    return repo_find(parent, required)

def resolve_ref(repo, ref, depth=0):
    """Resolves a reference (HEAD, branch, or SHA) to a SHA-1 hash."""
    if depth > 10:
        raise ValueError(f"Too many symbolic links resolving {ref}")

    # If it looks like a SHA already, return it
    if len(ref) == 40 and all(c in '0123456789abcdef' for c in ref.lower()):
        return ref

    path = repo.gitdir / ref

    if not path.is_file():
        # Try with refs/heads/ prefix if not found
        if not ref.startswith("refs/"):
            alt_path = repo.gitdir / "refs" / "heads" / ref
            if alt_path.is_file():
                path = alt_path
            else:
                return ref
        else:
            return ref

    try:
        with open(path, "r") as f:
            data = f.read().strip()
    except IOError as e:
        raise ValueError(f"Cannot read ref {ref}: {e}")

    if data.startswith("ref: "):
        return resolve_ref(repo, data[5:], depth + 1)

    return data