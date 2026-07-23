#!/usr/bin/env python3
"""Give Quarto's generated theme CSS stable URLs.

Quarto changes the Bootstrap CSS filename whenever the theme changes. Cached
HTML can otherwise keep pointing at a deleted hash and render without the
site theme, especially when Safari restores an older tab.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "_site"
BOOTSTRAP_DIR = OUTPUT_DIR / "site_libs" / "bootstrap"

THEMES = {
    "bootstrap": re.compile(r"bootstrap-[0-9a-f]{32}\.min\.css"),
    "bootstrap-dark": re.compile(r"bootstrap-dark-[0-9a-f]{32}\.min\.css"),
}

# Keep the two most recent pre-fix URLs alive so already-cached pages recover
# without requiring visitors to clear Safari's website data.
LEGACY_ALIASES = {
    "bootstrap": (
        "bootstrap-1f9ac3ef0e8f262428fcc6bb703857ff.min.css",
    ),
    "bootstrap-dark": (
        "bootstrap-dark-12243f65cb2b4c4bc0dbf661224a9805.min.css",
    ),
}


def generated_theme_path(stable_name: str, pattern: re.Pattern[str]) -> Path:
    aliases = set(LEGACY_ALIASES[stable_name])
    referenced_names = {
        match.group(0)
        for html_path in OUTPUT_DIR.rglob("*.html")
        for match in pattern.finditer(html_path.read_text(encoding="utf-8"))
        if match.group(0) not in aliases
    }
    if len(referenced_names) == 1:
        referenced = BOOTSTRAP_DIR / referenced_names.pop()
        if referenced.is_file():
            return referenced

    matches = sorted(
        path
        for path in BOOTSTRAP_DIR.glob("*.min.css")
        if pattern.fullmatch(path.name) and path.name not in aliases
    )
    if len(matches) != 1:
        names = ", ".join(path.name for path in matches) or "none"
        raise RuntimeError(f"expected one generated theme CSS, found: {names}")
    return matches[0]


def main() -> None:
    if not BOOTSTRAP_DIR.is_dir():
        raise RuntimeError(f"missing rendered Bootstrap directory: {BOOTSTRAP_DIR}")

    replacements: dict[str, str] = {}
    for stable_name, pattern in THEMES.items():
        generated = generated_theme_path(stable_name, pattern)
        stable = BOOTSTRAP_DIR / f"{stable_name}.min.css"
        shutil.copyfile(generated, stable)
        replacements[generated.name] = stable.name

        for alias_name in LEGACY_ALIASES[stable_name]:
            shutil.copyfile(generated, BOOTSTRAP_DIR / alias_name)

    changed = 0
    for html_path in OUTPUT_DIR.rglob("*.html"):
        original = html_path.read_text(encoding="utf-8")
        updated = original
        for generated_name, stable_name in replacements.items():
            updated = updated.replace(generated_name, stable_name)
        if updated != original:
            html_path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"stabilized theme CSS references in {changed} HTML files")


if __name__ == "__main__":
    main()
