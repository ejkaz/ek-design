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
    ("cockpit.html", "Cockpit"),
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
  /* v0.2 — Dark Ledger / Neon Operator palette */
  --bg: #070711;
  --bg-1: #10101A;
  --bg-2: #171727;
  --bg-3: #23233A;
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
  --gain: #4ADE80;
  --loss: #F87171;
  --watch: #FBBF24;
  --info-blue: #60A5FA;
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

.diagonal-cut { background: var(--bg-2); border: 1px solid #2C2A45;
  padding: 24px 28px; color: var(--fg); font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px); }

/* ★ v0.2 finance cockpit components ─────────────────────────────────── */

.kpi-card { background: var(--bg-2); border: 1px solid #2C2A45; border-radius: 6px;
  padding: 16px; min-width: 180px; }
.kpi-card .kpi-label { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--fg-muted); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.kpi-card .kpi-label .dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.kpi-card .kpi-value { font-family: 'JetBrains Mono', monospace; font-weight: 700;
  font-size: 1.875rem; line-height: 1.0; letter-spacing: -0.010em; color: var(--fg);
  font-feature-settings: "tnum"; }
.kpi-card .kpi-delta { font-family: 'JetBrains Mono', monospace; font-weight: 600;
  font-size: 0.78125rem; margin-top: 6px; font-feature-settings: "tnum"; }
.kpi-card .kpi-delta.gain { color: var(--gain); }
.kpi-card .kpi-delta.loss { color: var(--loss); }
.kpi-card.state-watch { border-color: var(--watch); }
.kpi-card.state-breach { border-color: var(--red); }
.kpi-card.state-agent { border-color: var(--magenta);
  box-shadow: 0 0 12px rgba(255,42,109,0.4), 0 0 24px rgba(255,42,109,0.2); }

.finance-panel { background: var(--bg-2); border: 1px solid var(--border-soft);
  border-radius: 6px; padding: 16px; margin-bottom: var(--gap-sm); }
.finance-panel.active { box-shadow: 0 0 12px rgba(255,42,109,0.4), 0 0 24px rgba(255,42,109,0.2); }
.finance-panel .fp-header { display: flex; justify-content: space-between;
  align-items: center; padding-bottom: 12px; border-bottom: 1px solid var(--border-soft);
  margin-bottom: 12px; }
.finance-panel .fp-title { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 1rem; }
.finance-panel .fp-meta { font-family: 'JetBrains Mono', monospace; font-size: 0.6875rem;
  color: var(--fg-muted); display: flex; gap: 12px; }
.finance-panel .fp-meta .trace-link { color: var(--cyan); cursor: pointer; }

.variance-row { display: grid;
  grid-template-columns: 1.5fr repeat(5, 1fr); gap: 12px; padding: 8px 0;
  border-bottom: 1px solid var(--border-soft); font-family: 'JetBrains Mono', monospace;
  font-size: 0.8125rem; align-items: center; font-feature-settings: "tnum"; }
.variance-row.header { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.7rem; letter-spacing: 0.10em; text-transform: uppercase; color: var(--fg-muted); }
.variance-row .label { font-family: 'Inter', sans-serif; font-size: 0.85rem; color: var(--fg); }
.variance-row .num { text-align: right; }
.variance-row .num.budget { color: var(--fg-muted); }
.variance-row .num.forecast { color: var(--fg-muted); }
.variance-row .num.gain { color: var(--gain); }
.variance-row .num.loss { color: var(--loss); }

.data-badge { display: inline-flex; align-items: center; gap: 4px; padding: 1px 6px;
  border: 1px solid currentColor; border-radius: 999px; font-family: 'JetBrains Mono', monospace;
  font-size: 0.625rem; text-transform: uppercase; letter-spacing: 0.060em; }
.data-badge .dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.data-badge.live { color: var(--lime); }
.data-badge.synced { color: var(--cyan); }
.data-badge.stale { color: var(--amber); }
.data-badge.failed { color: var(--red); }
.data-badge.manual { color: var(--magenta); }

.trace-rail { display: flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: var(--cyan); }
.trace-rail .crumb { padding: 1px 6px; border: 1px solid rgba(0,209,255,0.3);
  border-radius: 3px; }
.trace-rail .arrow { color: rgba(0,209,255,0.5); }

.command-bar { background: var(--bg-1); border: 1px solid #2C2A45;
  border-radius: 8px; padding: 16px; display: flex; gap: 12px; align-items: center;
  max-width: 720px; }
.command-bar .agent-status { font-family: 'JetBrains Mono', monospace; font-size: 0.6875rem;
  color: var(--magenta); text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
.command-bar input { flex: 1; background: transparent; border: 0; color: var(--fg);
  font-family: 'Inter', sans-serif; font-size: 0.9375rem; outline: none; }
.command-bar input::placeholder { color: var(--fg-muted); }
.command-bar .tool-chip { display: inline-flex; gap: 4px; padding: 2px 8px;
  background: var(--bg-2); border: 1px solid rgba(0,209,255,0.4); color: var(--cyan);
  font-family: 'JetBrains Mono', monospace; font-size: 0.625rem;
  border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; }
.command-bar button { background: var(--magenta); color: var(--fg); border: 0;
  padding: 8px 16px; border-radius: 4px; font-family: 'Chakra Petch', sans-serif;
  font-weight: 600; font-size: 0.8125rem; letter-spacing: 0.02em; cursor: pointer; }

.approval-card { background: var(--bg-2); border: 1px dashed var(--amber);
  border-radius: 6px; padding: 16px; max-width: 480px; }
.approval-card .ac-header { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.7rem; letter-spacing: 0.080em; text-transform: uppercase; color: var(--amber);
  margin-bottom: 8px; }
.approval-card h4 { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 1rem; margin: 0 0 8px 0; }
.approval-card .ac-evidence { background: #000000; border: 1px solid #0090B8;
  border-radius: 2px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: var(--cyan); margin: 8px 0; }
.approval-card .ac-impact { font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem;
  margin: 8px 0; font-feature-settings: "tnum"; }
.approval-card .ac-impact .gain { color: var(--gain); }
.approval-card .ac-impact .loss { color: var(--loss); }
.approval-card .ac-actions { display: flex; gap: 8px; margin-top: 12px; }
.approval-card .ac-actions .approve { background: var(--magenta); color: var(--fg); border: 0; padding: 6px 12px; border-radius: 4px;
  font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 0.78125rem; cursor: pointer; }
.approval-card .ac-actions .reject { background: transparent; color: var(--red);
  border: 1px solid var(--red); padding: 6px 12px; border-radius: 4px;
  font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 0.78125rem; cursor: pointer; }
.approval-card .ac-actions .inspect { background: transparent; color: var(--cyan);
  border: 1px solid var(--cyan); padding: 6px 12px; border-radius: 4px;
  font-family: 'Chakra Petch', sans-serif; font-weight: 600; font-size: 0.78125rem; cursor: pointer; }

/* Forecast confidence halo */
.confidence-halo-amber { box-shadow: inset 0 0 0 1px rgba(255,184,0,0.5); }
.confidence-halo-red { box-shadow: inset 0 0 0 1px rgba(255,0,60,0.5); }

/* Sample cockpit layout */
.cockpit-frame { background: var(--bg); border: 1px solid #2C2A45; border-radius: 8px;
  overflow: hidden; }
.cockpit-topbar { background: var(--bg-1); border-bottom: 1px solid var(--border-soft);
  padding: 10px 16px; display: flex; gap: 24px; align-items: center;
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; }
.cockpit-topbar .brand { font-family: 'Chakra Petch', sans-serif; font-weight: 700;
  font-size: 0.85rem; letter-spacing: 0.08em; color: var(--magenta);
  text-shadow: 0 0 6px rgba(255,42,109,0.3); }
.cockpit-topbar .topbar-meta { display: flex; gap: 16px; margin-left: auto; color: var(--fg-muted); }
.cockpit-topbar .topbar-meta .live { color: var(--lime); }
.cockpit-body { display: grid; grid-template-columns: 200px 1fr 280px; min-height: 460px; }
.cockpit-rail { background: var(--bg-1); border-right: 1px solid var(--border-soft);
  padding: 16px 8px; display: flex; flex-direction: column; gap: 4px; }
.cockpit-rail .rail-item { padding: 6px 12px; font-family: 'Chakra Petch', sans-serif;
  font-weight: 500; font-size: 0.78125rem; color: var(--fg-muted); border-radius: 4px;
  border-left: 2px solid transparent; }
.cockpit-rail .rail-item.active { color: var(--fg); border-left-color: var(--magenta);
  background: rgba(255,42,109,0.08); }
.cockpit-main { padding: 16px; overflow: auto; }
.cockpit-kpi-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px; margin-bottom: 16px; }
.cockpit-kpi-strip .kpi-card { padding: 10px 12px; min-width: 0; }
.cockpit-kpi-strip .kpi-value { font-size: 1.25rem; }
.cockpit-feed { background: var(--bg-1); border-left: 1px solid var(--border-soft);
  padding: 16px; overflow: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; }
