#!/usr/bin/env python3
"""
ek-craft.py — data-driven brand lint for .tsx / .jsx / .css / .html / .md targets.

Reads design-model.yaml from the sibling ek-design plugin and applies:
  - avoid.color / avoid.color_family / avoid.font_family / avoid.pattern
  - primary_axis_preserved (magenta CTA monopoly, fonts)
  - invariants (mono_for_identifiers, no_consumer_indigo_purple, etc.)

Plus universal rules adapted for cyberpunk web UI (see references/anti-ai-slop.md).

Usage:
  python3 ek-craft.py FILE_OR_GLOB [FILE_OR_GLOB...]
  python3 ek-craft.py --format jsonl FILE
  python3 ek-craft.py --severity error FILE
  python3 ek-craft.py --model /path/to/design-model.yaml FILE

Exit:
  0 — clean (no errors)
  1 — errors found
  2 — lint crashed
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_MODEL = SKILL_DIR.parents[2] / "ek-design" / "skills" / "ek-design" / "design-model.yaml"

HEX_RE = re.compile(r"#([0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
TAILWIND_INDIGO_RE = re.compile(r"\b(bg|text|border|ring|from|to|via)-(indigo|violet|purple|fuchsia)-\d{2,3}\b")
TAILWIND_FONT_RE = re.compile(r"\bfont-(serif|mono|sans|display|[A-Za-z][A-Za-z0-9_-]*)\b")
FONT_FAMILY_DECL_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)", re.IGNORECASE)
EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF✀-➿⌀-⏿]"
)
GRADIENT_MESH_RE = re.compile(r"bg-gradient-to-[a-z]+\s+from-(indigo|violet|purple|pink|fuchsia)", re.IGNORECASE)
DROP_SHADOW_RE = re.compile(r"box-shadow\s*:\s*[^;}\n]*rgba?\(\s*0\s*,\s*0\s*,\s*0", re.IGNORECASE)
BACKDROP_BLUR_HEAVY_RE = re.compile(r"backdrop-blur-(2xl|3xl)|backdrop-filter\s*:\s*blur\(\s*(?:[2-9]\d|\d{3,})px\s*\)", re.IGNORECASE)


@dataclass
class Finding:
    file: str
    line: int
    col: int
    severity: str  # "error" / "warning" / "info"
    rule: str
    value: str
    message: str
    suggestion: str = ""

    def human(self) -> str:
        sev = self.severity.upper().ljust(7)
        loc = f"{self.file}:{self.line}".ljust(60)
        rule = self.rule.ljust(28)
        suggestion = f"\n  → {self.suggestion}" if self.suggestion else ""
        return f"{loc} {sev} {rule} {self.message}{suggestion}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, f: Finding):
        self.findings.append(f)

    def by_severity(self) -> dict:
        counts = {"error": 0, "warning": 0, "info": 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts


# ─── Model loader + token resolver ─────────────────────────────────────────

TOKEN_RE = re.compile(r"\{([a-z_]+)\.([a-zA-Z0-9_]+)\}")


def resolve_color(value, primitives: dict) -> str:
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


def collect_role_hex_map(model: dict) -> dict[str, str]:
    """Map normalized hex → role-token name (uppercase hex)."""
    prims = model["primitives"]["colors"]
    mapping = {}
    for role_name, role_ref in model.get("roles", {}).items():
        resolved = resolve_color(role_ref, prims)
        if isinstance(resolved, str) and resolved.startswith("#"):
            mapping[resolved.upper()] = role_name
    return mapping


# ─── Linters ───────────────────────────────────────────────────────────────


def normalize_hex(h: str) -> str:
    """Normalize #abc → #AABBCC; uppercase. Drop alpha."""
    h = h.lstrip("#").upper()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]  # drop alpha
    return f"#{h}"


def file_lines(text: str) -> list[tuple[int, str]]:
    return list(enumerate(text.splitlines(), start=1))


