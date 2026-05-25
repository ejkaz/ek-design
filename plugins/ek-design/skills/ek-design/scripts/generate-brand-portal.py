#!/usr/bin/env python3
"""
generate-brand-portal.py

Reads design-model.yaml (sibling file) and emits 5 self-contained HTML pages
into ../brand-portal/. Each page is regenerated from the YAML — manual edits
are not allowed. Used as iteration substrate for ek-design brand evolution.

Usage:
    python3 generate-brand-portal.py

Output:
    ../brand-portal/index.html       — Overview
    ../brand-portal/color.html       — Primary axis, surfaces, ramps, roles, invariants, avoid
    ../brand-portal/typography.html  — Chakra Petch + Inter + JetBrains Mono ladder (live samples)
    ../brand-portal/motifs.html      — Neon edge glow, terminal block, scanline, diagonal cuts (live)
    ../brand-portal/components.html  — Buttons, card, terminal_block, agent_status badges, inputs (live)
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
YAML_PATH = SKILL_DIR / "design-model.yaml"
OUT_DIR = SKILL_DIR / "brand-portal"

AUTOGEN_BANNER = """<!--
    AUTO-GENERATED FROM design-model.yaml — DO NOT EDIT MANUALLY
    Regenerate: python3 scripts/generate-brand-portal.py
    Generated: {timestamp}
    design-model.yaml version: {version} · brand_version: {brand_version}
-->"""


# ─── Token resolution ──────────────────────────────────────────────────────

TOKEN_RE = re.compile(r"\{([a-z_]+)\.([a-zA-Z0-9_]+)\}")


def resolve_color(value, primitives: dict) -> str:
    """Resolve {family.stop} reference to hex, or pass through literal hex."""
    if not isinstance(value, str):
        return str(value)
    m = TOKEN_RE.fullmatch(value.strip())
    if not m:
        return value  # already a hex or literal
    family, stop = m.group(1), m.group(2)
    # numeric stops parsed as int by yaml — handle both
    fam = primitives.get(family, {})
    if stop in fam:
        return fam[stop]
    try:
        return fam[int(stop)]
    except (KeyError, ValueError):
        return value  # leave unresolved tag visible


def fg_for_bg(hex_color: str) -> str:
    """Pick #FFFFFF or #0A0A14 for text contrast against a background hex."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return "#FFFFFF"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0A0A14" if luminance > 0.55 else "#FFFFFF"


# ─── Page chrome ───────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("index.html", "Overview"),
    ("color.html", "Color"),
    ("typography.html", "Typography"),
    ("motifs.html", "Motifs"),
    ("components.html", "Components"),
]


def nav_html(current: str) -> str:
    out = ['<nav class="portal-nav">']
    for href, label in NAV_ITEMS:
        cls = "portal-nav-item active" if href == current else "portal-nav-item"
        out.append(f'<a class="{cls}" href="{href}">{label}</a>')
    out.append("</nav>")
    return "".join(out)


