#!/usr/bin/env python3
"""
corch-skills 安装器 — 跨平台（macOS / Windows / Linux）
"""

import json, os, subprocess, sys, platform
from pathlib import Path

REPO = "fanzy531/corch-skills"
HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent
REQUIREMENTS = ROOT / ".skill-requirements.json"
INSTALLER = Path.home() / ".codex" / "skills" / ".system" / "skill-installer" / "scripts" / "install-skill-from-github.py"


def run(cmd, check=False):
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def install_skills(req, dest_dir):
    """安装所有可安装的 skill"""
    for s in req.get("skills", []):
        name = s["name"]
        path = s["path"]
        print(f"\n  → {name}")
        subprocess.run(["rm", "-rf", str(dest_dir / name)], capture_output=True)
        if INSTALLER.exists():
            run([sys.executable, str(INSTALLER), "--repo", REPO, "--path", path,
                 "--dest", str(dest_dir), "--name", name])
        else:
            print(f"    安装器未找到: {INSTALLER}")
            print(f"    手动安装: codex skill install fanzy531/corch-skills --path {path}")


def main():
    if not REQUIREMENTS.exists():
        print(f"✗ {REQUIREMENTS} 未找到")
        sys.exit(1)

    req = json.loads(REQUIREMENTS.read_text())
    system = platform.system()
    
    print(f"=== corch-skills 安装器 ===")
    print(f"系统: {system}")
    print()

    # 安装 skill
    for dest_name, dest_path in [("agent", Path.home() / ".agents" / "skills"),
                                   ("codex", Path.home() / ".codex" / "skills")]:
        print(f"--- 安装到 {dest_name} ---")
        install_skills(req, dest_path)
        print()

    # pip 依赖
    for pkg in req.get("dependencies", {}).get("pip", []):
        print(f"pip install {pkg}")
        run([sys.executable, "-m", "pip", "install", pkg])

    # 系统依赖
    sys_deps = req.get("dependencies", {}).get("system", {}).get(system, {})
    for mgr, pkgs in sys_deps.items():
        for pkg in pkgs:
            print(f"系统包: {pkg} ({mgr})")
            if system == "Darwin":
                run(["brew", "install", pkg])
            elif system == "Windows":
                run([mgr, "install", pkg, "-y"])
            elif system == "Linux":
                run(["sudo", "apt-get", "install", "-y", pkg])

    # 推荐 skill（需要手动启用）
    recommended = req.get("recommended", [])
    if recommended:
        print("\n=== 推荐 skill（Corch 内置，无需安装）===")
        print("以下能力是 Corch 系统内置的，在对话中直接使用即可：")
        for s in recommended:
            print(f"  • {s['name']} — {s['description']}")

    print("\n=== 安装完成 ===")
    print(f"已安装 {len(req['skills'])} 个 skill")
    if recommended:
        print(f"{len(recommended)} 个推荐能力可用（Corch 内置）")
    print("重启 Codex 后生效。")


if __name__ == "__main__":
    main()
