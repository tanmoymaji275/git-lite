import subprocess
import os
import shutil
import sys

REPO_DIR = "test_integration_repo"
PYTHON_EXE = sys.executable
CLI_MODULE = "gitlite.cli"

def run_gitlite(args, cwd=REPO_DIR):
    cmd = [PYTHON_EXE, "-m", CLI_MODULE] + args
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() # Ensure root is in path
    
    # Set author for predictable commits
    env["GIT_AUTHOR_NAME"] = "TestBot"
    env["GIT_AUTHOR_EMAIL"] = "bot@test.com"
    
    result = subprocess.run(
        cmd, 
        cwd=cwd, 
        capture_output=True, 
        text=True, 
        env=env
    )
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    return result

def test_workflow():
    print("--- Starting Integration Test ---")
    
    # Clean up
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)
    
    # 1. Init
    print("[1] Init")
    res = run_gitlite(["init", REPO_DIR], cwd=".")
    assert "Initialized empty Git repository" in res.stdout
    assert os.path.isdir(os.path.join(REPO_DIR, ".git"))

    # 2. Create file
    print("[2] Create File")
    with open(os.path.join(REPO_DIR, "hello.txt"), "w") as f:
        f.write("Version 1")
    
    # 3. Commit 1
    print("[3] Commit 1")
    res = run_gitlite(["commit", "-m", "First Commit"])
    assert "[detached HEAD" in res.stdout or "refs/heads/master" in res.stdout
    commit1_sha = res.stdout.split()[1].strip("[]")
    print(f"    Commit 1 SHA: {commit1_sha}")

    # 4. Modify file
    print("[4] Modify File")
    with open(os.path.join(REPO_DIR, "hello.txt"), "w") as f:
        f.write("Version 2")
        
    # 5. Commit 2
    print("[5] Commit 2")
    res = run_gitlite(["commit", "-m", "Second Commit"])
    commit2_sha = res.stdout.split()[1].strip("[]")
    print(f"    Commit 2 SHA: {commit2_sha}")
    
    # 6. Log
    print("[6] Log")
    res = run_gitlite(["log"])
    assert "First Commit" in res.stdout
    assert "Second Commit" in res.stdout
    assert commit1_sha in res.stdout
    assert commit2_sha in res.stdout
    
    # 7. Verify Content (Version 2)
    with open(os.path.join(REPO_DIR, "hello.txt"), "r") as f:
        content = f.read()
    assert content == "Version 2"
    
    # 8. Checkout Commit 1
    print("[7] Checkout Commit 1")
    run_gitlite(["checkout", commit1_sha])
    
    # 9. Verify Content (Version 1)
    with open(os.path.join(REPO_DIR, "hello.txt"), "r") as f:
        content = f.read()
    if content == "Version 1":
        print("    SUCCESS: File reverted to Version 1")
    else:
        print(f"    FAILURE: File content is '{content}', expected 'Version 1'")
        sys.exit(1)
        
    # Cleanup
    shutil.rmtree(REPO_DIR)
    print("--- Test Passed ---")

if __name__ == "__main__":
    test_workflow()