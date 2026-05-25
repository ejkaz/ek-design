"""
ek-web shared helpers — yaml loader, token resolver, output writer.

The exporter scripts (export-tailwind / export-shadcn / export-css-vars)
import from this module so token resolution stays consistent across formats.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DIST_DIR = SKILL_DIR / "dist"

# design-model.yaml lives in the sibling ek-design plugin.
# Layout: ek-design-repo/plugins/{ek-design, ek-web}/skills/{ek-design, ek-web}/
# From SKILL_DIR (=plugins/ek-web/skills/ek-web), parents are:
#   [0] plugins/ek-web/skills · [1] plugins/ek-web · [2] plugins
EK_DESIGN_YAML = SKILL_DIR.parents[2] / "ek-design" / "skills" / "ek-design" / "design-model.yaml"

TOKEN_RE = re.compile(r"\{([a-z_]+)\.([a-zA-Z0-9_]+)\}")


def load_model() -> dict:
    """Load and return the ek-design design-model.yaml."""
    if not EK_DESIGN_YAML.exists():
        print(f"ERROR: {EK_DESIGN_YAML} not found", file=sys.stderr)
        sys.exit(1)
    with EK_DESIGN_YAML.open() as f:
        return yaml.safe_load(f)


def resolve(value, primitives: dict) -> str:
    """Resolve a single {family.stop} reference to its hex value.

    Pass-through for already-literal hexes or non-strings.
    """
    if not isinstance(value, str):
        return str(value)
    m = TOKEN_RE.fullmatch(value.strip())
    if not m:
        return value
    family, stop = m.group(1), m.group(2)
    fam = primitives.get(family, {})
    if stop in fam:
        return fam[stop]
    try:
        return fam[int(stop)]
    except (KeyError, ValueError):
        return value


def resolve_deep(value, primitives: dict) -> str:
    """Resolve a value that may contain MULTIPLE {family.stop} references
    interspersed with literal text (e.g. box-shadow strings).

    Example:
      '0 0 8px {magenta.500}, 0 0 16px {magenta.500}40'
      → '0 0 8px #FF2A6D, 0 0 16px #FF2A6D40'
    """
    if not isinstance(value, str):
        return str(value)

    def sub(m):
        family, stop = m.group(1), m.group(2)
        fam = primitives.get(family, {})
        if stop in fam:
            return fam[stop]
        try:
            return fam[int(stop)]
        except (KeyError, ValueError):
            return m.group(0)

    return TOKEN_RE.sub(sub, value)


def banner(model: dict, regen_cmd: str, comment_open: str = "/*", comment_close: str = "*/") -> str:
    """Standard autogen banner. comment_open/close defaults work for CSS."""
    meta = model["meta"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = (
        f"AUTO-GENERATED FROM ek-design design-model.yaml — DO NOT EDIT MANUALLY\n"
        f"Source: ek-design v{meta['version']} · brand_version: {meta['brand_version']}\n"
        f"Generated: {ts}\n"
        f"Regenerate: {regen_cmd}"
    )
    indent = "\n  "
    return f"{comment_open}\n  {body.replace(chr(10), indent)}\n{comment_close}"


def banner_line(model: dict, regen_cmd: str, line_prefix: str = "// ") -> str:
    """Single-line-comment style banner (for TS/JS)."""
    meta = model["meta"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "AUTO-GENERATED FROM ek-design design-model.yaml — DO NOT EDIT MANUALLY",
        f"Source: ek-design v{meta['version']} · brand_version: {meta['brand_version']}",
        f"Generated: {ts}",
        f"Regenerate: {regen_cmd}",
    ]
    return "\n".join(f"{line_prefix}{ln}" for ln in lines)


def write_output(filename: str, content: str) -> Path:
    """Write to dist/<filename> and return the path."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    out = DIST_DIR / filename
    out.write_text(content, encoding="utf-8")
    print(f"  wrote {out.relative_to(SKILL_DIR)}  ({len(content):,} bytes)")
    return out
