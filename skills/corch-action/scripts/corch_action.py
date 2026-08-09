#!/usr/bin/env python3
"""Secure WordPress helper for corch-action.

The helper reads credentials internally from ~/.corch/config.json. It never
prints the application password or an Authorization header.
"""

import argparse
import base64
import getpass
import hashlib
import html.parser
import json
import mimetypes
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


CONFIG_FILE = Path.home() / ".corch" / "config.json"
DEFAULT_SITE = "https://c-lab.org"
VALID_STATUSES = {"draft", "pending", "private", "publish", "future"}
VALID_CATEGORIES = {"fieldwork", "inspirations"}
DATE_FIELDS = ("period_start", "period_end")


class ActionError(Exception):
    """A user-facing, non-secret error."""


def output(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def normalize_site(site):
    site = (site or "").strip()
    if not site:
        raise ActionError("WordPress site is empty")
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    return site.rstrip("/")


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ActionError(f"Cannot read {CONFIG_FILE}: {exc}") from exc


def save_config(config):
    config_dir = CONFIG_FILE.parent
    config_dir.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="config.", suffix=".tmp", dir=config_dir)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(config, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, CONFIG_FILE)
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def credentials():
    wordpress = load_config().get("wordpress", {})
    site = wordpress.get("site")
    username = wordpress.get("username")
    password = wordpress.get("app_password")
    if not site or not username or not password:
        raise ActionError(
            "WordPress credentials are not configured; run corch_action.py login"
        )
    return normalize_site(site), str(username), str(password)


def redact(message, username="", password=""):
    text = str(message)
    for secret in (password, username):
        if secret:
            text = text.replace(secret, "[redacted]")
    text = re.sub(r"(?i)(authorization\s*:\s*basic\s+)[^\s]+", r"\1[redacted]", text)
    return text[:500]


