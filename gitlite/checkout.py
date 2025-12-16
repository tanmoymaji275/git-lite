from .storage import object_read
 
def checkout_tree(repo, tree, path):
    """Restore the working tree from a Tree object."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    for item in tree.items:
        item_name = item['path'].decode()

        # Security: Validate path doesn't escape worktree
        if '..' in item_name or item_name.startswith('/') or item_name.startswith('\\'):
            raise ValueError(f"Invalid path in tree object: {item_name}")

        item_path = path / item_name

        # Double-check resolved path is within worktree
        try:
            item_path.resolve().relative_to(repo.worktree.resolve())
        except ValueError:
            raise ValueError(f"Path attempts to escape repository: {item_name}")

        sha = item['sha']
        
        obj = object_read(repo, sha)
        
        if obj.fmt == b'tree':
            checkout_tree(repo, obj, item_path)
        elif obj.fmt == b'blob':
            item_path.parent.mkdir(parents=True, exist_ok=True)
            with open(item_path, "wb") as f:
                f.write(obj.blobdata)