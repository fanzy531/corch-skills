#!/usr/bin/env python3
"""C-hub (C-Hub) 知识库查询工具。

认证方式（二选一）：
  --login             交互式输入 API Key
  --login-email       用 C-hub 邮箱 + 密码登录（自动换取 API Key）

查询模式：
  search <query>      关键词搜索（无需分块，立即可用）
  chat <query>        RAG 问答（需分块）

工具命令：
  --status            查看认证状态
  --list-kbs          列出知识库
  --list-docs <kb_id> 列出知识库文档

凭证存储：~/.corch/config.json（仅 owner 可读）
也可通过环境变量 WEKNORA_API_KEY / WEKNORA_BASE_URL 注入。
"""

import argparse, json, os, sys, uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

CONFIG_DIR = Path.home() / ".corch"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_BASE = "https://c-hub.cschool.ac.cn/api/v1"


# ── 认证与配置 ──────────────────────────────────

def _load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def _save_config(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(0o600)

def _get_creds():
    key = os.getenv("WEKNORA_API_KEY")
    base = os.getenv("WEKNORA_BASE_URL", DEFAULT_BASE)
    if not key:
        cfg = _load_config()
        key = cfg.get("api_key", "")
        base = cfg.get("base_url", base)
    return base, key


# ── API 请求 ────────────────────────────────────

def _api(path, method="GET", body=None, headers=None, params=None, use_auth=True):
    base, key = _get_creds()
    if use_auth and not key:
        bail("未认证。请先运行 --login 或 --login-email")

    url = f"{base.rstrip('/')}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    hdrs = {"Content-Type": "application/json"}
    if use_auth:
        hdrs["X-API-Key"] = key
    if headers:
        hdrs.update(headers)
    data = json.dumps(body).encode() if body else None
    try:
        with urlopen(Request(url, data=data, headers=hdrs, method=method), timeout=60) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body_text = e.read().decode()[:300]
        if e.code == 401:
            if "auth" in path.lower():
                bail("邮箱或密码错误，请重试 --login-email")
            bail("API Key 无效，请重试 --login-email")
        bail(f"HTTP {e.code}: {body_text}")
    except URLError as e:
        bail(f"无法连接 C-hub: {e.reason}")

def bail(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(1)


# ── 认证命令 ────────────────────────────────────

def cmd_login(args):
    """交互式输入 API Key"""
    base = args.base_url or DEFAULT_BASE
    key = args.api_key or input("  API Key: ").strip()
    if not key:
        bail("API Key 不能为空")
    _verify_and_save(base, key, "API Key")


def cmd_login_email(args):
    os.environ["WEKNORA_BASE_URL"] = args.base_url or DEFAULT_BASE
    """用邮箱密码登录，自动换取 API Key"""
    base = args.base_url or DEFAULT_BASE
    email = args.email or input("  C-hub 邮箱: ").strip()
    password = args.password or input("  密码: ").strip()
    if not email or not password:
        bail("邮箱和密码不能为空")

    print(f"🔐 正在登录 C-hub...", end=" ", flush=True)
    result = _api("/auth/login", "POST",
                  {"email": email, "password": password}, use_auth=False)
    if result.get("_http_error"):
        print("❌")
        bail(f"登录失败：{result.get('_body', '未知错误')}")
    
    tenant = result.get("tenant", {})
    api_key = tenant.get("api_key", "")
    if not api_key:
        bail(f"登录成功但未获取到 API Key。响应：{json.dumps(result, ensure_ascii=False)[:200]}")

    print("✅")
    _verify_and_save(base, api_key, "邮箱登录")


def _verify_and_save(base, api_key, label):
    os.environ["WEKNORA_API_KEY"] = api_key
    os.environ["WEKNORA_BASE_URL"] = base
    # 注意：_api 的 base 是从环境变量读的，要先设
    global _get_creds
    # 重新认证

    print(f"🔍 正在验证 C-hub 连接...", end=" ", flush=True)
    try:
        kbs = _call_api(f"{base}/knowledge-bases", api_key)
        count = len(kbs.get("data", []))
        print("✅ 通过")
        print(f"   可访问 {count} 个知识库")
    except SystemExit:
        print("❌ 失败")
        sys.exit(1)

    _save_config({"base_url": base, "api_key": api_key})
    print(f"💾 凭证已保存到 {CONFIG_FILE}")
    print(f"✅ 认证完成，现在可以正常使用 corch-hub 了")


def _call_api(url, api_key, method="GET", body=None):
    hdrs = {"X-API-Key": api_key, "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    try:
        with urlopen(Request(url, data=data, headers=hdrs, method=method), timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        bail(f"验证失败: HTTP {e.code}")
    except URLError as e:
        bail(f"连接失败: {e.reason}")


def cmd_status():
    base, key = _get_creds()
    cfg = _load_config()
    env = os.getenv("WEKNORA_API_KEY", "")

    print("🔐 C-hub 认证状态")
    print(f"   服务地址: {base}")
    print(f"   API Key: {'✅ 已设置' if key else '❌ 未设置'}")
    if key:
        src = "环境变量" if env else "配置" if cfg.get("api_key") else "?"
        print(f"   来源: {src}")
        print(f"   正在验证...", end=" ", flush=True)
        try:
            kbs = _call_api(f"{base}/knowledge-bases", key)
            print("✅ 连接正常")
            print(f"   可访问 {len(kbs.get('data', []))} 个知识库")
        except SystemExit:
            print("❌ 连接失败")


# ── 查询命令 ────────────────────────────────────

def cmd_search(query, kb_ids, top_n=10):
    if not kb_ids:
        kb_ids = [kb["id"] for kb in _api("/knowledge-bases").get("data", [])]
    data = _api("/knowledge-search", "POST",
                {"query": query, "knowledge_base_ids": kb_ids, "top_n": top_n})
    return {"results": data.get("data", []), "mode": "keyword_search"}


def cmd_chat(query, kb_ids, agent_id, session_id=None):
    if not kb_ids:
        kb_ids = [kb["id"] for kb in _api("/knowledge-bases").get("data", [])]
    if not session_id:
        session_id = _api("/sessions", "POST", {"title": "corch-hub"})["data"]["id"]

    base, key = _get_creds()
    payload = {"query": query, "agent_id": agent_id, "knowledge_base_ids": kb_ids}
    req = Request(f"{base.rstrip('/')}/knowledge-chat/{session_id}",
                  data=json.dumps(payload).encode(),
                  headers={"X-API-Key": key, "Content-Type": "application/json",
                           "Accept": "text/event-stream"}, method="POST")
    answer_parts, references = [], []
    with urlopen(req, timeout=120) as resp:
        for line_raw in resp:
            line = line_raw.decode().strip()
            if not line or not line.startswith("data: "):
                continue
            try:
                ev = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            rt = ev.get("response_type", "")
            if rt == "references" and ev.get("knowledge_references"):
                references = ev["knowledge_references"]
            elif rt == "answer":
                c = ev.get("content", "")
                if c:
                    answer_parts.append(c)
                if ev.get("done"):
                    break
    return {"answer": "".join(answer_parts), "references": references,
            "session_id": session_id, "mode": "rag_chat"}


def list_docs(kb_id, page_size=500):
    docs, page = [], 1
    while True:
        data = _api(f"/knowledge-bases/{kb_id}/knowledge",
                     params={"page": str(page), "page_size": str(page_size)})
        items = data.get("data", [])
        docs.extend(items)
        if len(docs) >= data.get("total", 0) or not items:
            break
        page += 1
    return docs


# ── CLI ─────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="C-hub 知识库查询工具")
    p.add_argument("--login", nargs="?", const=True, help="输入 API Key 认证")
    p.add_argument("--login-email", nargs="?", const=True, help="用邮箱密码登录")
    p.add_argument("--api-key", help="API Key（配合 --login）")
    p.add_argument("--email", help="C-hub 邮箱（配合 --login-email）")
    p.add_argument("--password", help="密码（配合 --login-email）")
    p.add_argument("--base-url", help="C-hub 服务地址")
    p.add_argument("--status", action="store_true", help="查看认证状态")

    sub = p.add_subparsers(dest="mode")
    s = sub.add_parser("search", help="关键词搜索（无需分块）")
    s.add_argument("query"); s.add_argument("--kb-ids"); s.add_argument("--top-n", type=int, default=10)
    c = sub.add_parser("chat", help="RAG 问答（需分块）")
    c.add_argument("query"); c.add_argument("--kb-ids")
    c.add_argument("--agent", default="builtin-quick-answer"); c.add_argument("--session")
    p.add_argument("--list-kbs", action="store_true")
    p.add_argument("--list-docs", metavar="KB_ID")
    args = p.parse_args()

    if args.login:
        return cmd_login(args)
    if args.login_email:
        return cmd_login_email(args)
    if args.status:
        return cmd_status()

    _get_creds()  # 触发未认证检查

    if args.list_kbs:
        kbs = _api("/knowledge-bases")
        return print(json.dumps([{"id": kb["id"], "name": kb.get("name","?"),
                                   "chunk_count": kb.get("chunk_count", 0)}
                                  for kb in kbs.get("data", [])], ensure_ascii=False, indent=2))
    if args.list_docs:
        docs = list_docs(args.list_docs)
        print(json.dumps([{"id": d["id"], "type": d.get("type","?"),
                           "title": d.get("title","?")[:60]} for d in docs],
                         ensure_ascii=False, indent=2))
        return print(f"\n--- Total: {len(docs)} ---", file=sys.stderr)

    if not args.mode:
        return p.print_help()

    kb_ids = args.kb_ids.split(",") if args.kb_ids else None
    if args.mode == "search":
        result = cmd_search(args.query, kb_ids, args.top_n)
    else:
        result = cmd_chat(args.query, kb_ids, args.agent, args.session)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