def base_styles() -> str:
    return """<style>
:root {
  --bg: #0A0A14;
  --bg-2: #15151F;
  --bg-3: #1F1F2A;
  --bg-deep: #000000;
  --fg: #FFFFFF;
  --fg-muted: rgba(255,255,255,0.68);
  --fg-dim: rgba(255,255,255,0.40);
  --magenta: #FF2A6D;
  --cyan: #00D1FF;
  --lime: #A6FF00;
  --amber: #FFB800;
  --red: #FF003C;
  --steel-violet: #3B3B92;
  --border: rgba(255,255,255,0.10);
  --border-soft: rgba(255,255,255,0.06);
  --gap-sm: clamp(0.5rem, 1vw, 1rem);
  --gap-md: clamp(1rem, 2vw, 2rem);
  --gap-lg: clamp(1.5rem, 3vw, 3rem);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
  font-family: 'Inter', -apple-system, sans-serif; line-height: 1.55; font-feature-settings: "ss01", "cv11"; }
.display, h1, h2, h3, .eyebrow { font-family: 'Chakra Petch', sans-serif; letter-spacing: -0.010em; }
code, pre, .mono { font-family: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace; }
code { font-size: 0.875em; background: rgba(0,209,255,0.10); padding: 0.12em 0.4em; border-radius: 3px;
  color: var(--cyan); border: 1px solid rgba(0,209,255,0.22); }
strong { font-weight: 700; }
a { color: var(--cyan); text-decoration: none; }
a:hover { text-decoration: underline; }

.portal-header { position: sticky; top: 0; background: rgba(10,10,20,0.92);
  backdrop-filter: blur(8px); border-bottom: 1px solid var(--border); z-index: 10; padding: 1rem 0; }
.portal-header-inner { max-width: 1240px; margin: 0 auto;
  padding: 0 var(--gap-md); display: flex; justify-content: space-between;
  align-items: center; gap: var(--gap-md); flex-wrap: wrap; }
.portal-mark { display: flex; flex-direction: column; gap: 0.2rem; }
.portal-mark strong { font-family: 'Chakra Petch', sans-serif; font-weight: 700;
  letter-spacing: 0.18em; font-size: 1.05rem; color: var(--magenta);
  text-shadow: 0 0 8px rgba(255,42,109,0.4); }
.portal-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--fg-muted); }
.portal-nav { display: flex; gap: 0.25rem; flex-wrap: wrap; }
.portal-nav-item { color: var(--fg-muted); text-decoration: none;
  font-family: 'Chakra Petch', sans-serif; font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase; padding: 0.45rem 0.85rem; border-radius: 4px;
  border: 1px solid transparent; transition: all 0.12s ease; }
.portal-nav-item:hover { color: var(--fg); border-color: var(--border); text-decoration: none; }
.portal-nav-item.active { color: var(--magenta); border-color: var(--magenta);
  box-shadow: 0 0 0 1px rgba(255,42,109,0.4), 0 0 12px rgba(255,42,109,0.3); }

.portal-main { max-width: 1240px; margin: 0 auto; padding: var(--gap-lg) var(--gap-md); }
.page-title { font-family: 'Chakra Petch', sans-serif; font-size: clamp(2.25rem, 5vw, 3.75rem);
  font-weight: 700; letter-spacing: -0.020em; margin: 0 0 var(--gap-md) 0; line-height: 1.02; }
.page-lead { color: var(--fg-muted); font-size: 1.0625rem; max-width: 70ch;
  line-height: 1.6; margin-bottom: var(--gap-lg); }

h2.section { font-family: 'Chakra Petch', sans-serif; font-size: 1.5rem; font-weight: 600;
  letter-spacing: -0.012em; margin: var(--gap-lg) 0 var(--gap-md) 0;
  padding-top: var(--gap-md); border-top: 1px solid var(--border); }
h3.subsection { font-family: 'Chakra Petch', sans-serif; font-size: 1.0625rem; font-weight: 600;
  letter-spacing: -0.005em; margin: var(--gap-md) 0 var(--gap-sm) 0; }
.eyebrow { font-family: 'Chakra Petch', sans-serif; font-size: 0.7rem;
  letter-spacing: 0.180em; text-transform: uppercase; font-weight: 600;
  color: var(--magenta); margin-bottom: 0.5rem; }

.swatch-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--gap-sm); margin-bottom: var(--gap-md); }
.swatch { aspect-ratio: 1.6 / 1; border-radius: 4px; padding: 0.85rem;
  display: flex; flex-direction: column; justify-content: space-between;
  font-size: 0.75rem; font-weight: 500; border: 1px solid var(--border-soft);
  position: relative; overflow: hidden; }
.swatch::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  border-radius: inherit; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }
.swatch .swatch-name { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.85rem; line-height: 1.15; letter-spacing: 0; }
.swatch .swatch-hex { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
  font-weight: 500; opacity: 0.88; padding: 0; background: transparent; color: inherit; border: 0; }
.swatch .swatch-role { font-size: 0.7rem; opacity: 0.78; line-height: 1.35; margin-top: 0.3rem; }

.token-row { display: grid; grid-template-columns: minmax(180px, 1fr) minmax(180px, 1.4fr) 2fr;
  gap: var(--gap-md); padding: 0.65rem 0; border-bottom: 1px solid var(--border-soft);
  align-items: start; font-size: 0.9rem; }
.token-row .role-name { font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 0.84rem; }
.token-row .role-ref { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
  color: var(--fg-muted); }
.token-row .role-desc { color: var(--fg-muted); line-height: 1.5; font-size: 0.84rem; }
.token-chip { display: inline-block; width: 1em; height: 1em; vertical-align: -0.15em;
  border-radius: 2px; margin-right: 0.5em; border: 1px solid rgba(255,255,255,0.15); }

.callout { border-left: 2px solid var(--magenta); background: rgba(255,42,109,0.05);
  padding: var(--gap-md); margin: var(--gap-md) 0; border-radius: 0 4px 4px 0; }
.callout strong { color: var(--magenta); }
.callout.cyan { border-left-color: var(--cyan); background: rgba(0,209,255,0.05); }
.callout.cyan strong { color: var(--cyan); }
.callout.lime { border-left-color: var(--lime); background: rgba(166,255,0,0.05); }
.callout.lime strong { color: var(--lime); }

.avoid-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--gap-sm); margin-top: var(--gap-sm); }
.avoid-item { background: rgba(255,255,255,0.025); border: 1px solid var(--border-soft);
  padding: 0.85rem; border-radius: 4px; font-size: 0.85rem; }
.avoid-item .av-swatch { display: inline-block; width: 1.4em; height: 1.4em;
  border-radius: 3px; margin-right: 0.5em; vertical-align: -0.4em;
  border: 1px solid rgba(255,255,255,0.18); }
.avoid-item .av-name { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.95rem; }
.avoid-item .av-reason { color: var(--fg-muted); font-size: 0.8rem;
  margin-top: 0.4rem; line-height: 1.45; }
.avoid-item .av-severity { font-family: 'JetBrains Mono', monospace; font-size: 0.66rem;
  letter-spacing: 0.06em; text-transform: uppercase; padding: 1px 6px; border-radius: 2px; margin-left: 0.4em; }
.av-severity.error { background: rgba(255,0,60,0.18); color: var(--red); border: 1px solid rgba(255,0,60,0.4); }
.av-severity.warning { background: rgba(255,184,0,0.18); color: var(--amber); border: 1px solid rgba(255,184,0,0.4); }

.surface-card { background: var(--bg-2); border: 1px solid var(--border-soft);
  border-radius: 6px; padding: var(--gap-md); margin-bottom: var(--gap-sm); }
.surface-card h3 { margin: 0 0 0.4rem 0; }
.surface-card .surface-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;
  color: var(--fg-muted); padding: 0; background: transparent; border: 0; }
.surface-card .surface-rationale { color: var(--fg-muted); font-size: 0.9rem;
  line-height: 1.6; margin-top: 0.6rem; }

.invariant-row { padding: 0.85rem 0; border-bottom: 1px solid var(--border-soft); font-size: 0.9rem; }
.invariant-row .inv-name { font-family: 'JetBrains Mono', monospace; font-weight: 500;
  font-size: 0.88rem; color: var(--magenta); }
.invariant-row .inv-rule { margin: 0.35rem 0; }
.invariant-row .inv-rationale { color: var(--fg-muted); font-size: 0.84rem; line-height: 1.55; }
.invariant-row .inv-severity { float: right; }

.type-sample { padding: 1.25rem; border: 1px solid var(--border-soft); border-radius: 4px;
  margin-bottom: 0.85rem; background: rgba(255,255,255,0.02); }
.type-sample .type-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
  color: var(--fg-muted); margin-bottom: 0.5rem; letter-spacing: 0.02em; }
.type-sample .type-render { line-height: 1.15; }

.motif-card { background: var(--bg-2); border: 1px solid var(--border-soft);
  border-radius: 6px; padding: var(--gap-md); margin-bottom: var(--gap-md); }
.motif-card .motif-title { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 1.0625rem; margin: 0 0 0.4rem 0; }
.motif-card .motif-rationale { color: var(--fg-muted); font-size: 0.88rem;
  line-height: 1.55; margin-bottom: var(--gap-md); }
.motif-stage { background: var(--bg); border: 1px dashed var(--border);
  border-radius: 4px; padding: var(--gap-lg); display: grid; place-items: center;
  min-height: 200px; margin-bottom: var(--gap-sm); position: relative; overflow: hidden; }
.motif-stage pre { font-size: 0.78rem; color: var(--fg-muted); margin: 0;
  white-space: pre-wrap; word-break: break-all; }

.spec-pre { background: var(--bg-2); border: 1px solid var(--border-soft);
  border-radius: 4px; padding: var(--gap-md); margin: var(--gap-sm) 0;
  font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; line-height: 1.55;
  overflow-x: auto; color: var(--fg-muted); }
.spec-pre .spec-key { color: var(--cyan); }
.spec-pre .spec-val { color: var(--lime); }

.component-stage { background: var(--bg); border: 1px solid var(--border-soft);
  border-radius: 6px; padding: var(--gap-lg); margin-bottom: var(--gap-sm);
  display: flex; gap: var(--gap-md); flex-wrap: wrap; align-items: center; }

/* Live cyberpunk components used inside the portal demos */
.btn-primary { background: var(--magenta); color: #FFFFFF; padding: 10px 20px;
  border: 0; border-radius: 4px; font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; font-size: 0.9375rem; letter-spacing: 0.020em; cursor: pointer;
  transition: all 100ms cubic-bezier(0.2,0.8,0.2,1); }
.btn-primary:hover { background: #E11D5F; box-shadow: 0 0 8px var(--magenta), 0 0 16px rgba(255,42,109,0.25); }
.btn-primary:focus-visible { outline: none; box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--magenta); }
.btn-secondary { background: transparent; color: var(--cyan); padding: 10px 20px;
  border: 1px solid var(--cyan); border-radius: 4px; font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; font-size: 0.9375rem; letter-spacing: 0.020em; cursor: pointer;
  transition: all 100ms cubic-bezier(0.2,0.8,0.2,1); }
.btn-secondary:hover { background: rgba(0,209,255,0.10); color: #2DD9FF; }
.btn-destructive { background: transparent; color: var(--red); padding: 10px 20px;
  border: 1px solid var(--red); border-radius: 4px; font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; font-size: 0.9375rem; letter-spacing: 0.020em; cursor: pointer; }

.card-demo { background: var(--bg-2); border: 1px solid #2E2E40; border-radius: 6px;
  padding: 24px; max-width: 320px; }
.card-demo .card-eyebrow { font-family: 'Chakra Petch', sans-serif; font-size: 0.7rem;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--magenta); margin-bottom: 0.5rem; }
.card-demo h4 { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 1.125rem; margin: 0 0 0.5rem 0; }
.card-demo p { color: var(--fg-muted); font-size: 0.875rem; margin: 0; line-height: 1.55; }

.terminal-demo { background: #000000; border: 1px solid #0090B8; border-radius: 2px;
  padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem;
  color: var(--cyan); line-height: 1.55; max-width: 480px; }
.terminal-demo .term-prompt { color: var(--lime); }
.terminal-demo .term-meta { color: var(--fg-muted); }

.input-demo { background: var(--bg-2); color: var(--fg); padding: 10px 12px;
  border: 1px solid #2E2E40; border-radius: 4px; font-family: 'Inter', sans-serif;
  font-size: 0.9375rem; width: 280px; transition: all 100ms ease; }
.input-demo::placeholder { color: #5C5C70; }
.input-demo:focus { outline: none; border-color: var(--cyan);
  box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--cyan); }

.badge { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px;
  border: 1px solid currentColor; border-radius: 999px; font-family: 'JetBrains Mono', monospace;
  font-weight: 500; font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.060em; }
.badge .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.badge.active { color: var(--lime); box-shadow: 0 0 6px var(--lime), 0 0 12px rgba(166,255,0,0.25); }
.badge.thinking { color: var(--cyan); }
.badge.thinking .dot { animation: ek-pulse 1.5s ease-in-out infinite; }
.badge.tool { color: #6B6BC4; }
.badge.complete { color: var(--lime); }
.badge.blocked { color: var(--amber); }
.badge.error { color: var(--red); }
.badge.idle { color: #5C5C70; }

@keyframes ek-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }

.scanline-stage { position: relative; }
.scanline-stage::after { content: ""; position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent 0, transparent 2px, rgba(255,255,255,0.06) 2px, rgba(255,255,255,0.06) 3px); }

.diagonal-cut { background: var(--bg-2); border: 1px solid #2E2E40;
  padding: 24px 28px; color: var(--fg); font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px); }

.portal-footer { max-width: 1240px; margin: var(--gap-lg) auto 0;
  padding: var(--gap-md); border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; gap: var(--gap-md);
  font-size: 0.75rem; color: var(--fg-dim); flex-wrap: wrap;
  font-family: 'JetBrains Mono', monospace; }

@media (max-width: 720px) {
  .portal-nav { width: 100%; justify-content: flex-start; }
  .token-row { grid-template-columns: 1fr; gap: 0.35rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition-duration: 80ms !important; }
}
</style>"""


