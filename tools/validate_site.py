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
    items = json.loads(mf.read_text(encoding="utf-8")).get("items", [])
    for it in items:
        for field in ("thumb", "large"):
            if field in it and not (SITE / it[field]).exists():
                err(f"{key}: {it[field]} listed in manifest but file is missing")
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
    "Rp. 15.000", "Rp. 20.000", "Rp. 25.000", "TH 8 – 10", "TH 11 – 13", "TH 14 – 18",
    "https://wa.me/6285876832230",
    "Jika tombol WhatsApp tidak ter-direct ke aplikasi, buka halaman ini melalui browser HP. "
    "Tekan titik tiga di pojok kanan atas, lalu pilih browser, atau chat manual di",
    "085876832230", "mujib_syarif", "Segera hadir",
    "OpenLayout&id=TH13%3AHV%3AAAAAXAAAAAHgDBRZjV-taqygtyJvksiK",
    "OpenLayout&id=TH14%3AHV%3AAAAAKgAAAAKg-3NiX9FBrECvkHNUh3KN",
    "Custom Base Nama Keren Sesuai Style Yang Dipilih",
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
