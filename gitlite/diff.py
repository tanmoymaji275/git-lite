import difflib
import os
import sys
from pathlib import Path
from .storage import object_read
from .staging import is_ignored, read_gitignore
 
def is_binary(data):
    return b'\0' in data[:8000]
 
def diff_blobs(path, old_data, new_data):
    if is_binary(old_data) or is_binary(new_data):
        if old_data != new_data:
            print(f"Binary files {path} differ")
        return
 
    try:
        old_str = old_data.decode('utf-8').splitlines(keepends=True)
        new_str = new_data.decode('utf-8').splitlines(keepends=True)
    except UnicodeDecodeError:
        print(f"Binary files {path} differ (encoding)")
        return
 
    diff = difflib.unified_diff(
        old_str, new_str,
        fromfile=f"a/{path}",
        tofile=f"b/{path}"
    )
    
    for line in diff:
        sys.stdout.write(line)
 
def diff_trees(repo, tree_sha, work_path, relative_prefix=""):
    tree_obj = object_read(repo, tree_sha)
    if not tree_obj or tree_obj.fmt != b'tree':
        return
 
    # Build map of tree entries {name: item}
    tree_entries = {item['path'].decode(): item for item in tree_obj.items}
    
    rules = read_gitignore(work_path)
    rules.append(".git")
 
    for entry in os.scandir(work_path):
        name = entry.name
        path = Path(entry.path)
        display_path = os.path.join(relative_prefix, name)
        
        if is_ignored(path, rules):
            continue
            
        if name in tree_entries:
            tree_item = tree_entries[name]
            
            if entry.is_file():
                blob_obj = object_read(repo, tree_item['sha'])
                if not blob_obj: continue
                
                with open(path, "rb") as f:
                    file_data = f.read()
                
                if blob_obj.blobdata != file_data:
                    diff_blobs(display_path, blob_obj.blobdata, file_data)
                    
            elif entry.is_dir():
                # Recurse
                mode = tree_item['mode']
                if mode.startswith(b'04') or mode == b'40000':
                    diff_trees(repo, tree_item['sha'], path, display_path)
            
            del tree_entries[name] # Mark as processed
        else:
            # Untracked file (ignored in diff)
            pass
 
    # Remaining tree_entries are DELETED files
    for name, item in tree_entries.items():
        display_path = os.path.join(relative_prefix, name)
        print(f"deleted: {display_path}")
        # To show full diff:
        # blob_obj = object_read(repo, item['sha'])
        # diff_blobs(display_path, blob_obj.blobdata, b"")