.cockpit-feed .feed-title { font-family: 'Chakra Petch', sans-serif; font-weight: 600;
  font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--fg-muted); margin-bottom: 12px; }
.cockpit-feed .feed-event { padding: 6px 0; border-bottom: 1px solid var(--border-soft);
  line-height: 1.5; }
.cockpit-feed .feed-event .ts { color: var(--fg-dim); }
.cockpit-feed .feed-event.command { color: var(--magenta); }
.cockpit-feed .feed-event.sync { color: var(--cyan); }
.cockpit-feed .feed-event.approval { color: var(--amber); }
.cockpit-feed .feed-event.complete { color: var(--lime); }
.cockpit-feed .feed-event.error { color: var(--red); }

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
    thesis = m.get("thesis", "")
    thesis_one_line = m.get("thesis_one_line", "")
    cards = ""
    for href, title, desc in [
        ("color.html", "Color", "Primary axis, 6 surfaces, 9 primitive ramps (incl. new finance directionality), 100 role tokens, 15 invariants, 29 avoid entries."),
        ("typography.html", "Typography", "Chakra Petch / Inter / JetBrains Mono. Brand portal vs cockpit modes documented. 5 new finance type roles with tabular numerals."),
        ("motifs.html", "Motifs", "13 motifs: 5 v0.1 (neon edge glow, terminal block, katakana-numeric ID, scanline, diagonal cut) + 8 v0.2 finance (dark-ledger-panel, neon-operator-layer, trace-rail, agent-event-feed, forecast-confidence-halo, board-safe-mode, executive-command-state, machine-identifier-strip)."),
        ("components.html", "Components", "16 components: 6 v0.1 + 10 v0.2 finance cockpit (kpi_card, finance_panel, agent_command_bar, agent_status_badge expanded, data_freshness_badge, source_trace_row, variance_row, approval_card, agent_log, board_export_preview) — all live."),
        ("cockpit.html", "Cockpit", "Sample FinanceOS layout demonstrating the Dark Ledger / Neon Operator thesis applied to a finance cockpit. Brand reference only — actual cepsra implementation lives in a separate thread."),
    ]:
        cards += f'<a href="{href}" style="text-decoration:none;color:inherit;"><div class="surface-card"><h3>{title}</h3><p class="surface-rationale">{desc}</p></div></a>'

    # Product metaphors + what-this-is-not
    metaphor_items = "".join(
        f'<li style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;color:var(--fg-muted);margin-bottom:0.4rem;">{x}</li>'
        for x in m.get("product_metaphor", [])
    )
    not_items = "".join(
        f'<li style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:var(--fg-muted);margin-bottom:0.4rem;">{x}</li>'
        for x in m.get("what_this_is_not", [])
    )

    return f"""
<p class="page-lead">ek-design brand SSoT, rendered live from <code>design-model.yaml</code>. Every swatch, token, type sample, motif demo, and component preview on this site is auto-generated. To iterate, edit the YAML and run <code>python3 scripts/generate-brand-portal.py</code>.</p>

<div class="callout">
  <div class="eyebrow">Active version</div>
  <p style="margin:0;">Schema <strong>{meta['version']}</strong> · Brand version <strong>{meta['brand_version']}</strong> · Status <strong>{meta.get('status','—')}</strong> · Updated <strong>{meta.get('updated','—')}</strong> by <strong>{meta.get('updated_by','—')}</strong>.</p>
</div>

<h2 class="section">Thesis · {thesis}</h2>
<p style="font-family:'Chakra Petch',sans-serif;font-size:1.5rem;font-weight:600;letter-spacing:-0.010em;color:var(--magenta);text-shadow:0 0 12px rgba(255,42,109,0.3);max-width:60ch;margin-bottom:var(--gap-md);">{thesis_one_line}</p>
<div class="callout cyan" style="margin-bottom:var(--gap-md);">
<p style="margin:0;font-size:0.95rem;line-height:1.65;">
<strong style="color:var(--cyan);">Layer separation:</strong>
the static finance truth layer is dark and sober · the data lineage layer is <span style="color:var(--cyan);">cyan</span> · the agentic execution layer is <span style="color:var(--magenta);">magenta</span> · CFO attention is <span style="color:var(--amber);">amber</span> · health and completion are <span style="color:var(--lime);">lime</span> · true risk is <span style="color:var(--red);">red</span> · atmosphere is steel-violet (rarely text).
</p>
</div>

<h2 class="section">Product metaphor</h2>
<ul style="list-style:none;padding:0;margin:0 0 var(--gap-md) 0;">{metaphor_items}</ul>

<h2 class="section">What this is not</h2>
<ul style="list-style:none;padding:0;margin:0 0 var(--gap-md) 0;">{not_items}</ul>

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

    # Primary axis swatches — manually pick the labelled ones from the axis dict.
    # v0.2 key names: magenta_command, cyan_trace, lime_health (renamed from v0.1).
    axis_pairs = [
        ("Background", axis["background"], "Default app + cockpit + marketing surface (deep violet-black)"),
        ("Panel", axis["panel"], "Layered finance panel (surface_2)"),
        ("Off-white", axis["off_white"], "Inverted (light-mode opt-in)"),
        ("White", axis["white"], "Text on dark"),
        ("Magenta Command", axis.get("magenta_command", axis.get("magenta_cta", "")), "Primary CTA + agentic command monopoly"),
        ("Cyan Trace", axis.get("cyan_trace", axis.get("cyan_secondary", "")), "Trace / lineage / inspectability / secondary"),
        ("Lime Health", axis.get("lime_health", axis.get("lime_alive", "")), "Success + completion + agent active"),
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

<h2 class="section">Finance directionality (★ v0.2)</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">Semantic colors for variance / delta / financial directionality. <strong>Distinct from agent state.</strong> Locked invariant <code>finance_directionality_locked</code> enforces these appear ONLY in variance, delta, or financial-health contexts — never as brand accent, never as decorative chart color, never as a button background.</p>
<div class="swatch-grid">
  <div class="swatch" style="background:#4ADE80;color:#0A0A14;"><div><div class="swatch-name">Gain</div><span class="swatch-hex">#4ADE80</span></div><div class="swatch-role">Positive variance · favorable · under budget · on target</div></div>
  <div class="swatch" style="background:#F87171;color:#0A0A14;"><div><div class="swatch-name">Loss</div><span class="swatch-hex">#F87171</span></div><div class="swatch-role">Negative variance · unfavorable · over budget · miss</div></div>
  <div class="swatch" style="background:#FBBF24;color:#0A0A14;"><div><div class="swatch-name">Watch</div><span class="swatch-hex">#FBBF24</span></div><div class="swatch-role">Approaching threshold · forecast uncertainty · stale data</div></div>
  <div class="swatch" style="background:#60A5FA;color:#0A0A14;"><div><div class="swatch-name">Info Blue</div><span class="swatch-hex">#60A5FA</span></div><div class="swatch-role">Calm informational · model version · environment · NEVER as link (that's cyan)</div></div>
</div>

<h2 class="section">Surface architecture (★ v0.2)</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">Four layered dark surfaces, all violet-undertone, used as a depth stack. Default border <code>#2C2A45</code> (steel-violet-tinted).</p>
<div class="swatch-grid">
  <div class="swatch" style="background:#070711;color:#F0F0F5;"><div><div class="swatch-name">bg (neutral.950)</div><span class="swatch-hex">#070711</span></div><div class="swatch-role">App / cockpit / marketing default</div></div>
  <div class="swatch" style="background:#10101A;color:#F0F0F5;"><div><div class="swatch-name">surface_1 (neutral.900)</div><span class="swatch-hex">#10101A</span></div><div class="swatch-role">Topbar / rail / subtle chrome</div></div>
  <div class="swatch" style="background:#171727;color:#F0F0F5;"><div><div class="swatch-name">surface_2 (neutral.850)</div><span class="swatch-hex">#171727</span></div><div class="swatch-role">Default panel chrome (finance_panel default)</div></div>
  <div class="swatch" style="background:#23233A;color:#F0F0F5;"><div><div class="swatch-name">surface_3 (neutral.800)</div><span class="swatch-hex">#23233A</span></div><div class="swatch-role">Selected / nested panel</div></div>
</div>

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
    scale_keys = ["display", "h1", "h2", "h3", "body_lg", "body", "small", "eyebrow", "mono", "mono_sm", "code", "kpi_value", "kpi_label", "table_numeric", "delta", "timestamp"]
    scale_html = ""
    sample_by_key = {
        "display": "Boot the agent",
        "h1": "Operator console",
        "h2": "Section header",
        "h3": "Subsection",
        "body_lg": "Lead paragraph: the operator wants information, not whitespace.",
        "body": "Body copy. ek-design treats the user as the operator; surface state plainly (model, agent ID, latency, token count).",
        "small": "Small print, metadata, label text",
        "eyebrow": "Eyebrow / Section Label",
        "mono": "model: claude-opus-4-7 · 2,847 tokens · 212ms",
        "mono_sm": "agent_id_0042 · 2026-05-24T22:35:54.013Z",
        "code": "const result = await agent.run({ task, model });",
        # ★ v0.2 finance type roles
        "kpi_value": "$12,847,392",
        "kpi_label": "ARR · annual recurring",
        "table_numeric": "1,847,392.50    2,140,000.00    -292,607.50",
        "delta": "+18.4%   -2.1%   +312bps",
        "timestamp": "2026-05-24T22:35:54.013Z · synced 12s ago",
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

    # ★ v0.2 — typography modes
    modes_html = ""
    modes = typ.get("modes", {})
    for mode_name, mode_def in modes.items():
        body_alt = f' · <em>body_alt:</em> {mode_def.get("body_alt")}' if mode_def.get("body_alt") else ""
        mono_alt = f' · <em>mono_alt:</em> {mode_def.get("mono_alt")}' if mode_def.get("mono_alt") else ""
        tnum = " · <strong>tabular numerals required</strong>" if mode_def.get("tabular_numerals_required") else ""
        modes_html += (
            f'<div class="surface-card">'
            f'<h3>{mode_name.replace("_", " ").title()}</h3>'
            f'<div class="surface-meta">display: <strong>{mode_def["display"]}</strong> · body: <strong>{mode_def["body"]}</strong> · mono: <strong>{mode_def["mono"]}</strong> · density: <strong>{mode_def["density"]}</strong>{tnum}</div>'
            f'<p class="surface-rationale">{mode_def["description"]}{body_alt}{mono_alt}</p>'
            f'</div>'
        )

    return f"""
