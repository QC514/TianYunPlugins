#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan plugins/ and regenerate publicFileIndex.json."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"
OUTPUT_FILE = ROOT / "publicFileIndex.json"

SUPPORTED_SUFFIXES = {".py", ".js"}

BOOL_KEYS = {"public", "admin", "disable"}
MULTI_KEYS = {"rule"}
KEY_ALIASES = {
    "tile": "title",  # common typo in some plugins
}

# Line prefix + opening bracket + key + colon.
HEADER_START_RE = re.compile(
    r"^[ \t]*(?:\#|//)[ \t]*\[\s*(?P<key>[A-Za-z_][\w-]*)\s*:\s*"
)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def parse_bool(value: str, default: bool = False) -> bool:
    text = value.strip().lower()
    if not text:
        return default
    # Strip trailing comments/noise after the boolean token.
    token = re.split(r"[\s,;，。]", text, maxsplit=1)[0]
    if token in {"true", "1", "yes", "y", "on"}:
        return True
    if token in {"false", "0", "no", "n", "off"}:
        return False
    return default


def normalize_version(value: str) -> str:
    text = value.strip()
    if not text:
        return "v0"
    if text.lower().startswith("v"):
        return text
    return f"v{text}"


def clean_header_value(value: str) -> str:
    return value.strip().strip("\"'").strip()


def extract_header_value(line: str, start_index: int) -> str:
    """Extract value after key colon until the header's closing bracket.

    Plugin headers are single-line. Values may contain nested [] (regex
    character classes, inline notes like [author]), so use the last ']' on
    the line as the closer. Anything after that is treated as a trailing
    comment.
    """
    close_at = line.rfind("]")
    if close_at >= start_index:
        return line[start_index:close_at]
    return line[start_index:]


def iter_header_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    lines = text.splitlines()
    header_lines: list[str] = []

    for line in lines[:200]:
        stripped = line.strip()
        if not stripped:
            if header_lines:
                header_lines.append(line)
            continue
        if stripped.startswith("#") or stripped.startswith("//"):
            header_lines.append(line)
            continue
        if header_lines:
            break
        if (
            stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith("var ")
            or stripped.startswith("let ")
            or stripped.startswith("const ")
            or stripped.startswith("function ")
        ):
            break

    scan_lines = header_lines if header_lines else lines[:120]
    for line in scan_lines:
        match = HEADER_START_RE.match(line)
        if not match:
            continue
        key = match.group("key").strip().lower()
        value = extract_header_value(line, match.end())
        pairs.append((key, clean_header_value(value)))
    return pairs


def parse_headers(text: str) -> dict[str, Any]:
    """Parse plugin metadata headers from the top of a file."""
    meta: dict[str, Any] = {"rule": []}

    for key, value in iter_header_pairs(text):
        key = KEY_ALIASES.get(key, key)

        if key in MULTI_KEYS:
            if value:
                meta.setdefault("rule", []).append(value)
            continue

        if key in BOOL_KEYS:
            meta[key] = parse_bool(value, default=False if key != "public" else True)
            continue

        # Keep first non-empty occurrence for scalar fields.
        if key not in meta or meta[key] in ("", None):
            meta[key] = value

    return meta


def infer_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".js":
        return "nodejs"
    return "python"


def fallback_title(filename: str) -> str:
    stem = Path(filename).stem
    # Drop a trailing ".js" for names like foo.js.py from archive packaging.
    if stem.lower().endswith(".js"):
        stem = stem[:-3]
    # Prefer human title from "[author]_name" packaging if present.
    m = re.match(r"^\[(?P<author>[^\]]+)\]_(?P<name>.+)$", stem)
    if m:
        return m.group("name").strip() or stem
    return stem


def build_entry(rel_path: str, filename: str, meta: dict[str, Any]) -> dict[str, Any]:
    title = clean_header_value(str(meta.get("title") or "")) or fallback_title(filename)
    version = normalize_version(str(meta.get("version") or "0"))
    rules = meta.get("rule") or []
    if isinstance(rules, str):
        rule = rules
    else:
        rule = "|".join(r for r in rules if r)

    public = meta.get("public")
    if not isinstance(public, bool):
        public = parse_bool(str(public), default=True) if public is not None else True

    admin = meta.get("admin")
    if not isinstance(admin, bool):
        admin = parse_bool(str(admin), default=False) if admin is not None else False

    disable = meta.get("disable")
    if not isinstance(disable, bool):
        disable = parse_bool(str(disable), default=False) if disable is not None else False

    return {
        "id": title,  # may be rewritten later for duplicate titles
        "name": title,
        "title": title,
        "type": infer_type(Path(filename)),
        "path": rel_path.replace("\\", "/"),
        "version": version,
        "desc": str(meta.get("description") or meta.get("desc") or ""),
        "rule": rule,
        "icon": str(meta.get("icon") or "").strip(),
        "author": str(meta.get("author") or "").strip(),
        "class": str(meta.get("class") or "").strip(),
        "public": public,
        "admin": admin,
        "disable": disable,
    }


def assign_unique_ids(entries: list[dict[str, Any]]) -> None:
    """Assign id/name with _2/_3 suffixes for duplicate titles, path-sorted."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        groups[entry["title"]].append(entry)

    for title, group in groups.items():
        group.sort(key=lambda e: e["path"])
        for index, entry in enumerate(group):
            plugin_id = title if index == 0 else f"{title}_{index + 1}"
            entry["id"] = plugin_id
            entry["name"] = plugin_id


def collect_plugin_files(plugins_dir: Path) -> list[Path]:
    if not plugins_dir.is_dir():
        raise FileNotFoundError(f"plugins directory not found: {plugins_dir}")
    files = [
        p
        for p in plugins_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    files.sort(key=lambda p: p.name)
    return files


def generate_index(plugins_dir: Path = PLUGINS_DIR) -> dict[str, dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in collect_plugin_files(plugins_dir):
        rel_path = f"plugins/{path.name}"
        text = read_text(path)
        meta = parse_headers(text)
        entries.append(build_entry(rel_path, path.name, meta))

    assign_unique_ids(entries)
    index = {entry["path"]: entry for entry in entries}
    # Stable key order, matching existing publicFileIndex.json habit.
    return dict(sorted(index.items(), key=lambda item: item[0]))


def dump_index(index: dict[str, dict[str, Any]], output_file: Path = OUTPUT_FILE) -> None:
    # Match existing pretty style: 1-space indent.
    text = json.dumps(index, ensure_ascii=False, indent=1)
    output_file.write_text(text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check_only = "--check" in argv

    index = generate_index()
    if check_only:
        if not OUTPUT_FILE.exists():
            print(f"missing index file: {OUTPUT_FILE}", file=sys.stderr)
            return 1
        current = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        if current == index:
            print(f"publicFileIndex.json is up to date ({len(index)} plugins)")
            return 0
        print(
            f"publicFileIndex.json is stale (current={len(current)}, generated={len(index)})",
            file=sys.stderr,
        )
        return 2

    dump_index(index)
    print(f"Wrote {OUTPUT_FILE} with {len(index)} plugins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())