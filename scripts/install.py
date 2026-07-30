#!/usr/bin/env python3
"""
corch-skills installer — cross-platform (macOS / Windows / Linux)
Reads .skill-requirements.json and installs:
  - Codex skills (via install-skill-from-github.py)
  - pip packages (Pillow)
  - System packages (brew / choco / apt)
"""

import json, os, subprocess, sys, platform
from pathlib import Path

REPO = "fanzy531/corch-skills"
HERE = Path(__file__).parent.resolve()
REPO_ROOT = HERE.parent
REQUIREMENTS = REPO_ROOT / ".skill-requirements.json"
INSTALLER = Path.home() / ".codex" / "skills" / ".system" / "skill-installer" / "scripts" / "install-skill-from-github.py"


def run(cmd, check=True, capture=False):
    """Run a command and print output."""
    print(f"  $ {' '.join(cmd)}")
    try:
        if capture:
            return subprocess.run(cmd, capture_output=True, text=True, check=check)
        subprocess.run(cmd, check=check)
    except subprocess.CalledProcessError as e:
        print(f"    ⚠ failed (exit {e.returncode}), continuing...")


def install_skills(req, dest):
    """Install all skills from manifest to dest directory."""
    for s in req["skills"]:
        name = s["name"]
        path = s["path"]
        print(f"\n  → {name} ({path})")
        # Remove old
        subprocess.run(["rm", "-rf", str(dest / name)], capture_output=True)
        # Install
        if INSTALLER.exists():
            run(["python3", str(INSTALLER), "--repo", REPO, "--path", path,
                 "--dest", str(dest), "--name", name])
        else:
            print(f"    ⚠ installer not found at {INSTALLER}")
            print(f"    Install via: codex skill install fanzy531/corch-skills --path {path}")


def install_pip(deps):
    """Install pip packages."""
    for pkg in deps:
        print(f"  pip install {pkg}")
        run([sys.executable, "-m", "pip", "install", pkg], check=False)


def install_system(deps):
    """Install system packages — platform-aware."""
    system = platform.system()
    for pkg in deps:
        print(f"  System: {pkg}")
        if system == "Darwin":
            run(["brew", "install", pkg], check=False)
        elif system == "Windows":
            # Try chocolatey first, then winget
            run(["choco", "install", pkg, "-y"], check=False)
        elif system == "Linux":
            run(["sudo", "apt-get", "install", "-y", pkg], check=False)
        else:
            print(f"    ⚠ unknown platform {system}, please install {pkg} manually")


def main():
    if not REQUIREMENTS.exists():
        print(f"✗ {REQUIREMENTS} not found")
        sys.exit(1)

    req = json.loads(REQUIREMENTS.read_text())
    print(f"=== corch-skills installer ===")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Skills to install: {len(req['skills'])}")
    print()

    # Install to both agent and codex
    for dest_name, dest_path in [("agent", Path.home() / ".agents" / "skills"),
                                   ("codex", Path.home() / ".codex" / "skills")]:
        print(f"--- Installing to {dest_name} ---")
        install_skills(req, dest_path)
        print()

    # Pip dependencies
    pip_deps = req.get("dependencies", {}).get("pip", [])
    if pip_deps:
        print("--- Python packages ---")
        install_pip(pip_deps)
        print()

    # System dependencies
    brew_deps = req.get("dependencies", {}).get("brew", [])
    if brew_deps:
        print("--- System packages ---")
        install_system(brew_deps)
        print()

    print("=== Done ===")
    print(f"Installed {len(req['skills'])} skills")
    print()
    print("Restart Codex for changes to take effect.")


if __name__ == "__main__":
    main()