def lint_avoid_block(text: str, file: str, model: dict, report: Report):
    """Apply each entry in design-model.yaml `avoid` to the file."""
    avoid = model.get("avoid", [])
    primitives = model["primitives"]["colors"]
    # Pre-collect ek primitive hexes so we don't flag those
    allowed_hexes = set()
    for fam in primitives.values():
        for v in fam.values():
            if isinstance(v, str) and v.startswith("#"):
                allowed_hexes.add(normalize_hex(v))

    for line_no, line in file_lines(text):
        for entry in avoid:
            sev = entry.get("severity", "warning")

            if "color" in entry:
                target = normalize_hex(entry["color"])
                for m in HEX_RE.finditer(line):
                    if normalize_hex("#" + m.group(1)) == target:
                        report.add(
                            Finding(
                                file=file,
                                line=line_no,
                                col=m.start() + 1,
                                severity=sev,
                                rule=f"avoid.color",
                                value=entry["color"],
                                message=f"{entry.get('name', target)}: {entry.get('reason', 'forbidden color').rstrip('.')}",
                                suggestion="use a role token or an ek primitive ramp",
                            )
                        )

            elif "color_family" in entry:
                family = entry["color_family"]
                if family == "consumer-purple" or family == "trust-gradient":
                    for m in HEX_RE.finditer(line):
                        hx = normalize_hex("#" + m.group(1))
                        if _is_consumer_indigo_purple(hx):
                            report.add(
                                Finding(
                                    file=file,
                                    line=line_no,
                                    col=m.start() + 1,
                                    severity=sev,
                                    rule=f"avoid.color_family:{family}",
                                    value=hx,
                                    message=f"Hex {hx} falls in banned family '{family}': {entry.get('reason','')}",
                                    suggestion="use bg-magenta-500 / bg-steel-violet-500 / etc.",
                                )
                            )

            elif "font_family" in entry:
                target_font = entry["font_family"].lower()
                for m in FONT_FAMILY_DECL_RE.finditer(line):
                    decl = m.group(1).lower()
                    if target_font in decl:
                        report.add(
                            Finding(
                                file=file,
                                line=line_no,
                                col=m.start() + 1,
                                severity=sev,
                                rule="avoid.font_family",
                                value=entry["font_family"],
                                message=f"Forbidden font in font-family declaration: {entry.get('reason', target_font)}",
                                suggestion="use Chakra Petch (font-display), Inter (font-sans), or JetBrains Mono (font-mono)",
                            )
                        )
                # Tailwind class form: font-<name>
                for m in TAILWIND_FONT_RE.finditer(line):
                    cls = m.group(1).lower()
                    if cls == target_font.replace(" ", "-").replace("'", "").replace('"', ""):
                        report.add(
                            Finding(
                                file=file,
                                line=line_no,
                                col=m.start() + 1,
                                severity=sev,
                                rule="avoid.font_family",
                                value=cls,
                                message=f"Forbidden Tailwind font class: font-{cls}",
                                suggestion="use font-display, font-sans, or font-mono",
                            )
                        )

            elif "pattern" in entry:
                _check_pattern(line, line_no, file, entry, sev, report)


def _is_consumer_indigo_purple(hex_v: str) -> bool:
    """Return True if hex is in the Tailwind indigo / consumer purple family."""
    blocked = {
        "#6366F1", "#4F46E5", "#4338CA", "#3730A3", "#312E81",
        "#8B5CF6", "#7C3AED", "#6D28D9", "#5B21B6",
        "#A78BFA", "#C4B5FD", "#DDD6FE",
        "#A855F7", "#9333EA", "#7E22CE",
        "#D946EF", "#C026D3", "#A21CAF",
        "#EC4899", "#DB2777", "#BE185D",  # consumer-pink, near family
    }
    return hex_v.upper() in blocked


