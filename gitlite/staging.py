import os
import fnmatch
from pathlib import Path
from .objects.blob import GitBlob
from .objects.tree import GitTree
from .storage import object_write

def read_gitignore(path):
    rules = []
    ignore_path = path / ".gitignore"
    if ignore_path.exists():
        with open(ignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                rules.append(line)
    return rules
 
def is_ignored(path, rules):
    name = path.name
    for rule in rules:
        if fnmatch.fnmatch(name, rule):
            return True
        # Handle directory specific patterns
        if rule.endswith("/") and path.is_dir():
             if fnmatch.fnmatch(name + "/", rule):
                 return True
    return False
 
def write_tree_recursive(repo, path, rules=None):
    if rules is None:
        rules = read_gitignore(repo.worktree)
        # Always ignore .git
        rules.append(".git")
 
    items = []
    
    # Iterate over directory entries. Sorted order ensures deterministic Tree SHAs.
    entries = sorted(os.scandir(path), key=lambda e: e.name)
    
    for entry in entries:
        full_path = Path(entry.path)
        
        if is_ignored(full_path, rules):
            continue
            
        if entry.is_file():
            with open(full_path, 'rb') as f:
                data = f.read()
            blob = GitBlob(data)
            sha = object_write(blob, repo)
            
            # Mode: 100644 (regular)
            # On Windows, os.access(X_OK) often returns true for everything or relies on file extensions (.exe),
            # making it unreliable for mimicking Git's exact behavior without complex logic.
            mode = b'100644'
            
            items.append({
                'mode': mode,
                'path': entry.name.encode(),
                'sha': sha
            })
            
        elif entry.is_dir():
            sha = write_tree_recursive(repo, full_path, rules)
            items.append({
                'mode': b'40000', 
                'path': entry.name.encode(),
                'sha': sha
            })
            
    tree = GitTree()
    tree.items = items
    return object_write(tree, repo)