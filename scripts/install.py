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

AGENT_MD_CANDIDATES = [
    Path.home() / ".agents" / "agent.md",
    Path.home() / ".agents" / "AGENTS.md",
    Path.home() / ".agents" / "CLAUDE.md",
]


def run(cmd, check=False):
    print(f"  $ {' '.join(cmd)}")
    subprocess.run(cmd, check=check)


def install_skill(name, source, path, dest_dir):
    """安装单个 skill，支持本地仓库和外部仓库源"""
    print(f"\n  → {name} (from {source})")
    subprocess.run(["rm", "-rf", str(dest_dir / name)], capture_output=True)

    if INSTALLER.exists():
        if source == REPO:
            run([sys.executable, str(INSTALLER), "--repo", REPO, "--path", path,
                 "--dest", str(dest_dir), "--name", name])
        else:
            run([sys.executable, str(INSTALLER), "--repo", source, "--path", path,
                 "--dest", str(dest_dir), "--name", name])
    else:
        print(f"    安装器未找到: {INSTALLER}")
        print(f"    手动安装: codex skill install {source} --path {path} --name {name}")


def install_skills(req, dest_dir):
    """安装所有可安装的 skill"""
    for s in req.get("skills", []):
        name = s["name"]
        path = s["path"]
        source = s.get("source", REPO)
        install_skill(name, source, path, dest_dir)


def install_tools(req):
    """安装 OptMem 等工具依赖"""
    tools = req.get("dependencies", {}).get("tools", {})
    if not tools:
        return

    for name, info in tools.items():
        print(f"\n  → 安装 {name}: {info.get('description', '')}")
        cmd = info.get("install", "")
        if not cmd:
            continue
        if "curl" in cmd and "|" in cmd:
            print(f"  $ {cmd}")
            subprocess.run(cmd, shell=True, check=False)
        else:
            run(cmd.split())

        if name == "optmem":
            inject_optmem_prompt()


def inject_optmem_prompt():
    """把 OptMem 的 ## Memory 提示词写入 agent.md（如果存在）"""
    memo = Path.home() / ".optmem" / "memo"
    if not memo.exists():
        print("    OptMem 未安装成功，跳过 agent.md 集成")
        return

    try:
        result = subprocess.run([str(memo), "init"], capture_output=True, text=True, timeout=10)
        prompt_block = result.stdout
        if not prompt_block:
            prompt_block = get_fallback_prompt()
    except Exception:
        prompt_block = get_fallback_prompt()

    agent_md = None
    for cand in AGENT_MD_CANDIDATES:
        if cand.exists():
            agent_md = cand
            break

    if not agent_md:
        agent_md = AGENT_MD_CANDIDATES[0]
        agent_md.parent.mkdir(parents=True, exist_ok=True)
        agent_md.touch()

    content = agent_md.read_text()
    if "## Memory" in content:
        print(f"    agent.md 已有 ## Memory 块，跳过")
        return

    new_block = prompt_block.strip() + "\n"
    if content.startswith("# AGENTS.md"):
        marker = "# AGENTS.md — 全局指令\n\n"
        content = marker + new_block + "\n" + content[len(marker):]
    else:
        content = new_block + "\n" + content

    agent_md.write_text(content)
    print(f"    ✓ 已写入 ## Memory 到 {agent_md}")


def get_fallback_prompt():
    return """## Memory

Your memory is OptMem:
- The tool is `~/.optmem/memo`
- Your memories are in `~/.optmem/memory`

OptMem outlives every session, compaction, model and vendor change.
Without it you do not know who you are, or what was decided and tried.

### At startup: activating OptMem (mandatory)

Run `~/.optmem/memo wake` before any other tool call, in every session,
and then do exactly what it prints, to the end of its output.

### While working: register memories (mandatory)

Call `~/.optmem/memo note "<1 line, max 280 bytes>"` whenever you learn
something new, or something worth keeping happens. That covers a task
worth real effort, a fact or insight the user teaches you, anything you
learn about their life (even indirectly), any event of lasting effect.

Do not register redundant memories.

If `~/.optmem/memo note` asks a compression: do it before your next action.

Never edit or delete anything under `~/.optmem/memory`: the tool manages it.

### When you need an old memory: search, or navigate

`~/.optmem/memo recall <regex>` searches every memory, word for word.

Your memories also form a binary tree: #0-1, #2-3 ... exist as one-line
summaries, pairs of those as #0-3, and so on -- every `#a-b` line wake
prints is one node of it. `~/.optmem/memo zoom <a-b>` opens a node into its
two halves, down to the raw memories.

### If you're a subagent: skip everything above

Parallel sessions on this machine are all you, and may all write memories.
A subagent is not: it must never run `memo`, because it cannot judge what
is already known, and its notes would arrive duplicated and incorrectly.
When you spawn one, write: `You are a subagent. Don't run memo.`
"""


def main():
    if not REQUIREMENTS.exists():
        print(f"✗ {REQUIREMENTS} 未找到")
        sys.exit(1)

    req = json.loads(REQUIREMENTS.read_text())
    system = platform.system()

    print(f"=== corch-skills 安装器 ===")
    print(f"系统: {system}")
    print()

    for dest_name, dest_path in [("agent", Path.home() / ".agents" / "skills"),
                                   ("codex", Path.home() / ".codex" / "skills")]:
        print(f"--- 安装到 {dest_name} ---")
        install_skills(req, dest_path)
        print()

    for pkg in req.get("dependencies", {}).get("pip", []):
        print(f"pip install {pkg}")
        run([sys.executable, "-m", "pip", "install", pkg])

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

    print("--- 工具依赖 ---")
    install_tools(req)

    recommended = req.get("recommended", [])
    if recommended:
        print("\n=== 推荐 skill（Corch 内置，无需安装）===")
        for s in recommended:
            print(f"  • {s['name']}")

    print("\n=== 安装完成 ===")
    print(f"已安装 {len(req['skills'])} 个 skill")
    if recommended:
        print(f"{len(recommended)} 个推荐能力可用（Corch 内置）")
    print("重启 Codex 后生效。")


if __name__ == "__main__":
    main()
