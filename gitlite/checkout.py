from .storage import object_read
 
def checkout_tree(repo, tree, path):
    """Restore the working tree from a Tree object."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    for item in tree.items:
        item_path = path / item['path'].decode()
        sha = item['sha']
        
        obj = object_read(repo, sha)
        
        if obj.fmt == b'tree':
            checkout_tree(repo, obj, item_path)
        elif obj.fmt == b'blob':
            with open(item_path, "wb") as f:
                f.write(obj.blobdata)