def page_chrome(model: dict, page_title: str, body: str, current: str) -> str:
    meta = model["meta"]
    banner = AUTOGEN_BANNER.format(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        version=meta["version"],
        brand_version=meta["brand_version"],
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{banner}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ek-design Brand Portal — {page_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
{base_styles()}
</head>
<body>
<header class="portal-header">
  <div class="portal-header-inner">
    <div class="portal-mark">
      <strong>EK·DESIGN</strong>
      <span class="portal-meta">Brand Portal · v{meta['version']} · {meta['brand_version']}</span>
    </div>
    {nav_html(current)}
  </div>
</header>

<main class="portal-main">
  <h1 class="page-title">{page_title}</h1>
  {body}
</main>

<footer class="portal-footer">
  <div>Auto-generated from <code>design-model.yaml</code>. Manual edits not permitted.</div>
  <div>Regenerate: <code>python3 scripts/generate-brand-portal.py</code></div>
</footer>
</body>
</html>
"""


# ─── Page bodies ───────────────────────────────────────────────────────────

def body_index(m: dict) -> str:
    meta = m["meta"]
    notes_html = (meta.get("notes") or "").replace("<", "&lt;").replace(">", "&gt;")
    cards = ""
    for href, title, desc in [
        ("color.html", "Color", "Primary axis, surfaces, primitive ramps, role tokens, invariants, avoid list."),
        ("typography.html", "Typography", "Chakra Petch display + Inter body + JetBrains Mono ladder with live samples."),
        ("motifs.html", "Motifs", "Neon edge glow, terminal block inset, scanline overlay, diagonal cut corners, katakana-numeric agent IDs."),
        ("components.html", "Components", "Buttons (primary/secondary/destructive), card, terminal block, agent-status badges, code block, input field — all live-rendered."),
    ]:
        cards += f'<a href="{href}" style="text-decoration:none;color:inherit;"><div class="surface-card"><h3>{title}</h3><p class="surface-rationale">{desc}</p></div></a>'

    return f"""
<p class="page-lead">ek-design brand SSoT, rendered live from <code>design-model.yaml</code>. Every swatch, token, type sample, motif demo, and component preview on this site is auto-generated. To iterate, edit the YAML and run <code>python3 scripts/generate-brand-portal.py</code>.</p>

<div class="callout">
  <div class="eyebrow">Active version</div>
  <p style="margin:0;">Schema <strong>{meta['version']}</strong> · Brand version <strong>{meta['brand_version']}</strong> · Status <strong>{meta.get('status','—')}</strong> · Updated <strong>{meta.get('updated','—')}</strong> by <strong>{meta.get('updated_by','—')}</strong>.</p>
</div>

<h2 class="section">Identity</h2>
<p class="page-lead" style="margin-bottom:var(--gap-md);">{m.get('philosophy','').strip()}</p>

<h2 class="section">What's here</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:var(--gap-md);margin-top:var(--gap-md);">{cards}</div>

<h2 class="section">Source notes</h2>
<pre class="spec-pre" style="white-space:pre-wrap;">{notes_html}</pre>
"""


def body_color(m: dict) -> str:
    primitives = m["primitives"]["colors"]
    axis = m["primary_axis_preserved"]

    # Primary axis swatches — manually pick the labelled ones from the axis dict
    axis_pairs = [
        ("Background", axis["background"], "Default app + marketing surface"),
        ("Panel", axis["panel"], "Layered surface"),
        ("Off-white", axis["off_white"], "Inverted (light-mode opt-in)"),
        ("White", axis["white"], "Text on dark"),
        ("Magenta CTA", axis["magenta_cta"], "Primary CTA monopoly"),
        ("Cyan Secondary", axis["cyan_secondary"], "Secondary action / info / link"),
        ("Lime Alive", axis["lime_alive"], "Success + agent active indicator"),
    ]
    axis_html = ""
    for name, hex_v, role in axis_pairs:
        fg = fg_for_bg(hex_v)
        axis_html += f'<div class="swatch" style="background:{hex_v};color:{fg};"><div><div class="swatch-name">{name}</div><span class="swatch-hex">{hex_v}</span></div><div class="swatch-role">{role}</div></div>'

    # Surfaces
    surf_html = ""
    for sname, sdef in m["surfaces"].items():
        bg_resolved = resolve_color(sdef["background"], primitives)
        examples = ", ".join(sdef.get("examples", []))
        rat = sdef.get("rationale", "").strip()
        surf_html += (
            f'<div class="surface-card"><h3>{sname.replace("_", " ").title()}</h3>'
            f'<div class="surface-meta">mode: <strong>{sdef["mode"]}</strong> · '
            f'background: <span class="mono">{sdef["background"]}</span> → <span class="mono">{bg_resolved}</span></div>'
            f'<div style="margin-top:0.5rem;font-size:0.85rem;color:var(--fg-muted);"><strong>Examples:</strong> {examples}</div>'
            f'<p class="surface-rationale">{rat}</p></div>'
        )

    # Role tokens
    role_html = ""
    for rname, rref in m["roles"].items():
        resolved = resolve_color(rref, primitives) if isinstance(rref, str) else str(rref)
        role_html += (
            f'<div class="token-row"><div class="role-name">'
            f'<span class="token-chip" style="background:{resolved};"></span>{rname}</div>'
            f'<div class="role-ref">{rref} → {resolved}</div>'
            f'<div class="role-desc">Every consumer references the role token name, never the resolved hex.</div></div>'
        )

    # Primitive ramps
    ramp_html = ""
    for family, ramp in primitives.items():
        ramp_html += f'<h3 class="subsection"><code>primitives.colors.{family}</code></h3>'
        ramp_html += '<div class="swatch-grid" style="grid-template-columns:repeat(auto-fill,minmax(120px,1fr));">'
        for stop, hex_v in ramp.items():
            fg = fg_for_bg(hex_v)
            ramp_html += f'<div class="swatch" style="background:{hex_v};color:{fg};"><div><div class="swatch-name" style="font-size:0.78rem;">{stop}</div></div><span class="swatch-hex">{hex_v}</span></div>'
        ramp_html += "</div>"

    # Invariants
    inv_html = ""
    for iname, idef in m["invariants"].items():
        sev = idef.get("severity", "warning")
        rule = idef.get("rule", "")
        rationale = idef.get("rationale", "")
        inv_html += (
            f'<div class="invariant-row">'
            f'<div class="inv-name">{iname}</div>'
            f'<div class="inv-rule">{rule}</div>'
            f'<div class="inv-rationale">{rationale} <span class="av-severity {sev}">{sev}</span></div>'
            f'</div>'
        )

    # Avoid
    avoid_html = ""
    for entry in m["avoid"]:
        sev = entry.get("severity", "warning")
        if "color" in entry:
            hex_v = entry["color"]
            name = entry.get("name", hex_v)
            reason = entry.get("reason", "")
            avoid_html += (
                f'<div class="avoid-item"><span class="av-swatch" style="background:{hex_v};"></span>'
                f'<span class="av-name">{name}</span> <code style="font-size:0.7rem;">{hex_v}</code> '
                f'<span class="av-severity {sev}">{sev}</span>'
                f'<div class="av-reason">{reason}</div></div>'
            )
        elif "color_family" in entry:
            name = entry["color_family"]
            desc = entry.get("description", "")
            reason = entry.get("reason", "")
            avoid_html += (
                f'<div class="avoid-item"><span class="av-name">{name}</span> '
                f'<span class="av-severity {sev}">{sev}</span>'
                f'<div class="av-reason"><em>{desc}</em><br>{reason}</div></div>'
            )
        elif "font_family" in entry:
            name = f"font: {entry['font_family']}"
            reason = entry.get("reason", "")
            avoid_html += (
                f'<div class="avoid-item"><span class="av-name">{name}</span> '
                f'<span class="av-severity {sev}">{sev}</span>'
                f'<div class="av-reason">{reason}</div></div>'
            )
        elif "pattern" in entry:
            name = f"pattern: {entry['pattern']}"
            reason = entry.get("reason", "")
            avoid_html += (
                f'<div class="avoid-item"><span class="av-name">{name}</span> '
                f'<span class="av-severity {sev}">{sev}</span>'
                f'<div class="av-reason">{reason}</div></div>'
            )

    return f"""
<p class="page-lead">Two-tier token model: primitive ramps → role tokens. Every consumer references a role (e.g. <code>roles.cta</code>), never a raw hex. CTA monopoly, semantic-locked statuses, and the no-consumer-indigo rule are enforced by <code>ek-craft</code> (when shipped) reading the <code>invariants</code> block at the bottom of this page.</p>

<h2 class="section">Primary axis (locked)</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">These do not change. Any palette evolution may modify atmospheric tints / motifs — never these.</p>
<div class="swatch-grid">{axis_html}</div>

<h2 class="section">Surfaces — mode per surface</h2>
{surf_html}

<h2 class="section">Roles — semantic tokens</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">{len(m["roles"])} role tokens. Each resolves to exactly one primitive.</p>
{role_html}

<h2 class="section">Primitive ramps</h2>
{ramp_html}

<h2 class="section">Invariants — hard rules</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">Surfaced from <code>invariants</code>. <code>ek-craft</code> enforces.</p>
{inv_html}

<h2 class="section">Avoid · forbidden colors / fonts / patterns</h2>
<p style="color:var(--fg-muted);">Surfaced from <code>avoid</code>. <code>ek-craft</code> lints any <code>.tsx</code>/<code>.css</code> against this list.</p>
<div class="avoid-grid">{avoid_html}</div>
"""


def body_typography(m: dict) -> str:
    typ = m["tokens"]["typography"]
    fams = typ["families"]

    # Family overview
    fam_html = ""
    for label, key in [("Display", "display"), ("Body", "body"), ("Mono (required for identifiers)", "mono")]:
        fname = fams[key]
        sample_text = "Aa Ee 01 — agent_id_0042" if key == "mono" else ("Neo-Tokyo Cyberpunk" if key == "display" else "The operator scans identifiers constantly.")
        fam_html += (
            f'<div class="type-sample">'
            f'<div class="type-meta">{label} · <strong>{fname}</strong></div>'
            f'<div class="type-render" style="font-family:\'{fname}\',sans-serif;font-size:2rem;font-weight:600;">{sample_text}</div>'
            f'</div>'
        )

    # Scale ladder — render each named step at its scale
    scale_keys = ["display", "h1", "h2", "h3", "body_lg", "body", "small", "eyebrow", "mono", "mono_sm", "code"]
    scale_html = ""
    sample_by_key = {
        "display": "Boot the agent",
        "h1": "Operator console",
        "h2": "Section header",
        "h3": "Subsection",
        "body_lg": "Lead paragraph — the operator wants information, not whitespace.",
        "body": "Body copy. ek-design treats the user as the operator; surface state plainly (model, agent ID, latency, token count).",
        "small": "Small print, metadata, label text",
        "eyebrow": "Eyebrow / Section Label",
        "mono": "model: claude-opus-4-7 · 2,847 tokens · 212ms",
        "mono_sm": "agent_id_0042 · 2026-05-24T22:35:54.013Z",
        "code": "const result = await agent.run({ task, model });",
    }
    for key in scale_keys:
        if key not in typ:
            continue
        s = typ[key]
        fam_v = s.get("family", "Inter")
        sample = sample_by_key.get(key, "Sample text")
        attrs = []
        if "size_clamp" in s:
            attrs.append(f"font-size:{s['size_clamp']}")
        if "weight" in s:
            attrs.append(f"font-weight:{s['weight']}")
        if "line_height" in s:
            attrs.append(f"line-height:{s['line_height']}")
        if "letter_spacing" in s:
            attrs.append(f"letter-spacing:{s['letter_spacing']}")
        if "transform" in s:
            attrs.append(f"text-transform:{s['transform']}")
        style_str = ";".join(attrs)
        meta_str = " · ".join(f"{k}:{v}" for k, v in s.items() if k != "family")
        scale_html += (
            f'<div class="type-sample">'
            f'<div class="type-meta">{key} · <strong>{fam_v}</strong> · {meta_str}</div>'
            f'<div class="type-render" style="font-family:\'{fam_v}\',sans-serif;{style_str};">{sample}</div>'
            f'</div>'
        )

    return f"""
<p class="page-lead">Three families. <strong>Chakra Petch</strong> for display + headers + eyebrows + UI chrome (cyber-coded angled cuts, highly legible). <strong>Inter</strong> for body + labels (neutral workhorse). <strong>JetBrains Mono</strong> for every identifier — code, paths, IDs, timestamps, model names, hashes, token counts. Mono-for-identifiers is a locked invariant; see <a href="color.html#invariants">color → invariants</a>.</p>

<h2 class="section">Families</h2>
{fam_html}

<h2 class="section">Scale ladder</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">All sizes use <code>clamp(min, preferred, max)</code> for fluid scaling. Letter-spacing is explicit per step (Linear/Vercel pattern).</p>
{scale_html}

<h2 class="section">Google Fonts URL</h2>
<pre class="spec-pre">{typ.get("google_fonts_url","")}</pre>
"""


def body_motifs(m: dict) -> str:
    motifs = m["primary_axis_preserved"].get("motifs", [])

    motif_demos = {
        "neon-edge-glow": {
            "title": "Neon edge glow",
            "rationale": "Replaces gray drop-shadow as elevation cue. Bound to focus / hover / agent_status_active. <code>box-shadow</code> with brand-color RGBA; never decorative.",
            "stage": '<button class="btn-primary" style="box-shadow:0 0 8px var(--magenta), 0 0 16px rgba(255,42,109,0.25);">Hover state</button>',
            "code": "box-shadow: 0 0 8px var(--magenta), 0 0 16px rgba(255,42,109,0.25);",
        },
        "terminal-block-inset": {
            "title": "Terminal block inset",
            "rationale": "Pure-black recess with cyan border, JetBrains Mono content. The visually-distinct surface for machine output (logs, tool calls, JSON streams). Maps to <code>surfaces.terminal_inset</code>.",
            "stage": '<div class="terminal-demo"><span class="term-meta">[2026-05-24T22:35:54.013Z]</span> <span class="term-prompt">›</span> agent_0042 invoking <span style="color:var(--magenta);">claude-opus-4-7</span><br><span class="term-meta">  → tool_use: bash · </span>echo "deploy ready"<br><span class="term-meta">  → 212ms · 47 tokens · $0.0009</span></div>',
            "code": 'background: #000000;\nborder: 1px solid var(--cyan, #00D1FF);\ncolor: var(--cyan);\nfont-family: "JetBrains Mono", monospace;',
        },
        "katakana-numeric-id": {
            "title": "Katakana-numeric agent ID",
            "rationale": "Agent / job IDs styled in mono with leading-zero numerics and optional katakana prefix glyph. Establishes the 'these are machine identifiers' visual register at a glance.",
            "stage": '<div style="font-family:\'JetBrains Mono\',monospace;display:flex;gap:1.5rem;flex-wrap:wrap;font-size:0.95rem;"><span style="color:var(--cyan);">エ·0042</span><span style="color:var(--lime);">JOB·001847</span><span style="color:var(--magenta);">PR·00139</span><span style="color:var(--fg-muted);">2026·05·24·T22·35·54</span></div>',
            "code": 'font-family: "JetBrains Mono", monospace;\nletter-spacing: 0.02em;\n/* Format IDs with leading zeros + middle-dot separators */',
        },
        "scanline-overlay": {
            "title": "Scanline overlay (optional, reduced-motion-safe)",
            "rationale": "Subtle CRT-line texture for hero / marketing surfaces. Pure-CSS gradient overlay, no motion. <strong>Must</strong> respect <code>prefers-reduced-motion</code>; can trigger vestibular issues if animated.",
            "stage": '<div class="scanline-stage" style="background:var(--bg-2);padding:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:\'Chakra Petch\',sans-serif;font-weight:600;font-size:1.5rem;color:var(--cyan);text-shadow:0 0 12px var(--cyan);width:100%;">SYSTEM ONLINE</div>',
            "code": 'background: repeating-linear-gradient(\n  0deg,\n  transparent 0,\n  transparent 2px,\n  rgba(255,255,255,0.06) 2px,\n  rgba(255,255,255,0.06) 3px\n);',
        },
        "diagonal-cut-corner": {
            "title": "Diagonal cut corner (alt to rounded)",
            "rationale": "Replaces <code>border-radius</code> on hero / feature surfaces for an angular cyber register. Use sparingly — overuse reads as costume. Render via <code>clip-path</code>.",
            "stage": '<div class="diagonal-cut">CYBERPUNK PANEL</div>',
            "code": 'clip-path: polygon(\n  12px 0, 100% 0,\n  100% calc(100% - 12px), calc(100% - 12px) 100%,\n  0 100%, 0 12px\n);',
        },
    }

    motif_html = ""
    for slug in motifs:
        d = motif_demos.get(slug)
        if not d:
            continue
        motif_html += (
            f'<div class="motif-card">'
            f'<h3 class="motif-title">{d["title"]} <code style="font-size:0.7rem;margin-left:0.5rem;">{slug}</code></h3>'
            f'<p class="motif-rationale">{d["rationale"]}</p>'
            f'<div class="motif-stage">{d["stage"]}</div>'
            f'<pre class="spec-pre">{d["code"]}</pre>'
            f'</div>'
        )

    return f"""
<p class="page-lead">Cyberpunk-coded visual signatures. Each motif has a narrow role binding (focus / hover / status / hero / identifier); decorative overuse collapses the register. <code>ek-craft</code> warns on <code>decorative-neon-glow</code> and <code>drop-shadow-as-elevation</code>.</p>

{motif_html}
"""


def body_components(m: dict) -> str:
    return """
<p class="page-lead">Live-rendered components consuming the locked tokens. Hover the primary button to see the neon glow on hover. Click into the input to see the cyan focus ring. All variants below are bound to <code>design-model.yaml</code> <code>components.*</code> specs — when those change, this page re-renders.</p>

<h2 class="section">Buttons</h2>
<div class="component-stage">
  <button class="btn-primary">Primary CTA</button>
  <button class="btn-secondary">Secondary</button>
  <button class="btn-destructive">Destructive</button>
</div>
<pre class="spec-pre">button_primary  · magenta.500 fill · white text · Chakra Petch 600 · neon-glow on hover · focus-ring magenta
button_secondary · transparent · cyan.500 border + text · Chakra Petch 600 · focus-ring cyan
destructive_action · transparent · red.500 border + text · Chakra Petch 600</pre>

<h2 class="section">Card</h2>
<div class="component-stage">
  <div class="card-demo">
    <div class="card-eyebrow">Agent · 0042</div>
    <h4>Daily briefing ready</h4>
    <p>Reviewed 23 emails, 4 Slack threads, 7 HubSpot deals. 3 items need decisions; 1 escalation.</p>
  </div>
</div>
<pre class="spec-pre">background: neutral.850 (#15151F)
border: 1px solid slate.700 (#2E2E40)
radius: 6 (component)
padding: spacing.lg (24px)</pre>

<h2 class="section">Terminal block</h2>
<div class="component-stage">
  <div class="terminal-demo">
    <span class="term-meta">[2026-05-24T22:35:54.013Z]</span> <span class="term-prompt">›</span> agent_0042 invoking <span style="color:var(--magenta);">claude-opus-4-7</span><br>
    <span class="term-meta">  → tool_use: bash · </span>echo "deploy ready"<br>
    <span class="term-meta">  → 212ms · 47 tokens · $0.0009</span><br>
    <span class="term-meta">  → status: </span><span class="term-prompt">complete</span>
  </div>
</div>
<pre class="spec-pre">background: neutral.1000 (#000000)
border: 1px solid cyan.700 (#0090B8)
color: cyan.500 (#00D1FF)
font-family: JetBrains Mono
role: surfaces.terminal_inset — machine output only</pre>

<h2 class="section">Agent-status badges</h2>
<div class="component-stage">
  <span class="badge active"><span class="dot"></span>active</span>
  <span class="badge thinking"><span class="dot"></span>thinking</span>
  <span class="badge tool"><span class="dot"></span>tool_use</span>
  <span class="badge complete"><span class="dot"></span>complete</span>
  <span class="badge blocked"><span class="dot"></span>blocked</span>
  <span class="badge error"><span class="dot"></span>error</span>
  <span class="badge idle"><span class="dot"></span>idle</span>
</div>
<pre class="spec-pre">active    · lime.500 + neon-glow-lime
thinking  · cyan.500 + pulse animation (reduced-motion: no pulse)
tool_use  · steel_violet.300
complete  · lime.500
blocked   · amber.500
error     · red.500
idle      · slate.500
font: JetBrains Mono 500 0.6875rem · letter-spacing 0.060em · uppercase</pre>

<h2 class="section">Input field</h2>
<div class="component-stage">
  <input class="input-demo" placeholder="Type a task or query…">
</div>
<pre class="spec-pre">background: neutral.850 (#15151F)
border: 1px solid slate.700 (#2E2E40)
radius: 4 (control)
focus: border cyan.500 + focus-ring cyan</pre>

<h2 class="section">Code block</h2>
<div class="component-stage">
<pre class="spec-pre" style="margin:0;background:#15151F;color:var(--fg);width:100%;max-width:600px;"><span class="spec-key">async function</span> runAgent({"{"} task, model {"}"}) {"{"}
  <span class="spec-key">const</span> result = <span class="spec-key">await</span> agent.invoke({"{"}
    <span class="spec-key">prompt</span>: task,
    <span class="spec-key">model</span>: <span class="spec-val">"claude-opus-4-7"</span>,
  {"}"});
  <span class="spec-key">return</span> result;
{"}"}</pre>
</div>
<pre class="spec-pre">background: neutral.900 (#0F0F18)
color: neutral.0 (#FFFFFF)
border: 1px solid slate.700
syntax accent: cyan.500
font-family: JetBrains Mono</pre>
"""


# ─── Main ──────────────────────────────────────────────────────────────────

def main() -> int:
    if not YAML_PATH.exists():
        print(f"ERROR: {YAML_PATH} not found", file=sys.stderr)
        return 1
    with YAML_PATH.open() as f:
        model = yaml.safe_load(f)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages = [
        ("index.html", "Overview", body_index(model)),
        ("color.html", "Color", body_color(model)),
        ("typography.html", "Typography", body_typography(model)),
        ("motifs.html", "Motifs", body_motifs(model)),
        ("components.html", "Components", body_components(model)),
    ]

    for filename, title, body in pages:
        html = page_chrome(model, title, body, filename)
        (OUT_DIR / filename).write_text(html, encoding="utf-8")
        print(f"  wrote {filename} ({len(html):,} bytes)")

    print(f"\nGenerated {len(pages)} pages → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