def _check_pattern(line: str, line_no: int, file: str, entry: dict, sev: str, report: Report):
    pattern = entry["pattern"]
    msg = entry.get("reason", "")

    if pattern == "emoji-as-icon":
        # Look for emoji inside button/heading-ish JSX or className contexts
        if EMOJI_RE.search(line) and any(s in line for s in ["<button", "<h1", "<h2", "<h3", '<li', 'className="icon', 'icon-']):
            for m in EMOJI_RE.finditer(line):
                report.add(
                    Finding(
                        file=file, line=line_no, col=m.start() + 1, severity=sev,
                        rule="avoid.pattern:emoji-as-icon",
                        value=m.group(0),
                        message=f"Emoji in UI chrome: {msg}",
                        suggestion="use a Lucide SVG icon instead",
                    )
                )

    elif pattern == "gradient-mesh-background":
        if GRADIENT_MESH_RE.search(line):
            m = GRADIENT_MESH_RE.search(line)
            report.add(
                Finding(
                    file=file, line=line_no, col=m.start() + 1, severity=sev,
                    rule="avoid.pattern:gradient-mesh-background",
                    value=m.group(0),
                    message=f"Gradient mesh: {msg}",
                    suggestion="solid bg-bg + accent component(s)",
                )
            )

    elif pattern == "drop-shadow-as-elevation":
        if DROP_SHADOW_RE.search(line):
            m = DROP_SHADOW_RE.search(line)
            report.add(
                Finding(
                    file=file, line=line_no, col=m.start() + 1, severity=sev,
                    rule="avoid.pattern:drop-shadow-as-elevation",
                    value="box-shadow rgba(0,0,0,...)",
                    message=f"Gray drop shadow as elevation: {msg}",
                    suggestion="use shadow-neon-glow-magenta / shadow-neon-glow-cyan / shadow-panel-lift",
                )
            )

    elif pattern == "glassmorphism-heavy-blur":
        if BACKDROP_BLUR_HEAVY_RE.search(line):
            m = BACKDROP_BLUR_HEAVY_RE.search(line)
            report.add(
                Finding(
                    file=file, line=line_no, col=m.start() + 1, severity=sev,
                    rule="avoid.pattern:glassmorphism-heavy-blur",
                    value=m.group(0),
                    message=f"Heavy backdrop blur: {msg}",
                    suggestion="cap at backdrop-blur-md (8px) + border glow",
                )
            )

    elif pattern == "lorem-ipsum":
        if "lorem ipsum" in line.lower() or "Lorem ipsum" in line:
            idx = line.lower().find("lorem ipsum")
            report.add(
                Finding(
                    file=file, line=line_no, col=idx + 1, severity=sev,
                    rule="avoid.pattern:lorem-ipsum",
                    value="lorem ipsum",
                    message=f"Lorem ipsum: {msg}",
                    suggestion="use real content or an honest placeholder",
                )
            )

    elif pattern == "rounded-card-with-colored-left-border":
        # Heuristic: rounded-* + border-l-* + (-magenta-|-cyan-|-lime-|-amber-|-red-) on same line
        if re.search(r"rounded-(?!none\b)\w+", line) and re.search(
            r"border-l-(2|4|8)?\s*border-(magenta|cyan|lime|amber|red|green|blue)-\d", line
        ):
            report.add(
                Finding(
                    file=file, line=line_no, col=1, severity=sev,
                    rule="avoid.pattern:rounded-card-with-colored-left-border",
                    value="rounded-* + border-l-color",
                    message=f"Rounded card with colored left border: {msg}",
                    suggestion="drop either the radius or the left border",
                )
            )


def lint_consumer_indigo_purple(text: str, file: str, report: Report):
    """Tailwind class form of the indigo/purple/violet/fuchsia ban (locked invariant)."""
    for line_no, line in file_lines(text):
        for m in TAILWIND_INDIGO_RE.finditer(line):
            report.add(
                Finding(
                    file=file, line=line_no, col=m.start() + 1, severity="error",
                    rule="invariants.no_consumer_indigo_purple",
                    value=m.group(0),
                    message="Tailwind consumer-indigo / violet / purple / fuchsia class",
                    suggestion="use bg-magenta-* (action) or bg-steel-violet-* (atmospheric)",
                )
            )


def lint_costume_fonts(text: str, file: str, report: Report):
    """Costume cyberpunk fonts (Orbitron, Press Start 2P, etc.) — universal rule."""
    banned = {"orbitron", "press start 2p", "vt323", "audiowide", "bungee", "monoton"}
    for line_no, line in file_lines(text):
        for m in FONT_FAMILY_DECL_RE.finditer(line):
            decl = m.group(1).lower()
            for f in banned:
                if f in decl:
                    report.add(
                        Finding(
                            file=file, line=line_no, col=m.start() + 1, severity="warning",
                            rule="universal.costume_font",
                            value=f,
                            message=f"Costume cyberpunk font: {f}",
                            suggestion="use Chakra Petch (font-display) — cyber-coded but production-legible",
                        )
                    )


