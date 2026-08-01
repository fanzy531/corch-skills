#!/usr/bin/env python3
"""WordPress 凭证管理 — corch-digest / corch-action 共享。

用法:
  wordpress-credentials.py --login                交互式输入并验证保存
  wordpress-credentials.py --login --site URL --user USER --password PASS
  wordpress-credentials.py --status               查看认证状态
  wordpress-credentials.py --get                  输出 JSON 凭证（给发布脚本用）

凭证保存于 ~/.corch/config.json 的 wordpress 字段（权限 600）。
"""

import argparse, base64, json, os, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

CONFIG_DIR = Path.home() / ".corch"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_SITE = "https://c-lab.org"


def _load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def _save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(0o600)


def _wp_creds():
    cfg = _load_config()
    wp = cfg.get("wordpress", {})
    return wp.get("site", ""), wp.get("username", ""), wp.get("app_password", "")


def _verify(site, username, password):
    """通过 WordPress REST API 验证凭证是否有效。"""
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    site = site.rstrip("/")
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    req = Request(
        f"{site}/wp-json/wp/v2/users/me?context=edit",
        headers={"Authorization": f"Basic {token}"},
    )
    try:
        with urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            name = data.get("name") or data.get("username") or username
            roles = data.get("roles", [])
            return True, f"用户 {name}（角色: {', '.join(roles) or '未知'}）"
    except HTTPError as e:
        if e.code in (401, 403):
            return False, "凭证无效（401/403），请检查用户名和应用密码"
        return False, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except URLError as e:
        return False, f"无法连接 {site}: {e.reason}"


def cmd_login(args):
    site = args.site or DEFAULT_SITE
    username = args.user or input("  WordPress 用户名: ").strip()
    password = args.password or input("  应用密码（WP后台生成）: ").strip()
    if not username or not password:
        print("❌ 用户名和密码不能为空", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 正在验证 {site} ...", end=" ", flush=True)
    ok, msg = _verify(site, username, password)
    if not ok:
        print("❌")
        print(f"  {msg}", file=sys.stderr)
        sys.exit(1)
    print("✅")
    print(f"  {msg}")

    cfg = _load_config()
    cfg["wordpress"] = {"site": site, "username": username, "app_password": password}
    _save_config(cfg)
    print(f"💾 凭证已保存到 {CONFIG_FILE}")
    print("✅ 以后发布文章不再需要输入凭证")


def cmd_status():
    site, user, pwd = _wp_creds()
    print("🔐 WordPress 认证状态")
    if not site or not user or not pwd:
        print("   ❌ 未配置，请先运行 --login")
        sys.exit(1)
    print(f"   站点: {site}")
    print(f"   用户: {user}")
    print("   应用密码: ✅ 已配置")
    print("   正在验证...", end=" ", flush=True)
    ok, msg = _verify(site, user, pwd)
    if ok:
        print("✅ 连接正常")
        print(f"   {msg}")
    else:
        print("❌")
        print(f"   {msg}", file=sys.stderr)
        sys.exit(1)


def cmd_get():
    """输出凭证 JSON 给发布脚本用（不打印密码明文）。"""
    site, user, pwd = _wp_creds()
    if not site or not user or not pwd:
        print(json.dumps({"ok": False, "error": "未配置"}), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "site": site, "username": user, "app_password": pwd}))


def main():
    p = argparse.ArgumentParser(description="WordPress 凭证管理")
    p.add_argument("--login", action="store_true", help="交互式登录并保存")
    p.add_argument("--site", help="WordPress 站点 URL")
    p.add_argument("--user", help="WordPress 用户名")
    p.add_argument("--password", help="应用密码")
    p.add_argument("--status", action="store_true", help="查看认证状态")
    p.add_argument("--get", action="store_true", help="输出凭证 JSON")
    args = p.parse_args()

    if args.login:
        cmd_login(args)
    elif args.status:
        cmd_status()
    elif args.get:
        cmd_get()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
