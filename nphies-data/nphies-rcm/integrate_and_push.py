import subprocess
import os
import sys

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the result"""
    print(f"\n[RUNNING] {cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    base_dir = r"C:\Users\rcmrejection3\nphies-rcm"
    givc_dir = os.path.join(base_dir, "GIVC")
    
    print("="*60)
    print("GIVC INTEGRATION AND GIT PUSH")
    print("="*60)
    
    # Step 1: Run integration script
    print("\n[STEP 1] Running integration script...")
    integrate_script = os.path.join(base_dir, "integrate.ps1")
    success = run_command(
        f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{integrate_script}"',
        cwd=base_dir
    )
    
    if not success:
        print("[WARNING] Integration script had issues, continuing...")
    
    # Step 2: Git operations
    print("\n[STEP 2] Configuring git remote...")
    run_command("git remote remove origin", cwd=givc_dir)
    run_command("git remote add origin https://github.com/fadil369/GIVC.git", cwd=givc_dir)
    run_command("git remote -v", cwd=givc_dir)
    
    # Step 3: Stage changes
    print("\n[STEP 3] Staging all changes...")
    run_command("git add -A", cwd=givc_dir)
    
    # Step 4: Show status
    print("\n[STEP 4] Git status:")
    run_command("git status --short", cwd=givc_dir)
    
    # Step 5: Commit
    print("\n[STEP 5] Committing changes...")
    commit_msg = (
        "Unified GIVC platform with integrated features\\n\\n"
        "Merged best components from nphies-rcm, brainsait-nphies-givc, and brainsait-rcm:\\n"
        "- Enhanced Python backend with NPHIES integration\\n"
        "- AI fraud detection and predictive analytics\\n"
        "- Monorepo structure (apps/packages)\\n"
        "- OASIS automation templates\\n"
        "- Certificates and configuration\\n"
        "- Infrastructure and documentation"
    )
    run_command(f'git commit -m "{commit_msg}"', cwd=givc_dir)
    
    # Step 6: Pull with rebase
    print("\n[STEP 6] Syncing with remote...")
    if not run_command("git pull origin main --rebase", cwd=givc_dir):
        print("[INFO] Trying master branch...")
        run_command("git pull origin master --rebase", cwd=givc_dir)
    
    # Step 7: Push
    print("\n[STEP 7] Pushing to GitHub...")
    if run_command("git push -u origin main", cwd=givc_dir):
        print("\n" + "="*60)
        print("SUCCESS! Pushed to https://github.com/fadil369/GIVC")
        print("="*60)
    elif run_command("git push -u origin master", cwd=givc_dir):
        print("\n" + "="*60)
        print("SUCCESS! Pushed to https://github.com/fadil369/GIVC (master)")
        print("="*60)
    else:
        print("\n[WARNING] Push failed. You may need to:")
        print("  1. Set up authentication (git credential manager)")
        print("  2. Or force push: git push -u origin main --force")
        print("  3. Or create the repository on GitHub first")

if __name__ == "__main__":
    main()
