#!/usr/bin/env python3
"""
export-css-vars.py

Reads design-model.yaml and writes dist/ek-tokens.css — flat CSS variables
in the `--ek-*` namespace for plain CSS contexts (marketing pages, embedded
widgets, any surface that's not Tailwind- or shadcn-themed).

Wire into your stylesheet:
  @import "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/ek-tokens.css";

Then:
  .hero { background: var(--ek-bg); color: var(--ek-white); }
  .cta  { background: var(--ek-cta); box-shadow: var(--ek-neon-glow-magenta); }
"""

from __future__ import annotations

import sys
from _lib import banner, load_model, resolve, resolve_deep, write_output


def render(model: dict) -> str:
    prims = model["primitives"]["colors"]
    axis = model["primary_axis_preserved"]
    roles = model["roles"]
    typ = model["tokens"]["typography"]
    spacing = model["tokens"]["spacing"]
    radii = model["tokens"]["radii"]
    cuts = model["tokens"].get("cuts", {})
    motion = model["tokens"]["motion"]
    effects = model["tokens"]["effects"]

    def R(v):
        return resolve(v, prims) if isinstance(v, str) and v.startswith("{") else v

    sections = []

    # ─── Surfaces (named conveniences) ──────────────────────────────────
    sections.append("  /* ─── Surfaces ───────────────────────────────────────────── */")
    sections.append(f'  --ek-bg: {axis["background"]};')
    sections.append(f'  --ek-panel: {axis["panel"]};')
    sections.append(f'  --ek-off-white: {axis["off_white"]};')
    sections.append(f'  --ek-white: {axis["white"]};')
    sections.append(f'  --ek-terminal-bg: {prims["neutral"][1000]};')

    # ─── Primitive ramps ────────────────────────────────────────────────
    for family, ramp in prims.items():
        sections.append("")
        sections.append(f"  /* ─── Primitives — {family.replace('_', ' ')} ─── */")
        for stop, hex_v in ramp.items():
            sections.append(f"  --ek-{family.replace('_','-')}-{stop}: {hex_v};")

    # ─── Role tokens (alias to primitives via CSS var fallback chains) ──
    sections.append("")
    sections.append("  /* ─── Role tokens (semantic) ─────────────────────────────── */")
    for role_name, role_ref in roles.items():
        resolved = R(role_ref)
        # If the ref looks like {family.stop}, also link to --ek-family-stop var
        # so consumers can swap primitives later via cascade. For pure hexes pass through.
        if isinstance(role_ref, str) and role_ref.startswith("{") and role_ref.endswith("}"):
            inner = role_ref[1:-1]  # e.g. "magenta.500"
            family, stop = inner.split(".")
            css_ref = f"var(--ek-{family.replace('_','-')}-{stop})"
            sections.append(f"  --ek-{role_name.replace('_','-')}: {css_ref};")
        else:
            sections.append(f"  --ek-{role_name.replace('_','-')}: {resolved};")

    # ─── Typography ─────────────────────────────────────────────────────
    fams = typ["families"]
    sections.append("")
    sections.append("  /* ─── Typography ─────────────────────────────────────────── */")
    sections.append(f'  --ek-font-display: "{fams["display"]}", sans-serif;')
    sections.append(f'  --ek-font-body: "{fams["body"]}", system-ui, sans-serif;')
    sections.append(f'  --ek-font-mono: "{fams["mono"]}", ui-monospace, "SF Mono", "Menlo", monospace;')

    # Type scale (size_clamp values only — the most consumed)
    for scale_key in ["display", "h1", "h2", "h3", "body_lg", "body", "small", "eyebrow", "mono", "mono_sm", "code"]:
        s = typ.get(scale_key)
        if not s:
            continue
        if "size_clamp" in s:
            sections.append(f"  --ek-text-{scale_key.replace('_','-')}: {s['size_clamp']};")

    # ─── Spacing ────────────────────────────────────────────────────────
    sections.append("")
    sections.append("  /* ─── Spacing ────────────────────────────────────────────── */")
    for key, val in spacing.items():
        sections.append(f'  --ek-space-{key}: {val}px;')

    # ─── Radii + cuts ───────────────────────────────────────────────────
    sections.append("")
    sections.append("  /* ─── Radii / cuts ───────────────────────────────────────── */")
    for key, val in radii.items():
        if key == "pill":
            sections.append(f'  --ek-radius-{key}: 9999px;')
        else:
            sections.append(f'  --ek-radius-{key}: {val}px;')
    for key, val in cuts.items():
        sections.append(f'  --ek-cut-{key}: {val}px;')

    # ─── Motion ─────────────────────────────────────────────────────────
    sections.append("")
    sections.append("  /* ─── Motion ─────────────────────────────────────────────── */")
    sections.append(f'  --ek-easing: {motion["easing"]};')
    sections.append(f'  --ek-duration-fast: {motion["duration_fast"]};')
    sections.append(f'  --ek-duration-normal: {motion["duration_normal"]};')
    sections.append(f'  --ek-duration-slow: {motion["duration_slow"]};')

    # ─── Effects ────────────────────────────────────────────────────────
    sections.append("")
    sections.append("  /* ─── Effects ────────────────────────────────────────────── */")
    for key, val in effects.items():
        if isinstance(val, str):
            resolved = resolve_deep(val, prims)
            sections.append(f'  --ek-{key.replace("_","-")}: {resolved};')

    body = "\n".join(sections)

    head = banner(
        model,
        regen_cmd="python3 plugins/ek-web/skills/ek-web/scripts/export-css-vars.py",
    )

    return f"""{head}

/* ek-design flat CSS variables — for plain CSS contexts.

   Role tokens (--ek-cta, --ek-link-on-dark, etc.) reference primitive
   tokens via var() so a downstream consumer can swap the primitive value
   at any cascade level (e.g. an embedded white-label widget overriding
   --ek-magenta-500 to red would cascade through to --ek-cta automatically).

   For Tailwind v4 use tailwind-tokens.ts instead.
   For shadcn/ui use shadcn-theme.css instead. */

:root {{
{body}
}}

@media (prefers-reduced-motion: reduce) {{
  :root {{
    --ek-duration-fast: 80ms;
    --ek-duration-normal: 80ms;
    --ek-duration-slow: 80ms;
  }}
}}
"""


def main() -> int:
    model = load_model()
    write_output("ek-tokens.css", render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