def lint_role_token_preferred(text: str, file: str, role_hex_map: dict, report: Report):
    """If a literal hex matches a role-resolved hex, suggest the role token instead."""
    # Only flag in .tsx / .jsx / .html — in .css the hex literals are likely the @theme block itself
    if file.endswith((".css", ".scss")):
        return
    for line_no, line in file_lines(text):
        for m in HEX_RE.finditer(line):
            hx = normalize_hex("#" + m.group(1))
            if hx in role_hex_map:
                role = role_hex_map[hx]
                report.add(
                    Finding(
                        file=file, line=line_no, col=m.start() + 1, severity="info",
                        rule="prefer_role_tokens",
                        value=hx,
                        message=f"Hex literal {hx} matches role token '{role}'",
                        suggestion=f"use bg-{role.replace('_','-')} or var(--color-{role.replace('_','-')})",
                    )
                )


def lint_reduced_motion_required(text: str, file: str, report: Report):
    """If a CSS file declares @keyframes or animation, it must also include prefers-reduced-motion."""
    if not file.endswith((".css", ".scss")):
        return
    has_anim = bool(re.search(r"@keyframes\b|animation\s*:", text, re.IGNORECASE))
    has_pref = "prefers-reduced-motion" in text
    if has_anim and not has_pref:
        report.add(
            Finding(
                file=file, line=1, col=1, severity="warning",
                rule="invariants.reduced_motion_required",
                value="@keyframes / animation without prefers-reduced-motion",
                message="CSS contains animation/keyframes but no prefers-reduced-motion override",
                suggestion="add @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 80ms !important; transition-duration: 80ms !important; } }",
            )
        )


# ─── File walking ─────────────────────────────────────────────────────────


def expand_targets(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        # Glob expansion
        matches = glob.glob(p, recursive=True)
        if matches:
            out.extend(Path(m) for m in matches)
        else:
            out.append(Path(p))
    # De-dup, filter to lintable extensions
    seen = set()
    lintable = []
    for p in out:
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".tsx", ".jsx", ".ts", ".js", ".css", ".scss", ".html", ".htm", ".md", ".mdx"}:
            continue
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        lintable.append(p)
    return lintable


def lint_file(path: Path, model: dict, role_hex_map: dict, report: Report):
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        report.add(
            Finding(
                file=str(path), line=1, col=1, severity="warning",
                rule="lint.read_error", value="", message=f"Could not read file: {e}",
            )
        )
        return
    fp = str(path)
    lint_avoid_block(text, fp, model, report)
    lint_consumer_indigo_purple(text, fp, report)
    lint_costume_fonts(text, fp, report)
    lint_role_token_preferred(text, fp, role_hex_map, report)
    lint_reduced_motion_required(text, fp, report)


# ─── CLI ──────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ek-craft brand lint")
    ap.add_argument("targets", nargs="+", help="Files or globs to lint")
    ap.add_argument("--model", default=str(DEFAULT_MODEL), help="Path to design-model.yaml")
    ap.add_argument("--format", choices=["human", "jsonl"], default="human", help="Output format")
    ap.add_argument("--severity", choices=["error", "warning", "info"], default="info",
                    help="Minimum severity to report (info=all, warning=W+E, error=E only)")
    ap.add_argument("--no-info", action="store_true", help="Suppress info-level findings (alias for --severity warning)")
    args = ap.parse_args(argv)

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"ERROR: design-model.yaml not found at {model_path}", file=sys.stderr)
        return 2
    with model_path.open() as f:
        model = yaml.safe_load(f)

    role_hex_map = collect_role_hex_map(model)
    targets = expand_targets(args.targets)
    if not targets:
        print("ERROR: no lintable files found in targets", file=sys.stderr)
        return 2

    report = Report()
    for t in targets:
        lint_file(t, model, role_hex_map, report)

    # Severity filter
    severity_rank = {"error": 0, "warning": 1, "info": 2}
    min_rank = severity_rank["warning" if args.no_info else args.severity]
    filtered = [f for f in report.findings if severity_rank[f.severity] <= min_rank]

    if args.format == "jsonl":
        for f in filtered:
            print(json.dumps(asdict(f)))
    else:
        for f in filtered:
            print(f.human())
        counts = report.by_severity()
        scanned = len(targets)
        print(
            f"\nek-craft · {scanned} file{'s' if scanned != 1 else ''} scanned · "
            f"{counts['error']} error · {counts['warning']} warning · {counts['info']} info "
            f"· brand_version {model['meta']['brand_version']}"
        )

    return 1 if report.by_severity()["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
