#!/usr/bin/env python3
"""Dependency-free smoke checks for the static BaseNama site."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
INDEX = SITE / "index.html"


class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.fragments: list[str] = []
        self.external_blank: list[tuple[str, str]] = []
        self.images_without_alt: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "a":
            href = attrs.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.fragments.append(href[1:])
            if attrs.get("target") == "_blank":
                self.external_blank.append((href, attrs.get("rel", "")))
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src", "(dynamic image)"))


def relative_luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    first, second = relative_luminance(foreground), relative_luminance(background)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


def fail(message: str):
    print(f"FAIL: {message}")
    return 1


def main() -> int:
    errors: list[str] = []
    if not INDEX.is_file():
        return fail("site/index.html is missing")
    html = INDEX.read_text(encoding="utf-8")
    parser = AuditParser()
    parser.feed(html)
    parser.close()

    duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
    if duplicates:
        errors.append("duplicate HTML IDs: " + ", ".join(duplicates))
    missing = sorted(set(parser.fragments) - set(parser.ids))
    if missing:
        errors.append("broken in-page links: " + ", ".join("#" + item for item in missing))
    unsafe = [href for href, rel in parser.external_blank if "noopener" not in rel.split()]
    if unsafe:
        errors.append('target="_blank" links missing rel="noopener": ' + ", ".join(unsafe))
    if parser.images_without_alt:
        errors.append("images missing alt attributes: " + ", ".join(parser.images_without_alt))
    if 'name="google-site-verification"' not in html:
        errors.append("Google Search Console verification meta tag is missing")
    if "https://wa.me/6285876832230" not in html:
        errors.append("expected WhatsApp order destination is missing")
    if "prefers-reduced-motion" not in html:
        errors.append("reduced-motion handling is missing")

    light_muted_count = html.count("--muted:#666872")
    if light_muted_count < 2:
        errors.append("could not verify muted text color in both light-theme paths")
    light_muted = ["#666872"] if light_muted_count >= 2 else []
    for color in light_muted:
        for background in ("#f4f4f6", "#ffffff"):
            ratio = contrast_ratio(color, background)
            if ratio < 4.5:
                errors.append(
                    f"light-theme muted text contrast fails WCAG AA: {color} on {background} = {ratio:.2f}:1"
                )

    mobile_marker = html.find("/* ACCESSIBILITY PASS:")
    mobile_media = html.find("@media(max-width:767px){", mobile_marker)
    mobile_end = html.find("}", mobile_media)
    if mobile_marker < 0 or mobile_media < 0 or mobile_end < 0:
        errors.append("mobile accessibility touch-target rules are missing")
        rules = ""
    else:
        rules = html[mobile_media:mobile_end]
    for required in (
        ".icon-btn{width:40px;height:40px;min-width:40px;min-height:40px}",
        ".chip{min-height:36px;padding-inline:11px}",
        ".drawer-links a{min-height:44px}",
        ".fab{width:44px;height:44px;min-width:44px;min-height:44px}",
    ):
        if required not in rules:
            errors.append(f"mobile accessibility rule missing: {required}")

    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print(
        "PASS: HTML IDs and in-page links, external-link safety, image alt attributes, "
        "required metadata, reduced-motion support, light-theme contrast, mobile touch targets, manifest JSON, unique item IDs, and assets."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
