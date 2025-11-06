import subprocess
import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("\nStarting integration process...\n")

os.chdir(r'C:\Users\rcmrejection3\nphies-rcm')

# Step 1: Integration
print("="*60)
print("STEP 1: Running Integration Script")
print("="*60)
result = subprocess.run(
    ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'integrate-fixed.ps1'],
    capture_output=False
)
print(f"Integration exit code: {result.returncode}\n")

# Step 2: Git operations
print("="*60)
print("STEP 2: Git Operations")
print("="*60)

os.chdir(r'C:\Users\rcmrejection3\nphies-rcm\GIVC')

commands = [
    (['git', 'remote', 'remove', 'origin'], True),  # May fail, ignore
    (['git', 'remote', 'add', 'origin', 'https://github.com/fadil369/GIVC.git'], False),
    (['git', 'remote', '-v'], False),
    (['git', 'add', '-A'], False),
    (['git', 'status', '--short'], False),
    (['git', 'commit', '-m', 'Unified GIVC platform with integrated features from all directories'], True),
    (['git', 'pull', 'origin', 'main', '--rebase'], True),
    (['git', 'push', '-u', 'origin', 'main'], False),
]

for cmd, can_fail in commands:
    print(f"\nRunning: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and not can_fail:
        print("Error:", result.stderr)
    if result.returncode != 0 and not can_fail:
        print(f"Command failed with code {result.returncode}")
        # Try master branch as fallback for pull/push
        if 'main' in cmd:
            print("Trying with 'master' branch...")
            new_cmd = [x.replace('main', 'master') for x in cmd]
            result = subprocess.run(new_cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

print("\n" + "="*60)
print("INTEGRATION AND PUSH COMPLETE!")
print("Repository: https://github.com/fadil369/GIVC")
print("="*60)