<p class="page-lead">Three families. <strong>Chakra Petch</strong> for display + headers + eyebrows + UI chrome (cyber-coded angled cuts, highly legible). <strong>Inter</strong> for body + labels (neutral workhorse). <strong>JetBrains Mono</strong> for every identifier and every finance numeric (with tabular numerals locked via <code>font-feature-settings: "tnum"</code>). Mono-for-identifiers and tabular-numerals-for-finance are locked invariants; see <a href="color.html#invariants">color → invariants</a>.</p>

<h2 class="section">Modes (★ v0.2)</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">Same locked families, different density expectations.</p>
{modes_html}

<h2 class="section">Families</h2>
{fam_html}

<h2 class="section">Scale ladder</h2>
<p style="color:var(--fg-muted);margin-bottom:var(--gap-md);">All sizes use <code>clamp(min, preferred, max)</code> for fluid scaling. Letter-spacing is explicit per step (Linear/Vercel pattern). v0.2 adds 5 finance type roles (<code>kpi_value</code>, <code>kpi_label</code>, <code>table_numeric</code>, <code>delta</code>, <code>timestamp</code>) all with tabular numerals.</p>
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
        # ★ v0.2 finance motifs
        "dark-ledger-panel": {
            "title": "Dark Ledger Panel",
            "rationale": "The default chrome for FinanceOS surfaces. Sober finance panel: <code>surface_2</code> background, soft border, minimal glow, dense metric hierarchy. Used for P&amp;L, runway, revenue bridge, Opex, headcount, COGS, forecast variance. <strong>When to use:</strong> static finance truth display. <strong>When NOT to use:</strong> agent-active panels — those upgrade to neon-operator-layer.",
            "stage": '<div class="finance-panel" style="width:100%;max-width:480px;"><div class="fp-header"><div class="fp-title">Runway · forecast</div><div class="fp-meta"><span>FY26 Q2</span><span style="color:var(--cyan);">synced 12s ago</span><span class="trace-link">drill →</span></div></div><div style="font-family:\'JetBrains Mono\',monospace;font-feature-settings:\'tnum\';font-size:0.875rem;line-height:1.7;"><div>cash on hand:    $12,847,392</div><div>monthly burn:    <span style="color:var(--loss);">$847,212</span></div><div>runway:          <span style="color:var(--amber);">15.2 months</span></div></div></div>',
            "code": 'background: var(--surface-2, #171727);\nborder: 1px solid var(--border-soft);\nradius: 6px;\npadding: 16px;\n/* glow_default: none — sober by default */',
        },
        "neon-operator-layer": {
            "title": "Neon Operator Layer",
            "rationale": "Thin luminous overlay applied ONLY when an agent is actively acting on a surface, a command is executing, or an approval is pending. Magenta = command, cyan = trace, lime = complete. <strong>When NOT to use:</strong> as decoration on every card — violates <code>agent_command_magenta_only</code> invariant.",
            "stage": '<div class="finance-panel active" style="width:100%;max-width:480px;"><div class="fp-header"><div class="fp-title" style="color:var(--magenta);">Revenue bridge · running forecast</div><div class="fp-meta"><span class="data-badge manual"><span class="dot"></span>agent · acting</span></div></div><div style="font-family:\'JetBrains Mono\',monospace;color:var(--fg-muted);font-size:0.78rem;">claude-opus-4-7 running forecast() · 4.2k tokens · 1.8s elapsed</div></div>',
            "code": 'box-shadow: 0 0 12px rgba(255,42,109,0.4),\n            0 0 24px rgba(255,42,109,0.2);\n/* operator_layer_glow effect — used only on active surfaces */',
        },
        "trace-rail": {
            "title": "Trace Rail",
            "rationale": "Cyan micro-line breadcrumb showing source lineage / drill-through path. Answers \"where did this number come from?\" Bound to <code>cyan_for_trace_only</code> invariant. <strong>When to use:</strong> any computed financial metric. <strong>When NOT to use:</strong> as decorative accent.",
            "stage": '<div class="trace-rail"><span class="crumb">QuickBooks</span><span class="arrow">→</span><span class="crumb">P&amp;L · operating expenses</span><span class="arrow">→</span><span class="crumb">payroll</span><span class="arrow">→</span><span class="crumb">eng headcount</span></div>',
            "code": 'color: var(--cyan, #00D1FF);\nfont-family: "JetBrains Mono", monospace;\n/* crumb: border 1px solid rgba(0,209,255,0.3) */',
        },
        "agent-event-feed": {
            "title": "Agent Event Feed",
            "rationale": "Timestamped feed of tool calls, sync events, approvals, blocked tasks. Terminal-inset styling sparingly. Each event-type maps to a semantic color (command → magenta, sync → cyan, approval → amber, complete → lime, error → red).",
            "stage": '<div class="terminal-demo" style="width:100%;max-width:520px;"><div><span class="term-meta">[22:35:54]</span> <span style="color:var(--cyan);">→ sync</span>: QuickBooks · invoices · <span class="term-prompt">204 records</span></div><div><span class="term-meta">[22:35:58]</span> <span style="color:var(--magenta);">→ command</span>: run forecast() · revenue · FY26</div><div><span class="term-meta">[22:36:12]</span> <span style="color:var(--amber);">→ approval-required</span>: model update · runway recalc</div><div><span class="term-meta">[22:36:24]</span> <span class="term-prompt">→ complete</span>: forecast accepted</div></div>',
            "code": 'inherits: terminal_block\nevent_types:\n  command:           color: magenta\n  sync:              color: cyan\n  approval_request:  color: amber\n  approval_granted:  color: lime\n  error:             color: red',
        },
        "forecast-confidence-halo": {
            "title": "Forecast Confidence Halo",
            "rationale": "Subtle inset border indicating forecast confidence state. Amber halo = degraded confidence (uncertainty). Red halo = materially broken / breach threshold. <strong>When NOT to use:</strong> for any non-confidence signal — dilutes the watch semantic.",
            "stage": '<div style="display:flex;gap:12px;flex-wrap:wrap;"><div class="kpi-card confidence-halo-amber" style="min-width:160px;"><div class="kpi-label" style="color:var(--amber);"><span class="dot"></span>Forecast · Q3 ARR</div><div class="kpi-value">$14.2M</div><div class="kpi-delta gain">+8.2% · confidence: 64%</div></div><div class="kpi-card confidence-halo-red" style="min-width:160px;"><div class="kpi-label" style="color:var(--red);"><span class="dot"></span>Runway · breach</div><div class="kpi-value">9.1mo</div><div class="kpi-delta loss">-6.1mo from plan</div></div></div>',
            "code": 'confidence_halo_amber: inset 0 0 0 1px rgba(255,184,0,0.5)\nconfidence_halo_red:   inset 0 0 0 1px rgba(255,0,60,0.5)',
        },
        "board-safe-mode": {
            "title": "Board-Safe Mode",
            "rationale": "Same dark system with reduced neon for PDF exports / board screenshots / IC memo embeds. All <code>neon_glow_*</code> tokens collapse to inset 1px borders; scanlines removed; animations paused. Focus ring stays visible for accessibility. Activated via <code>.board-safe</code> body class. Bound to <code>board_safe_export_mode</code> invariant.",
            "stage": '<div style="display:flex;gap:12px;flex-wrap:wrap;"><div><div style="font-size:0.7rem;color:var(--fg-muted);font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">live cockpit</div><button class="btn-primary">Run forecast</button></div><div><div style="font-size:0.7rem;color:var(--fg-muted);font-family:\'JetBrains Mono\',monospace;margin-bottom:6px;">board-safe export</div><button style="background:transparent;color:var(--magenta);border:1px solid var(--magenta);padding:10px 20px;border-radius:4px;font-family:\'Chakra Petch\',sans-serif;font-weight:600;font-size:0.9375rem;letter-spacing:0.020em;">Run forecast</button></div></div>',
            "code": 'body.board-safe {\n  /* all effects.neon_glow_* override to inset 1px border */\n  --neon-glow-magenta: inset 0 0 0 1px var(--magenta);\n  --scanline-overlay: none;\n  --animation: none;\n}',
        },
        "executive-command-state": {
            "title": "Executive Command State",
            "rationale": "Magenta command button or command bar for high-leverage agentic actions: \"Run forecast\", \"Investigate variance\", \"Generate board memo\", \"Approve model update\", \"Reconcile source\". This is where the operator delegates to an agent. Bound to <code>agent_command_magenta_only</code>.",
            "stage": '<div class="command-bar"><span class="agent-status">agent · ready</span><input placeholder="Run forecast for FY26 Q3 ARR including new SDR hires" /><span class="tool-chip">qb</span><span class="tool-chip">forecast</span><button>Run</button></div>',
            "code": 'background: var(--bg-1);\nborder: 1px solid #2C2A45;\nradius: 8px;\nprimary_action: background magenta · color white',
        },
        "machine-identifier-strip": {
            "title": "Machine Identifier Strip",
            "rationale": "Compact monospace strip displaying agent IDs / model version / source freshness / period close status / environment metadata. Usually sits in topbar or page header. Mono-for-identifiers invariant locks the typography.",
            "stage": '<div style="background:var(--bg-1);border:1px solid #2C2A45;border-radius:6px;padding:10px 16px;display:flex;gap:20px;flex-wrap:wrap;font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;"><span style="color:var(--fg-muted);">env:</span><span>prod</span><span style="color:var(--fg-muted);">model:</span><span style="color:var(--magenta);">claude-opus-4-7</span><span style="color:var(--fg-muted);">period:</span><span>FY26·Q2·CLOSED</span><span style="color:var(--fg-muted);">last sync:</span><span style="color:var(--lime);">12s ago</span><span style="color:var(--fg-muted);">agent:</span><span style="color:var(--cyan);">エ·0042</span></div>',
            "code": 'font-family: "JetBrains Mono", monospace;\nfont-size: 0.72rem;\n/* identifiers in magenta (model) / lime (live) / cyan (agent) / fg (literal) */',
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
<pre class="spec-pre">background: neutral.900 (#10101A)
color: neutral.0 (#FFFFFF)
border: 1px solid neutral.700 (#2C2A45)
syntax accent: cyan.500
font-family: JetBrains Mono</pre>

<!-- ★ v0.2 finance cockpit components ───────────────────────────────── -->

<h2 class="section">KPI card (★ v0.2)</h2>
<div class="component-stage">
  <div class="kpi-card">
    <div class="kpi-label"><span class="dot" style="color:var(--lime);"></span>Cash · on hand</div>
    <div class="kpi-value">$12.8M</div>
    <div class="kpi-delta gain">+8.4% MoM</div>
  </div>
  <div class="kpi-card state-watch">
    <div class="kpi-label" style="color:var(--amber);"><span class="dot"></span>Runway · forecast</div>
    <div class="kpi-value">15.2mo</div>
    <div class="kpi-delta loss">-1.8mo vs plan</div>
  </div>
  <div class="kpi-card state-breach">
    <div class="kpi-label" style="color:var(--red);"><span class="dot"></span>Covenant · breach</div>
    <div class="kpi-value">62%</div>
    <div class="kpi-delta loss">7pp over threshold</div>
  </div>
  <div class="kpi-card state-agent">
    <div class="kpi-label" style="color:var(--magenta);"><span class="dot"></span>Agent · recomputing ARR</div>
    <div class="kpi-value">$14.2M</div>
    <div class="kpi-delta gain">+8.2% confidence: 64%</div>
  </div>
</div>
<pre class="spec-pre">label:   kpi_label (Chakra Petch 600 · 0.72rem · letter-spacing 0.14em · uppercase)
value:   kpi_value (JetBrains Mono 700 · 1.875rem · tnum)
delta:   delta (JetBrains Mono 600 · tnum · color_gain finance.gain / color_loss finance.loss)
state:   healthy (lime) · watch (amber border) · breach (red border) · agent_active (magenta border + neon-glow)</pre>

<h2 class="section">Finance panel (★ v0.2)</h2>
<div class="component-stage">
  <div class="finance-panel" style="width:100%;max-width:520px;">
    <div class="fp-header">
      <div class="fp-title">Operating expense · FY26 Q2</div>
      <div class="fp-meta">
        <span class="data-badge synced"><span class="dot"></span>synced 12s ago</span>
        <span class="trace-link">drill →</span>
      </div>
    </div>
    <div class="variance-row header">
      <div>Line</div><div class="num">Actual</div><div class="num">Budget</div><div class="num">Forecast</div><div class="num">Var $</div><div class="num">Var %</div>
    </div>
    <div class="variance-row">
      <div class="label">Payroll · Engineering</div>
      <div class="num">847,212</div>
      <div class="num budget">820,000</div>
      <div class="num forecast">840,000</div>
      <div class="num loss">-27,212</div>
      <div class="num loss">-3.3%</div>
    </div>
    <div class="variance-row">
      <div class="label">AWS · compute</div>
      <div class="num">142,847</div>
      <div class="num budget">160,000</div>
      <div class="num forecast">150,000</div>
      <div class="num gain">+17,153</div>
      <div class="num gain">+10.7%</div>
    </div>
    <div class="variance-row">
      <div class="label">AI · model spend</div>
      <div class="num">28,471</div>
      <div class="num budget">22,000</div>
      <div class="num forecast">26,000</div>
      <div class="num loss">-6,471</div>
      <div class="num loss">-29.4%</div>
    </div>
  </div>
</div>
<pre class="spec-pre">background:    surface_2 (neutral.850, #171727)
border:        1px solid border_soft (neutral.800, #23233A)
radius:        component (6px)
glow_default:  none  /* sober — Dark Ledger thesis */
glow_active:   operator_layer_glow  /* ONLY when agent is acting */
header:        title (Chakra Petch h3) + period (timestamp) + source_freshness (cyan) + drill_through (cyan)</pre>

<h2 class="section">Agent command bar (★ v0.2)</h2>
<div class="component-stage">
  <div class="command-bar">
    <span class="agent-status">agent · ready</span>
    <input placeholder="Run forecast for FY26 Q3 ARR including new SDR hires" />
    <span class="tool-chip">qb</span>
    <span class="tool-chip">forecast</span>
    <span class="tool-chip">hubspot</span>
    <button>Run</button>
  </div>
</div>
<pre class="spec-pre">background:     surface_1 (neutral.900, #10101A)
border:         1px solid border (neutral.700, #2C2A45)
primary_action: magenta — agentic command monopoly (locked invariant)
tool_chip:      cyan border + cyan text — trace lineage register
agent_status:   magenta mono</pre>

<h2 class="section">Agent-status badges (★ expanded v0.2)</h2>
<div class="component-stage">
  <span class="badge active"><span class="dot"></span>active</span>
  <span class="badge thinking"><span class="dot"></span>thinking</span>
  <span class="badge tool"><span class="dot"></span>tool_use</span>
  <span class="badge active" style="color:var(--magenta);box-shadow:0 0 8px var(--magenta);"><span class="dot"></span>command_active</span>
  <span class="badge complete"><span class="dot"></span>complete</span>
  <span class="badge blocked"><span class="dot"></span>blocked</span>
  <span class="badge blocked" style="border-style:dashed;"><span class="dot"></span>approval_required</span>
  <span class="badge error"><span class="dot"></span>error</span>
  <span class="badge idle"><span class="dot"></span>idle</span>
</div>
<pre class="spec-pre">active            · lime  + neon-glow-lime         (always-on agent alive indicator)
thinking          · cyan  + pulse animation         (model generating)
tool_use          · steel_violet.300               (tool call in progress)
command_active    · magenta + neon-glow-magenta    (★ v0.2 — agent executing a command)
complete          · lime
blocked           · amber                          (awaiting user)
approval_required · amber dashed border             (★ v0.2 — needs decision)
error             · red
idle              · slate</pre>

<h2 class="section">Data freshness badge (★ v0.2)</h2>
<div class="component-stage">
  <span class="data-badge live"><span class="dot"></span>live</span>
  <span class="data-badge synced"><span class="dot"></span>synced</span>
  <span class="data-badge stale"><span class="dot"></span>stale</span>
  <span class="data-badge failed"><span class="dot"></span>failed</span>
  <span class="data-badge manual"><span class="dot"></span>manual override</span>
</div>
<pre class="spec-pre">live             · lime    (sub-minute fresh)
synced           · cyan    (within sync interval)
stale            · amber   (past freshness threshold)
failed           · red     (last sync failed)
manual_override  · magenta (human override active)</pre>

<h2 class="section">Source trace row (★ v0.2)</h2>
<div class="component-stage" style="flex-direction:column;align-items:stretch;gap:0;max-width:720px;">
  <div style="display:grid;grid-template-columns:1.3fr 1fr 0.9fr 0.7fr 0.5fr 0.5fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--border-soft);font-family:'Chakra Petch',sans-serif;font-size:0.7rem;letter-spacing:0.10em;text-transform:uppercase;color:var(--fg-muted);">
    <div>Source</div><div>Object</div><div>Last sync</div><div>Owner</div><div style="text-align:right;">Conf</div><div style="text-align:right;">Drill</div>
  </div>
  <div style="display:grid;grid-template-columns:1.3fr 1fr 0.9fr 0.7fr 0.5fr 0.5fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--border-soft);font-family:'JetBrains Mono',monospace;font-size:0.8125rem;align-items:center;">
    <div style="color:var(--cyan);">QuickBooks</div>
    <div style="color:var(--fg-muted);">invoices</div>
    <div style="color:var(--fg-muted);">12s ago</div>
    <div style="font-family:'Inter',sans-serif;">eric</div>
    <div style="text-align:right;color:var(--gain);">99%</div>
    <div style="text-align:right;color:var(--cyan);">↗</div>
  </div>
  <div style="display:grid;grid-template-columns:1.3fr 1fr 0.9fr 0.7fr 0.5fr 0.5fr;gap:12px;padding:8px 0;border-bottom:1px solid var(--border-soft);font-family:'JetBrains Mono',monospace;font-size:0.8125rem;align-items:center;">
    <div style="color:var(--cyan);">HubSpot</div>
    <div style="color:var(--fg-muted);">deals</div>
    <div style="color:var(--amber);">4h ago</div>
    <div style="font-family:'Inter',sans-serif;">jay</div>
    <div style="text-align:right;color:var(--amber);">82%</div>
    <div style="text-align:right;color:var(--cyan);">↗</div>
  </div>
  <div style="display:grid;grid-template-columns:1.3fr 1fr 0.9fr 0.7fr 0.5fr 0.5fr;gap:12px;padding:8px 0;font-family:'JetBrains Mono',monospace;font-size:0.8125rem;align-items:center;">
    <div style="color:var(--cyan);">AWS · Cost Explorer</div>
    <div style="color:var(--fg-muted);">monthly_spend</div>
    <div style="color:var(--red);">failed</div>
    <div style="font-family:'Inter',sans-serif;">eric</div>
    <div style="text-align:right;color:var(--red);">—</div>
    <div style="text-align:right;color:var(--cyan);">↗</div>
  </div>
</div>
<pre class="spec-pre">columns: source_system (cyan mono) · object (mono dim) · last_sync (timestamp · freshness-colored)
         · owner (Inter) · confidence (delta · gain/loss/amber) · drill_through (cyan arrow)
border:  1px solid neutral.800 between rows</pre>

<h2 class="section">Variance row — embedded in finance_panel above</h2>
<p style="color:var(--fg-muted);font-size:0.9rem;margin-bottom:var(--gap-md);">See the Finance panel demo above — each row is a <code>variance_row</code> component instance. Columns: label · actual · budget · forecast · variance$ · variance% · materiality · agent_recommendation. All numerics use JetBrains Mono + <code>font-feature-settings: "tnum"</code>.</p>

<h2 class="section">Approval card (★ v0.2)</h2>
<div class="component-stage">
  <div class="approval-card">
    <div class="ac-header">Approval required · agent proposal</div>
    <h4>Update revenue forecast model</h4>
    <p style="color:var(--fg-muted);font-size:0.85rem;margin:0 0 12px 0;">Agent has detected a structural shift in close rates and proposes updating the FY26 forecast multiplier from 0.84 → 0.91.</p>
    <div class="ac-evidence">
      → 8 weeks of close-rate data (HubSpot)<br>
      → χ² = 17.4, p &lt; 0.001<br>
      → confidence: 94%
    </div>
    <div class="ac-impact">
      Impact on Q3 ARR forecast: <span class="gain">+$1.2M (+8.4%)</span><br>
      Impact on runway: <span class="gain">+2.1 months</span>
    </div>
    <div class="ac-actions">
      <button class="approve">Approve</button>
      <button class="reject">Reject</button>
      <button class="inspect">Inspect</button>
    </div>
  </div>
</div>
<pre class="spec-pre">background:  neutral.850
border:      1px DASHED amber  /* dashed signals "pending decision" */
header:      amber Chakra Petch 600 uppercase
evidence:    terminal-block-inset (black + cyan border + JetBrains Mono)
impact:      mono + tnum · gain/loss colors
actions:     approve (magenta) · reject (red ghost) · inspect (cyan ghost)</pre>

<h2 class="section">Agent log (★ v0.2)</h2>
<div class="component-stage">
  <div class="terminal-demo" style="width:100%;max-width:560px;">
    <div><span class="term-meta">[22:35:54.013]</span> <span style="color:var(--cyan);">→ sync</span>: QuickBooks · invoices · <span class="term-prompt">204 records · 142ms</span></div>
    <div><span class="term-meta">[22:35:58.847]</span> <span style="color:var(--magenta);">→ command</span>: run forecast() · revenue · FY26 · Q3</div>
    <div><span class="term-meta">[22:36:01.022]</span> <span style="color:#6B6BC4;">→ tool_use</span>: bash · python compute_forecast.py</div>
    <div><span class="term-meta">[22:36:12.541]</span> <span style="color:var(--amber);">→ approval-required</span>: model update · runway recalc</div>
    <div><span class="term-meta">[22:36:24.890]</span> <span class="term-prompt">→ complete</span>: forecast accepted · runway 15.2mo → 17.3mo</div>
    <div><span class="term-meta">[22:36:47.301]</span> <span style="color:var(--red);">→ error</span>: AWS Cost Explorer sync failed (HTTP 503)</div>
  </div>
</div>
<pre class="spec-pre">inherits:        terminal_block (pure black + cyan border + JetBrains Mono)
timestamp_color: neutral.500
event_types:
  command:           magenta  /* agentic action */
  sync:              cyan     /* data lineage */
  tool_use:          steel_violet.300
  approval_request:  amber
  approval_granted:  lime
  complete:          lime
  error:             red</pre>

<h2 class="section">Board export preview (★ v0.2)</h2>
<p style="color:var(--fg-muted);font-size:0.9rem;margin-bottom:var(--gap-md);">Same dashboard, reduced neon. Live cockpit on the left; board-safe export on the right. Glow collapses to inset 1px border; animations pause; focus rings stay visible for accessibility. Activated via <code>body.board-safe</code>.</p>
<div class="component-stage" style="align-items:flex-start;">
  <div style="flex:1;min-width:240px;">
    <div style="font-size:0.7rem;color:var(--fg-muted);font-family:'JetBrains Mono',monospace;margin-bottom:8px;">live cockpit</div>
    <div class="kpi-card state-agent">
      <div class="kpi-label" style="color:var(--magenta);"><span class="dot"></span>Agent · recomputing ARR</div>
      <div class="kpi-value">$14.2M</div>
      <div class="kpi-delta gain">+8.2% confidence: 64%</div>
    </div>
  </div>
  <div style="flex:1;min-width:240px;">
    <div style="font-size:0.7rem;color:var(--fg-muted);font-family:'JetBrains Mono',monospace;margin-bottom:8px;">board-safe export</div>
    <div class="kpi-card" style="border:1px solid var(--magenta);box-shadow:none;">
      <div class="kpi-label" style="color:var(--magenta);"><span class="dot"></span>Agent · recomputing ARR</div>
      <div class="kpi-value">$14.2M</div>
      <div class="kpi-delta gain">+8.2% confidence: 64%</div>
    </div>
  </div>
</div>
<pre class="spec-pre">body.board-safe overrides:
  --neon-glow-*    → inset 0 0 0 1px {color}
  --scanline-*     → none
  --animation-*    → none (paused)
  --focus-ring-*   → 0 0 0 2px {color}  /* stays visible — a11y */</pre>
"""


# ─── ★ v0.2 — Cockpit reference page (brand portal only, not cepsra impl) ─

def body_cockpit(m: dict) -> str:
    return """
<p class="page-lead">Sample FinanceOS layout demonstrating the <strong>Dark Ledger / Neon Operator</strong> thesis applied to a finance cockpit. <strong>This is a brand-portal reference page only</strong> — the actual cepsra cockpit implementation lives in a separate thread. Static finance panels are sober; the agentic execution layer (event feed, command bar, agent-active panels) is where neon emits.</p>

<h2 class="section">Thesis applied</h2>
<p style="color:var(--fg-muted);max-width:65ch;margin-bottom:var(--gap-md);">Topbar carries <code>machine-identifier-strip</code> motif (env, model, period, source freshness, agent ID). Left rail names the FinanceOS surfaces. Main column shows a KPI strip + a <code>finance_panel</code> (Operating expense variance, sober) + an active <code>finance_panel</code> (Revenue bridge, with <code>neon-operator-layer</code> glow because agent is actively recomputing). Right column carries <code>agent-event-feed</code>.</p>

<div class="cockpit-frame">
  <!-- Topbar / machine-identifier-strip -->
  <div class="cockpit-topbar">
    <span class="brand">PARSPEC · FINANCEOS</span>
    <span><span style="color:var(--fg-muted);">env:</span> prod</span>
    <span><span style="color:var(--fg-muted);">model:</span> <span style="color:var(--magenta);">claude-opus-4-7</span></span>
    <span><span style="color:var(--fg-muted);">period:</span> FY26·Q2·CLOSED</span>
    <div class="topbar-meta">
      <span><span style="color:var(--fg-muted);">last sync:</span> <span class="live">12s ago</span></span>
      <span><span style="color:var(--fg-muted);">agent:</span> <span style="color:var(--cyan);">エ·0042</span></span>
    </div>
  </div>

  <div class="cockpit-body">
    <!-- Left rail -->
    <nav class="cockpit-rail">
      <div class="rail-item">Runway</div>
      <div class="rail-item">Revenue</div>
      <div class="rail-item active">Opex</div>
      <div class="rail-item">Headcount</div>
      <div class="rail-item">Infra / AI COGS</div>
      <div class="rail-item">Forecast</div>
      <div class="rail-item">Board Pack</div>
      <div class="rail-item">Agent Logs</div>
    </nav>

    <!-- Main column -->
    <main class="cockpit-main">
      <!-- KPI strip -->
      <div class="cockpit-kpi-strip">
        <div class="kpi-card">
          <div class="kpi-label"><span class="dot" style="color:var(--lime);"></span>Cash</div>
          <div class="kpi-value">$12.8M</div>
          <div class="kpi-delta gain">+8.4% MoM</div>
        </div>
        <div class="kpi-card state-watch">
          <div class="kpi-label" style="color:var(--amber);"><span class="dot"></span>Runway</div>
          <div class="kpi-value">15.2mo</div>
          <div class="kpi-delta loss">-1.8mo vs plan</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span class="dot" style="color:var(--loss);"></span>Burn</div>
          <div class="kpi-value">$847K</div>
          <div class="kpi-delta loss">+3.3% MoM</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span class="dot" style="color:var(--lime);"></span>ARR</div>
          <div class="kpi-value">$14.2M</div>
          <div class="kpi-delta gain">+18.4% YoY</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label"><span class="dot" style="color:var(--cyan);"></span>Gross Margin</div>
          <div class="kpi-value">74%</div>
          <div class="kpi-delta gain">+220bps</div>
        </div>
      </div>

      <!-- Sober finance panel (no glow — Dark Ledger thesis) -->
      <div class="finance-panel">
        <div class="fp-header">
          <div class="fp-title">Operating expense · FY26 Q2</div>
          <div class="fp-meta">
            <span class="data-badge synced"><span class="dot"></span>synced 12s ago</span>
            <span class="trace-link">drill →</span>
          </div>
        </div>
        <div class="variance-row header">
          <div>Line</div><div class="num">Actual</div><div class="num">Budget</div><div class="num">Forecast</div><div class="num">Var $</div><div class="num">Var %</div>
        </div>
        <div class="variance-row">
          <div class="label">Payroll · Engineering</div>
          <div class="num">847,212</div>
          <div class="num budget">820,000</div>
          <div class="num forecast">840,000</div>
          <div class="num loss">-27,212</div>
          <div class="num loss">-3.3%</div>
        </div>
        <div class="variance-row">
          <div class="label">Payroll · Sales</div>
          <div class="num">412,890</div>
          <div class="num budget">410,000</div>
          <div class="num forecast">408,000</div>
          <div class="num loss">-2,890</div>
          <div class="num loss">-0.7%</div>
        </div>
        <div class="variance-row">
          <div class="label">AWS · compute</div>
          <div class="num">142,847</div>
          <div class="num budget">160,000</div>
          <div class="num forecast">150,000</div>
          <div class="num gain">+17,153</div>
          <div class="num gain">+10.7%</div>
        </div>
        <div class="variance-row">
          <div class="label">AI · model spend</div>
          <div class="num">28,471</div>
          <div class="num budget">22,000</div>
          <div class="num forecast">26,000</div>
          <div class="num loss">-6,471</div>
          <div class="num loss">-29.4%</div>
        </div>
      </div>

      <!-- Agent-active finance panel (neon-operator-layer glow) -->
      <div class="finance-panel active" style="margin-top:16px;">
        <div class="fp-header">
          <div class="fp-title" style="color:var(--magenta);">Revenue bridge · agent recomputing</div>
          <div class="fp-meta">
            <span class="data-badge manual"><span class="dot"></span>agent · acting</span>
          </div>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;color:var(--fg-muted);font-size:0.78rem;line-height:1.7;">
          <div>→ claude-opus-4-7 · forecast() · 4.2k tokens · 1.8s elapsed</div>
          <div>→ trace: HubSpot · deals · close_rate · 8w window</div>
          <div>→ proposing model update · confidence 94%</div>
          <div>→ <span style="color:var(--amber);">approval required</span></div>
        </div>
      </div>

      <!-- Approval card -->
      <div style="margin-top:16px;">
        <div class="approval-card">
          <div class="ac-header">Approval required · agent proposal</div>
          <h4>Update revenue forecast multiplier 0.84 → 0.91</h4>
          <div class="ac-evidence">
            → 8 weeks of close-rate data (HubSpot)<br>
            → χ² = 17.4, p &lt; 0.001 · confidence 94%
          </div>
          <div class="ac-impact">
            Q3 ARR forecast: <span class="gain">+$1.2M (+8.4%)</span> · Runway: <span class="gain">+2.1 months</span>
          </div>
          <div class="ac-actions">
            <button class="approve">Approve</button>
            <button class="reject">Reject</button>
            <button class="inspect">Inspect</button>
          </div>
        </div>
      </div>
    </main>

    <!-- Right column — agent event feed -->
    <aside class="cockpit-feed">
      <div class="feed-title">Agent · event feed</div>
      <div class="feed-event sync"><span class="ts">[22:35:54]</span> → sync: QuickBooks · invoices · 204 records · 142ms</div>
      <div class="feed-event command"><span class="ts">[22:35:58]</span> → command: run forecast() · revenue · FY26 Q3</div>
      <div class="feed-event"><span class="ts">[22:36:01]</span> → tool_use: bash · python compute_forecast.py</div>
      <div class="feed-event approval"><span class="ts">[22:36:12]</span> → approval-required: model update · runway recalc</div>
      <div class="feed-event complete"><span class="ts">[22:36:24]</span> → complete: forecast accepted · runway 15.2mo → 17.3mo</div>
      <div class="feed-event error"><span class="ts">[22:36:47]</span> → error: AWS Cost Explorer sync failed (HTTP 503)</div>
      <div class="feed-event sync"><span class="ts">[22:37:02]</span> → sync: HubSpot · deals · 47 records · 218ms</div>
      <div class="feed-event"><span class="ts">[22:37:18]</span> → tool_use: web_search · "covenant threshold reporting"</div>
      <div class="feed-event command"><span class="ts">[22:37:31]</span> → command: generate board memo · Q2 close</div>
      <div class="feed-event complete"><span class="ts">[22:37:54]</span> → complete: board memo drafted · 3.2k words</div>
    </aside>
  </div>
</div>

<h2 class="section">What this demonstrates</h2>
<ul style="font-family:'Inter',sans-serif;line-height:1.7;color:var(--fg-muted);">
  <li><strong style="color:var(--fg);">Dark sober finance truth:</strong> the Opex variance panel has no glow. Numerics are mono with tabular numerals. Gain/loss columns use finance directionality colors (not status colors).</li>
  <li><strong style="color:var(--fg);">Luminous agent layer:</strong> the Revenue bridge panel and the agent_command_active state on the KPI strip carry the neon-operator-layer glow because an agent is actually acting on them.</li>
  <li><strong style="color:var(--fg);">Cyan = trace:</strong> source freshness, drill-through links, source_trace_row source names — all cyan. The operator's "where did this come from?" signal.</li>
  <li><strong style="color:var(--fg);">Amber = attention:</strong> Runway is amber-bordered (watch state). Approval-required event is amber. Stale data badge is amber.</li>
  <li><strong style="color:var(--fg);">Red = real risk:</strong> covenant breach KPI border. Failed AWS sync. Material loss values. Operator scans red and knows to look.</li>
  <li><strong style="color:var(--fg);">Magenta = command:</strong> CTAs (Approve, Run, Investigate). Active agent indicators. Command bar primary. Manual override badges. Never decorative.</li>
  <li><strong style="color:var(--fg);">Mono everywhere identifiers live:</strong> topbar metadata, KPI values, table numerics, deltas, timestamps, agent IDs, model names — all JetBrains Mono.</li>
</ul>

<h2 class="section">Not for cepsra implementation reference</h2>
<p style="color:var(--fg-muted);max-width:65ch;">This page is a <em>brand portal artifact</em> — a reference showing the thesis applied. The actual cepsra cockpit (component composition, routing, data plumbing) lives in a separate workstream. When implementing, consume the same <code>design-model.yaml</code> tokens via <code>ek-web</code> and pair them with cepsra's own component architecture.</p>
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
        ("cockpit.html", "Cockpit", body_cockpit(model)),
    ]

    for filename, title, body in pages:
        html = page_chrome(model, title, body, filename)
        (OUT_DIR / filename).write_text(html, encoding="utf-8")
        print(f"  wrote {filename} ({len(html):,} bytes)")

    print(f"\nGenerated {len(pages)} pages → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
