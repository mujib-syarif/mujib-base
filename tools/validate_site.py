#!/usr/bin/env python3
"""Sanity checks for the static site. Exit code 1 when something is wrong."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)
    print("ERROR:", msg)


# 1. manifests point to files that exist
for key in ("gallery", "free", "testimoni"):
    mf = SITE / key / "manifest.json"
    if not mf.exists():
        err(f"missing {mf.relative_to(ROOT)}")
        continue
    try:
        manifest = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        err(f"{key}: invalid manifest JSON ({exc})")
        continue

    items = manifest.get("items", [])
    if not isinstance(items, list):
        err(f"{key}: manifest 'items' must be an array")
        continue

    seen_ids = set()
    site_root = SITE.resolve()
    for index, it in enumerate(items):
        if not isinstance(it, dict):
            err(f"{key}: item {index} must be an object")
            continue

        item_id = it.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            err(f"{key}: item {index} has no valid id")
        elif item_id in seen_ids:
            err(f"{key}: duplicate item id: {item_id}")
        else:
            seen_ids.add(item_id)

        for field in ("thumb", "large"):
            if field not in it:
                if field == "thumb":
                    err(f"{key}: item {index} is missing required thumb path")
                continue
            raw_path = it[field]
            if not isinstance(raw_path, str) or not raw_path.strip():
                err(f"{key}: item {index} has invalid {field} path")
                continue
            target = (SITE / raw_path).resolve()
            if not target.is_relative_to(site_root):
                err(f"{key}: {field} path escapes site directory: {raw_path}")
            elif not target.is_file():
                err(f"{key}: {raw_path} listed in manifest but file is missing")
    print(f"ok  {key}: {len(items)} items")

# 2. local references in index.html exist
html = (SITE / "index.html").read_text(encoding="utf-8")
for ref in re.findall(r'(?:src|href)="([^"#?][^"]*)"', html):
    if re.match(r"^(https?:|mailto:|tel:|data:|javascript:)", ref):
        continue
    if not (SITE / unquote(ref.split("?")[0])).exists():
        err(f"index.html references missing file: {ref}")

# 3. required content
required = [
    "Rp. 15.000", "Rp. 20.000", "Rp. 25.000", "TH 7 – 10", "TH 11 – 13", "TH 14 – 18",
    "https://wa.me/6285876832230",
    "085876832230", "mujib_syarif", "Segera hadir",
    "OpenLayout&id=TH13%3AHV%3AAAAAXAAAAAHgDBRZjV-taqygtyJvksiK",
    "OpenLayout&id=TH14%3AHV%3AAAAAKgAAAAKg-3NiX9FBrECvkHNUh3KN",
]
for text in required:
    if text not in html:
        err(f"index.html is missing required text: {text[:60]}")

# 4. stale references / dead code anywhere in tracked text files
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts or p.suffix.lower() not in {".html", ".md", ".yml", ".yaml", ".toml", ".json", ".py", ".txt"}:
        continue
    if p.name == "validate_site.py":
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    if "mujibsukaIT" in text:
        err(f"stale owner reference in {p.relative_to(ROOT)}")
for dead in ("card-fav", "fav-empty", "api.github.com", "raw.githubusercontent.com"):
    if dead in html:
        err(f"dead/stale code found in index.html: {dead}")

# 5. generated output never lands in the wrong place
if (ROOT / "gallery").exists():
    err("top-level gallery/ exists; generated images must live in site/gallery/")

print("FAILED" if errors else "All checks passed")
sys.exit(1 if errors else 0)