def request(site, username, password, path, method="GET", body=None, headers=None, timeout=30):
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    request_headers = {
        "Authorization": f"Basic {auth}",
        "User-Agent": "corch-action/1.0",
    }
    if headers:
        request_headers.update(headers)
    req = Request(f"{site}{path}", data=body, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as response:
            return response.status, response.headers.get_content_type(), response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ActionError(f"HTTP {exc.code}: {redact(detail, username, password)}") from exc
    except URLError as exc:
        raise ActionError(f"Network error: {redact(exc.reason, username, password)}") from exc
    except TimeoutError as exc:
        raise ActionError(f"Request timed out: {redact(exc, username, password)}") from exc


def json_request(site, username, password, path, payload, method="POST"):
    body = None if method == "GET" else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    status, _, response_body = request(
        site,
        username,
        password,
        path,
        method=method,
        body=body,
        headers={
            "Accept": "application/json",
            **({"Content-Type": "application/json"} if body is not None else {}),
        },
    )
    try:
        data = json.loads(response_body.decode("utf-8"))
    except json.JSONDecodeError:
        data = {"raw_response": response_body.decode("utf-8", errors="replace")[:1000]}
    return status, data


def load_json_file(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ActionError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ActionError(f"Invalid JSON in {path}: {exc}") from exc


def nonempty(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ActionError(f"{field} must be a non-empty string")


class ImageSourceChecker(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        values = dict(attrs)
        src = values.get("src", "")
        if not src.startswith(("http://", "https://")):
            self.errors.append("every img src must be an absolute http(s) URL")
        if not values.get("alt", "").strip():
            self.errors.append("every img must have non-empty alt text")


def check_html(value, field):
    if not isinstance(value, str):
        raise ActionError(f"{field} must be a string")
    parser = ImageSourceChecker()
    try:
        parser.feed(value)
    except Exception as exc:
        raise ActionError(f"{field} contains invalid HTML: {exc}") from exc
    if parser.errors:
        raise ActionError(f"{field}: {parser.errors[0]}")


def check_media_ids(value, field):
    if not isinstance(value, list):
        raise ActionError(f"{field} must be an array")
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            raise ActionError(f"{field} must contain positive media IDs")


def validate_payload(payload):
    if not isinstance(payload, dict):
        raise ActionError("Payload root must be a JSON object")
    nonempty(payload.get("title"), "title")

    status = payload.get("status", "draft")
    if status not in VALID_STATUSES:
        raise ActionError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
    if "content" in payload:
        nonempty(payload["content"], "content") if payload["content"] else None

    acf = payload.get("acf")
    if not isinstance(acf, dict):
        raise ActionError("acf must be an object")

    category = acf.get("action_category")
    if category not in VALID_CATEGORIES:
        raise ActionError("acf.action_category must be fieldwork or inspirations")

    period = acf.get("action_period")
    if not isinstance(period, dict):
        raise ActionError("acf.action_period must be an object")
    for field in DATE_FIELDS:
        value = period.get(field)
        if not isinstance(value, str) or not re.fullmatch(r"\d{8}", value):
            raise ActionError(f"acf.action_period.{field} must use YYYYMMDD")
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as exc:
            raise ActionError(f"acf.action_period.{field} is not a valid date") from exc

    sections = acf.get("action_sections")
    if not isinstance(sections, list) or not sections:
        raise ActionError("acf.action_sections must be a non-empty array")
    for index, section in enumerate(sections, 1):
        if not isinstance(section, dict):
            raise ActionError(f"acf.action_sections[{index}] must be an object")
        nonempty(section.get("section_number"), f"section {index}.section_number")
        nonempty(section.get("section_title"), f"section {index}.section_title")
        check_html(section.get("section_body", ""), f"section {index}.section_body")
        check_media_ids(section.get("section_gallery", []), f"section {index}.section_gallery")

    tags = acf.get("action_tags", [])
    if not isinstance(tags, list):
        raise ActionError("acf.action_tags must be an array")
    for index, tag in enumerate(tags, 1):
        if not isinstance(tag, dict):
            raise ActionError(f"action_tags[{index}] must be an object")
        nonempty(tag.get("tag"), f"action_tags[{index}].tag")

    outcomes = acf.get("action_outcomes", [])
    if not isinstance(outcomes, list):
        raise ActionError("acf.action_outcomes must be an array")
    for index, outcome in enumerate(outcomes, 1):
        if not isinstance(outcome, dict):
            raise ActionError(f"action_outcomes[{index}] must be an object")
        for field in ("outcome_label", "outcome_title", "outcome_desc"):
            nonempty(outcome.get(field), f"action_outcomes[{index}].{field}")

    gallery = acf.get("action_gallery", [])
    if not isinstance(gallery, list):
        raise ActionError("acf.action_gallery must be an array")
    for index, item in enumerate(gallery, 1):
        if not isinstance(item, dict):
            raise ActionError(f"action_gallery[{index}] must be an object")
        media_id = item.get("gallery_image")
        if isinstance(media_id, bool) or not isinstance(media_id, int) or media_id <= 0:
            raise ActionError(f"action_gallery[{index}].gallery_image must be a positive media ID")
        if "gallery_caption" in item and not isinstance(item["gallery_caption"], str):
            raise ActionError(f"action_gallery[{index}].gallery_caption must be a string")

    for key in payload:
        if any(token in key.lower() for token in ("password", "token", "api_key", "authorization")):
            raise ActionError(f"credential-like field is not allowed in payload: {key}")

    post_id = payload.get("post_id")
    if post_id is not None and (isinstance(post_id, bool) or not isinstance(post_id, int) or post_id <= 0):
        raise ActionError("post_id must be a positive integer")

    return {
        "title": payload["title"],
        "status": status,
        "post_id": post_id,
        "sections": len(sections),
        "inline_images": sum(len(re.findall(r"<img\b", section["section_body"], re.IGNORECASE)) for section in sections),
        "gallery_images": len(gallery) + sum(len(section.get("section_gallery", [])) for section in sections),
    }


def cmd_status(_args):
    site, username, password = credentials()
    status, data = json_request(site, username, password, "/wp-json/wp/v2/users/me?context=edit", {}, method="GET")
    output({
        "ok": status == 200,
        "site": site,
        "username": username,
        "application_password": "configured",
        "user": data.get("name") if isinstance(data, dict) else None,
        "roles": data.get("roles", []) if isinstance(data, dict) else [],
    })
    if status != 200:
        raise ActionError("WordPress credential verification failed")


def cmd_login(args):
    site = normalize_site(args.site or DEFAULT_SITE)
    username = (args.username or input("WordPress username: ")).strip()
    if args.password_stdin:
        password = sys.stdin.readline().rstrip("\r\n")
    else:
        password = getpass.getpass("WordPress application password: ")
    if not username or not password:
        raise ActionError("username and application password are required")
    status, data = json_request(site, username, password, "/wp-json/wp/v2/users/me?context=edit", {}, method="GET")
    if status != 200:
        raise ActionError("credential verification failed")
    config = load_config()
    config["wordpress"] = {"site": site, "username": username, "app_password": password}
    save_config(config)
    output({"ok": True, "site": site, "username": username, "saved": str(CONFIG_FILE), "user": data.get("name")})


def cmd_validate(args):
    summary = validate_payload(load_json_file(args.payload))
    output({"ok": True, "operation": "validate", **summary})


def cmd_plan(args):
    summary = validate_payload(load_json_file(args.payload))
    operation = "update" if summary["post_id"] else "create"
    output({"ok": True, "operation": operation, **summary})


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_map(path):
    if not path or not Path(path).exists():
        return {"version": 1, "items": {}}
    data = load_json_file(path)
    if not isinstance(data, dict) or not isinstance(data.get("items", {}), dict):
        raise ActionError("media map must contain an items object")
    return data


def save_map(path, media_map):
    if not path:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f"{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(media_map, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def cmd_upload_media(args):
    site, username, password = credentials()
    media_map = load_map(args.map)
    alt_map = {}
    if args.alt_map:
        alt_data = load_json_file(args.alt_map)
        if not isinstance(alt_data, dict):
            raise ActionError("--alt-map must contain a JSON object mapping paths to alt text")
        alt_map = alt_data
    results = []
    failures = []
    for raw_path in args.files:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            failures.append({"file": raw_path, "error": "file not found"})
            continue
        alt_text = alt_map.get(str(path)) or alt_map.get(raw_path) or args.alt or ""
        digest = sha256(path)
        key = str(path)
        cached = media_map["items"].get(key)
        if cached and cached.get("sha256") == digest and cached.get("id") and cached.get("url"):
            results.append({"file": raw_path, "id": cached["id"], "url": cached["url"], "reused": True})
            continue
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        filename = quote(path.name, safe="")
        try:
            status, _, response_body = request(
                site,
                username,
                password,
                "/wp-json/wp/v2/media",
                method="POST",
                body=path.read_bytes(),
                headers={
                    "Content-Type": content_type,
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Accept": "application/json",
                },
            )
            data = json.loads(response_body.decode("utf-8"))
            media_id = data.get("id")
            media_url = data.get("source_url")
            if status not in (200, 201) or not media_id or not media_url:
                raise ActionError("media upload returned an incomplete response")
            if alt_text:
                try:
                    json_request(site, username, password, f"/wp-json/wp/v2/media/{media_id}", {"alt_text": alt_text})
                except ActionError as exc:
                    failures.append({"file": raw_path, "id": media_id, "error": f"uploaded; alt text failed: {exc}"})
            media_map["items"][key] = {"sha256": digest, "id": media_id, "url": media_url, "source": raw_path}
            save_map(args.map, media_map)
            results.append({"file": raw_path, "id": media_id, "url": media_url, "reused": False})
        except (ActionError, OSError, json.JSONDecodeError) as exc:
            failures.append({"file": raw_path, "error": redact(exc, username, password)})
    output({"ok": not failures, "uploaded": results, "failures": failures, "map": args.map})
    if failures:
        raise ActionError("one or more media uploads failed; successful uploads were kept")


def cmd_publish(args):
    payload = load_json_file(args.payload)
    summary = validate_payload(payload)
    if summary["status"] in {"publish", "future"} and not args.confirm_publish:
        raise ActionError("publishing requires --confirm-publish")
    site, username, password = credentials()
    status, data = json_request(site, username, password, "/wp-json/clab/v1/publish-action", payload)
    if status < 200 or status >= 300:
        raise ActionError(f"publish endpoint returned HTTP {status}")
    output({"ok": True, "operation": "publish", "summary": summary, "response": data})


def build_parser():
    parser = argparse.ArgumentParser(description="Secure corch-action WordPress helper")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", help="verify and save credentials")
    login.add_argument("--site", help="WordPress site URL")
    login.add_argument("--username", help="WordPress username")
    login.add_argument("--password-stdin", action="store_true", help="read password from stdin; never pass it as an argument")
    login.set_defaults(func=cmd_login)

    status = sub.add_parser("status", help="verify saved credentials")
    status.set_defaults(func=cmd_status)

    for name, help_text, func in (("validate", "validate a payload without network access", cmd_validate), ("plan", "validate and summarize a payload", cmd_plan)):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("payload", help="payload JSON file")
        command.set_defaults(func=func)

    upload = sub.add_parser("upload-media", help="upload images without printing credentials")
    upload.add_argument("files", nargs="+", help="image files")
    upload.add_argument("--map", help="optional JSON media map for retry-safe reuse")
    upload.add_argument("--alt", help="fallback alt text applied to uploaded files without alt-map entry")
    upload.add_argument("--alt-map", help="JSON object mapping local image paths to alt text")
    upload.set_defaults(func=cmd_upload_media)

    publish = sub.add_parser("publish", help="publish a validated action payload")
    publish.add_argument("payload", help="payload JSON file")
    publish.add_argument("--confirm-publish", action="store_true", help="required for publish/future status")
    publish.set_defaults(func=cmd_publish)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(args)
    except ActionError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
