#!/usr/bin/env python3
import subprocess
import os

os.chdir(r'C:\Users\rcmrejection3\nphies-rcm')
subprocess.call(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'integrate.ps1'])
os.chdir(r'C:\Users\rcmrejection3\nphies-rcm\GIVC')
subprocess.call(['git', 'remote', 'remove', 'origin'], stderr=subprocess.DEVNULL)
subprocess.call(['git', 'remote', 'add', 'origin', 'https://github.com/fadil369/GIVC.git'])
subprocess.call(['git', 'add', '-A'])
subprocess.call(['git', 'commit', '-m', 'Unified GIVC platform - integrated all features'])
subprocess.call(['git', 'pull', 'origin', 'main', '--rebase'])
subprocess.call(['git', 'push', '-u', 'origin', 'main'])
print("\nDone! Check output above for any errors.")
