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

def resolve_ref(repo, ref):
    """
    Resolves a reference to a SHA-1 hash.
    Example: HEAD -> refs/heads/master -> <SHA>
    If the ref is already a SHA (doesn't exist as a file), returns it as is.
    """
    path = repo.gitdir / ref

    if not path.is_file():
        return ref

    with open(path, "r") as f:
        data = f.read().strip()

    if data.startswith("ref: "):
        return resolve_ref(repo, data[5:])
    
    return data