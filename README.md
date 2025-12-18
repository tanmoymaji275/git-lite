# git-lite

**git-lite** is a minimal, educational reimplementation of Git written in **Python 3**.  
It models Git’s internal data structures and on-disk formats, including content-addressable objects, trees, commits, refs, tags, diffs, and packfiles, exposed through a small but functional command-line interface.

---

## Features

### Core Git Object Model
- Pure-Python Git objects implemented from scratch:
  - **Blob** – raw file contents
  - **Tree** – directory structure snapshots
  - **Commit** – tree pointers, parents, author/committer metadata, messages
  - **Tag** – lightweight and annotated tags as first-class Git objects
- Shared **KVLM (Key-Value List Message)** parser/serializer for Commit and Tag objects.

### Object Database & Storage
- Content-addressable storage using **SHA-1** hashes.
- Loose object support:
  - Objects stored in `.git/objects/XX/YYYY` format, compressed like Git.
- Packfile support:
  - Reads Git **packfiles (v2)** via `.pack` and `.idx`.
  - Supports **OFS_DELTA** and **REF_DELTA** resolution.
  - Robust delta application with bounds and consistency checks.
- Fully compatible `.git` directory layout usable alongside official Git tooling.

### Command-Line Interface
- Git-style CLI exposed via the `gitlite` command.
- Modular command architecture under `gitlite/commands/`.
- Built-in help system:
  - `gitlite --help`
  - `gitlite help <command>`
  - `gitlite <command> --help`

### Implemented Git Commands
- **Repository & config**
  - `init` – initialize a repository
  - `config` – get/set local configuration (`user.name`, `user.email`)
- **Low-level plumbing**
  - `hash-object` – compute SHA-1 of file contents and optionally write blobs
  - `write-tree` – snapshot the working directory into a tree object
- **History & inspection**
  - `commit` – snapshot the working tree and create commits (similar to `git commit -a`)
  - `log` – traverse and display commit history (including merge parents)
  - `ls-tree` – list contents of tree objects
  - `cat-file` – inspect raw object contents
- **Branching & navigation**
  - `branch` – list and create branches
  - `checkout` – update the working tree to a commit or branch, including detached HEAD
  - `tag` – create and list lightweight and annotated tags
- **Diff**
  - `diff` – unified diffs between working tree and HEAD or between commits
  - Detects and reports binary file differences

### Working Tree & Ignore Rules
- **`.gitignore` support** – ignored files are excluded from tree creation and commits.
- Safe checkout with path traversal protection.

### Developer Experience & Robustness
- No external dependencies; uses only the Python standard library.
- Cross-platform support, including Windows-specific file mode handling.
- Defensive error handling for malformed objects, missing refs, and corrupt packfiles.

### Testing
- Unit and integration tests using `pytest`.
- Covers object storage, packfiles, diffs, config handling, and workflows.

---

## Installation

### Clone the repository
```bash
git clone https://github.com/tanmoymaji275/git-lite.git
cd git-lite
```

### (Optional) Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install in editable mode
```bash
pip install -e .
```

This installs the `gitlite` CLI entrypoint defined in `pyproject.toml`.

---

## Usage

### Initialize a repository
```bash
mkdir demo-repo
cd demo-repo
gitlite init
```

### Create a commit
```bash
echo "hello gitlite" > hello.txt
gitlite commit -m "Initial commit"
```

### Inspect history and trees
```bash
gitlite log
gitlite ls-tree HEAD
```

### Branching and checkout
```bash
gitlite branch feature-x
gitlite checkout feature-x

echo "feature work" >> hello.txt
gitlite commit -m "Add feature"
gitlite log
```

### Tags and diffs
```bash
gitlite tag v0.1
gitlite diff HEAD~1 HEAD
```

### Help
```bash
gitlite help
gitlite help commit
```

---

## Architecture

- `gitlite/cli.py` – CLI entrypoint and argument parsing
- `gitlite/repo.py` – Repository abstraction and ref resolution
- `gitlite/commands/` – User-facing subcommands
- `gitlite/objects/` – Blob, Tree, Commit, Tag implementations
- `gitlite/pack/` – Pack-file and delta parsing
- Supporting modules:
  - `storage.py`
  - `staging.py`
  - `diff.py`
  - `config.py`
  - `utils.py`
- `tests/` – Unit and integration tests

---

## Development

Run the test suite:
```bash
pytest
```

---

## Scope & Limitations

- Focuses on Git internals, not full Git feature parity
- Networking commands (`clone`, `fetch`, `push`) are out of scope
- Intended for learning, experimentation, and code reading

---

## Motivation

Built to explore Git’s internal design, including on-disk storage, reference resolution,
commit history, and packfile/delta mechanics. Intended as a systems/tooling project
for learning and interview discussion.
