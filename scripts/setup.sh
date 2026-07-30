#!/bin/bash
# corch-skills setup — install all skills and dependencies
set -e
REPO="fanzy531/corch-skills"
INSTALLER="$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py"

echo "=== corch-skills setup ==="
python3 -c "
import json
d=json.load(open('.skill-requirements.json'))
for s in d['skills']:
    n=s['name']; p=s['path']
    print(f'Installing {n}...')
    import subprocess
    for dest in ['$HOME/.agents/skills', '$HOME/.codex/skills']:
        subprocess.run(['rm', '-rf', f'{dest}/{n}'], capture_output=True)
        r=subprocess.run(['python3', '$INSTALLER', '--repo', '$REPO', '--path', p, '--dest', dest, '--name', n], capture_output=True, text=True)
        status='ok' if r.returncode==0 else 'fail'
        print(f'  {dest.split("/")[-1]}: {status}')
"
pip3 install Pillow 2>/dev/null && echo "Pillow ok" || true
echo "=== Done ==="
