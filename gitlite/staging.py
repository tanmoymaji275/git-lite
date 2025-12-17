import os
from pathlib import Path
from .objects.blob import GitBlob
from .objects.tree import GitTree
from .storage import object_write
 
def write_tree_recursive(repo, path):
    items = []
    
    # Iterate over directory entries. Sorted order ensures deterministic Tree SHAs.
    entries = sorted(os.scandir(path), key=lambda e: e.name)
    
    for entry in entries:
        if entry.name == '.git':
            continue
            
        full_path = Path(entry.path)
        
        if entry.is_file():
            with open(full_path, 'rb') as f:
                data = f.read()
            blob = GitBlob(data)
            sha = object_write(blob, repo)
            
            # Mode: 100644 (regular)
            # On Windows, os.access(X_OK) often returns true for everything or relies on file extensions (.exe), making it unreliable for mimicking Git's exact behavior without complex logic.
            mode = b'100644'
            
            items.append({
                'mode': mode,
                'path': entry.name.encode(),
                'sha': sha
            })
            
        elif entry.is_dir():
            sha = write_tree_recursive(repo, full_path)
            items.append({
                'mode': b'40000', 
                'path': entry.name.encode(),
                'sha': sha
            })
            
    tree = GitTree()
    tree.items = items
    return object_write(tree, repo)