import sys
from .commands.base import cmd_init, cmd_cat_file, cmd_hash_object
from .commands.commit import cmd_write_tree, cmd_commit
from .commands.inspect import cmd_log, cmd_ls_tree
from .commands.checkout import cmd_checkout
from .commands.branch import cmd_branch
from .commands.tag import cmd_tag
from .commands.config import cmd_config
from .commands.diff import cmd_diff
 
commands = {
    "init": cmd_init,
    "cat-file": cmd_cat_file,
    "hash-object": cmd_hash_object,
    "write-tree": cmd_write_tree,
    "commit": cmd_commit,
    "log": cmd_log,
    "ls-tree": cmd_ls_tree,
    "checkout": cmd_checkout,
    "branch": cmd_branch,
    "tag": cmd_tag,
    "config": cmd_config,
    "diff": cmd_diff
}
 
def main():
    if len(sys.argv) < 2:
        print("usage: gitlite <command> [<args>]")
        sys.exit(1)
 
    cmd = sys.argv[1]
    if cmd in commands:
        try:
            commands[cmd](sys.argv[2:])
        except Exception as e:
            print(f"gitlite {cmd}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)
 
if __name__ == "__main__":
    main()