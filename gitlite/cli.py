import sys
from .commands.base import cmd_init, cmd_cat_file, cmd_hash_object
from .commands.commit import cmd_write_tree, cmd_commit
from .commands.inspect import cmd_log, cmd_ls_tree
from .commands.checkout import cmd_checkout
from .commands.branch import cmd_branch
from .commands.tag import cmd_tag
from .commands.config import cmd_config
from .commands.diff import cmd_diff
from .help import show_help
 
def cmd_help(args):
    if args:
        command = args[0]
        if command.startswith("-"):
            show_help()
        else:
            show_help(command)
    else:
        show_help()

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
    "diff": cmd_diff,
    "help": cmd_help
}
 
def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ["-h", "--help"]:
        show_help()
        sys.exit(0)
        
    cmd = args[0]
    if cmd in commands:
        if len(args) > 1 and args[1] in ["-h", "--help"]:
             show_help(cmd)
             sys.exit(0)
             
        try:
            commands[cmd](args[1:])
        except Exception as e:
            print(f"gitlite {cmd}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"gitlite: '{cmd}' is not a gitlite command. See 'gitlite --help'.")
        sys.exit(1)
 
if __name__ == "__main__":
    main()