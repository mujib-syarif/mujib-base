#!/usr/bin/env python3
"""Build web-optimised WebP images and JSON manifests for the static site.

originals/              untouched masters (this script only READS from it)
site/gallery/           catalog thumbnails (WebP, max 1100px, q86) + manifest.json
site/gallery/large/     fullscreen/detail version (WebP, max 2400px, q90)
site/free/              same layout for the Free Base cards
site/testimoni/         optimised testimonials + manifest.json

Rules
- Only top-level image files are processed (no recursion, no dot-files/dirs),
  so nested repo/workflow files can never be picked up.
- Catalog display names come from the file name ("Nama TH 17.jpg") or from
  tools/catalog-names.json (original file name -> display name).
- Files that are neither named "... TH n" nor listed in catalog-names.json
  are skipped, so loose screenshots never leak into the public catalog.
- Unchanged sources are not re-encoded (sha1 + parameters stored in manifest).

Usage:  python tools/optimize_images.py [--seed-dates dates.json]
"""
import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
KEEP = {".gitkeep", "manifest.json"}

THUMB = {"max": 1100, "q": 86}
LARGE = {"max": 2400, "q": 90}
TESTI = {"max": 1000, "q": 85}

SETS = [
    {"key": "gallery", "src": "originals", "dst": "site/gallery", "large": True, "curate": True, "owned": True},
    {"key": "free", "src": "originals/free", "dst": "site/free", "large": True, "curate": False, "owned": True},
    {"key": "testimoni", "src": "originals/testimoni", "dst": "site/testimoni", "large": False, "curate": False, "owned": False},
]


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "base"


def parse_meta(stem: str):
    clean = re.sub(r"[()\[\]._-]+", " ", stem)
    clean = re.sub(r"\s+", " ", clean).strip()
    m = re.match(r"^(.*?)\s*\bTH\s*(\d{1,2})\b", clean, re.I)
    if not m:
        return clean, None
    return (m.group(1).strip() or clean), int(m.group(2))


def source_files(directory: Path):
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in EXTS
    )


def encode(src: Path, out: Path, spec: dict) -> tuple[int, int]:
    out.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        im.thumbnail((spec["max"], spec["max"]), Image.Resampling.LANCZOS)  # never upscales
        im.save(out, "WEBP", quality=spec["q"], method=6)
        return im.size


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json_if_changed(path: Path, data) -> bool:
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def build_set(cfg: dict, names: dict, seeds: dict) -> None:
    src_dir, dst_dir = ROOT / cfg["src"], ROOT / cfg["dst"]
    assert not str(dst_dir).startswith(str(src_dir) + "/") and dst_dir != src_dir, "output must not be inside originals/"
    manifest_path = dst_dir / "manifest.json"
    prev = {i["src"]: i for i in load_json(manifest_path, {}).get("items", [])}
    params = f"{THUMB}|{LARGE}" if cfg["large"] else f"{TESTI}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    items, used, expected, skipped = [], set(), set(), []
    for f in source_files(src_dir):
        display = names.get(f.name)
        stem = display or f.stem
        name, th = parse_meta(stem)
        if cfg["curate"] and not display and th is None:
            skipped.append(f.name)
            continue
        slug = base = slugify(stem)
        n = 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)

        thumb_rel = f"{slug}.webp"
        large_rel = f"large/{slug}.webp"
        digest = sha1(f)
        old = prev.get(f.name)
        thumb_out, large_out = dst_dir / thumb_rel, dst_dir / large_rel
        reuse = (old and old.get("sha") == digest and old.get("p") == params
                 and old.get("slug") == slug and thumb_out.exists()
                 and (not cfg["large"] or large_out.exists()))
        if reuse:
            w, h, lw, lh = old["w"], old["h"], old.get("lw"), old.get("lh")
        else:
            tspec = THUMB if cfg["large"] else TESTI
            w, h = encode(f, thumb_out, tspec)
            lw = lh = None
            if cfg["large"]:
                lw, lh = encode(f, large_out, LARGE)
            print(f"  encoded {f.name} -> {thumb_rel}")
        expected.add(thumb_rel)
        if cfg["large"]:
            expected.add(large_rel)

        item = {
            "id": slug, "name": name, "th": th, "src": f.name, "slug": slug,
            "thumb": f"{cfg['dst'].split('site/', 1)[1]}/{thumb_rel}",
            "w": w, "h": h,
            "v": hashlib.sha1(thumb_out.read_bytes()).hexdigest()[:8],
            "added": (old or {}).get("added") or seeds.get(f.name) or now,
            "sha": digest, "p": params,
        }
        if cfg["large"]:
            item["large"] = f"{cfg['dst'].split('site/', 1)[1]}/{large_rel}"
            item["lw"], item["lh"] = lw, lh
            item["lv"] = hashlib.sha1(large_out.read_bytes()).hexdigest()[:8]
        items.append(item)

    # stale generated files (only in directories this pipeline fully owns)
    if cfg["owned"] and dst_dir.is_dir():
        for p in list(dst_dir.rglob("*")):
            if p.is_file() and p.name not in KEEP:
                if p.relative_to(dst_dir).as_posix() not in expected:
                    p.unlink()
                    print(f"  removed stale {p.relative_to(ROOT)}")

    if cfg["key"] == "testimoni":
        # also list files placed directly in site/testimoni
        listed = {i["thumb"].rsplit("/", 1)[-1] for i in items}
        for p in source_files(dst_dir):
            if p.name not in listed:
                with Image.open(p) as im:
                    w, h = im.size
                items.append({"id": slugify(p.stem), "name": "Testimoni", "th": None, "src": p.name,
                              "thumb": f"testimoni/{p.name}", "w": w, "h": h,
                              "v": sha1(p)[:8], "added": prev.get(p.name, {}).get("added") or now})
        items.sort(key=lambda i: i["src"].casefold())
    else:
        items.sort(key=lambda i: (i["added"], i["name"].casefold()), reverse=False)
        items.sort(key=lambda i: i["added"], reverse=True)

    changed = write_json_if_changed(manifest_path, {"version": 1, "items": items})
    total_t = sum((dst_dir / Path(i["thumb"]).name).stat().st_size for i in items if (dst_dir / Path(i["thumb"]).name).exists())
    print(f"[{cfg['key']}] {len(items)} items, thumbs {total_t / 1024:.0f} KB total, "
          f"skipped {len(skipped)}, manifest {'updated' if changed else 'unchanged'}")
    for s in skipped:
        print(f"  skipped (no 'TH n' in name and not in catalog-names.json): {s}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-dates", help="JSON {original file name: ISO date} used for first-time 'added'")
    args = ap.parse_args()
    names = load_json(ROOT / "tools/catalog-names.json", {})
    seeds = load_json(Path(args.seed_dates), {}) if args.seed_dates else {}
    for cfg in SETS:
        build_set(cfg, names, seeds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
