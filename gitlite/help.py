OVERVIEW = """
usage: gitlite <command> [<args>]

gitlite is a minimal implementation of the git version control system.

These are common Git commands used in various situations:

start a working area (see also: gitlite help tutorial)
   init       Create an empty Git repository or reinitialize an existing one

work on the current change (see also: gitlite help everyday)
   diff       Show changes between commits, commit and working tree, etc
   status     Show the working tree status (Not implemented)

examine the history and state (see also: gitlite help revisions)
   log        Show commit logs
   cat-file   Provide content of repository objects
   ls-tree    List the contents of a tree object

grow, mark and tweak your common history
   branch     List, create, or delete branches
   checkout   Switch branches or restore working tree files
   commit     Record changes to the repository
   tag        Create, list, delete or verify a tag object signed with GPG

collaborate (see also: gitlite help workflows)
   config     Get and set repository or global options

'gitlite help -a' and 'gitlite help -g' list available subcommands and some
concept guides. See 'gitlite help <command>' or 'gitlite help <concept>'
to read about a specific subcommand or concept.
"""

HELP_INIT = """
gitlite-init - Create an empty Git repository or reinitialize an existing one

SYNOPSIS
    gitlite init [directory]

DESCRIPTION
    This command creates an empty Git repository - basically a .git directory with subdirectories for objects, refs/heads, refs/tags, and template files. An initial HEAD file that references the HEAD of the master branch is also created.

    If the directory does not exist, it will be created.
"""

HELP_COMMIT = """
gitlite-commit - Record changes to the repository

SYNOPSIS
    gitlite commit -m <msg>

DESCRIPTION
    Stores the current contents of the index in a new commit along with a log message from the user describing the changes.

    Note: In gitlite, this command acts like 'git commit -a', automatically snapshotting all tracked files in the current directory (respecting .gitignore).

OPTIONS
    -m <msg>
        Use the given <msg> as the commit message.
"""

HELP_CHECKOUT = """
gitlite-checkout - Switch branches or restore working tree files

SYNOPSIS
    gitlite checkout <commit>

DESCRIPTION
    Updates files in the working tree to match the version in the index or the specified tree. If no paths are given, git checkout will also update HEAD to set the specified branch as the current branch.

    If <commit> is a branch name, checking it out switches to that branch.
    If <commit> is a SHA-1 hash, checking it out puts the repository in a 'detached HEAD' state.
"""

HELP_LOG = """
gitlite-log - Show commit logs

SYNOPSIS
    gitlite log [<revision range>]

DESCRIPTION
    Shows the commit logs.

    The command takes options applicable to the git rev-list command to control what is shown and how, and options applicable to the git diff-* commands to control how the changes each commit introduces are shown.
"""

HELP_DIFF = """
gitlite-diff - Show changes between commits, commit and working tree, etc

SYNOPSIS
    gitlite diff [<commit>]

DESCRIPTION
    Show changes between the working tree and the index or a tree, changes between the index and a tree, changes between two trees, changes resulting from a merge, changes between two blob objects, or changes between two files on disk.

    gitlite diff
        Changes between the working tree and the index.

    gitlite diff <commit>
        Changes between the working tree and the named <commit>.
"""

HELP_BRANCH = """
gitlite-branch - List, create, or delete branches

SYNOPSIS
    gitlite branch
    gitlite branch <branchname> [<start-point>]

DESCRIPTION
    If --list is given, or if there are no non-option arguments, existing branches are listed; the current branch will be highlighted with an asterisk.

    The command's second form creates a new branch head named <branchname> which points to the current HEAD, or <start-point> if given.
"""

HELP_TAG = """
gitlite-tag - Create, list, delete or verify a tag object

SYNOPSIS
    gitlite tag
    gitlite tag [-a] [-m <msg>] <tagname> [<commit>]

DESCRIPTION
    Add a tag reference in refs/tags/

    Unless -f is given, the named tag must not yet exist.

    If one of -a, -s, or -u <keyid> is passed, the command creates a tag object, and requires a tag message. Unless -m <msg> or -F <file> is given, an editor is started for the user to type the tag message.

OPTIONS
    -a
        Make an unsigned, annotated tag object; replace <tagname> with a checksum.

    -m <msg>
        Use the given tag message (instead of prompting).
"""

HELP_CONFIG = """
gitlite-config - Get and set repository or global options

SYNOPSIS
    gitlite config <name> [<value>]
    gitlite config --list

DESCRIPTION
    You can query/set/replace/unset options with this command. The name is actually the section and the key separated by a dot, and the value will be escaped.

    gitlite config user.name "John Doe"
    gitlite config user.email john@doe.com
"""

HELP_CAT_FILE = """
gitlite-cat-file - Provide content of repository objects

SYNOPSIS
    gitlite cat-file <type> <object>

DESCRIPTION
    In its first form, the command provides the content or the type of an object in the repository. The type is required (blob, tree, commit, tag).
"""

HELP_HASH_OBJECT = """
gitlite-hash-object - Compute object ID and optionally create a blob from a file

SYNOPSIS
    gitlite hash-object [-w] <file>

DESCRIPTION
    Computes the object ID value for an object with specified type with the contents of the named file (which can be outside of the work tree), and optionally writes the resulting object into the object database.

OPTIONS
    -w
        Actually write the object into the object database.
"""

HELP_LS_TREE = """
gitlite-ls-tree - List the contents of a tree object

SYNOPSIS
    gitlite ls-tree <tree-ish>

DESCRIPTION
    Lists the contents of a given tree object, like what "ls -a" does in the current working directory.
"""

HELP_WRITE_TREE = """
gitlite-write-tree - Create a tree object from the current directory

SYNOPSIS
    gitlite write-tree

DESCRIPTION
    Creates a tree object using the current directory content.
    The index is not used in gitlite; this command scans the directory directly.
"""

DETAILS = {
    "init": HELP_INIT,
    "commit": HELP_COMMIT,
    "checkout": HELP_CHECKOUT,
    "log": HELP_LOG,
    "diff": HELP_DIFF,
    "branch": HELP_BRANCH,
    "tag": HELP_TAG,
    "config": HELP_CONFIG,
    "cat-file": HELP_CAT_FILE,
    "hash-object": HELP_HASH_OBJECT,
    "ls-tree": HELP_LS_TREE,
    "write-tree": HELP_WRITE_TREE
}

def show_help(cmd=None):
    if cmd and cmd in DETAILS:
        print(DETAILS[cmd])
    else:
        print(OVERVIEW)
