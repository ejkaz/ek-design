#!/usr/bin/env python3
"""
export-tailwind-v4.py

Reads design-model.yaml and writes dist/tailwind-v4.css — a Tailwind v4
CSS-first config (@theme inline block) that an app's globals.css imports.

Tailwind v4 changed config from `tailwind.config.ts` JS objects to a
CSS-native @theme block. This is THE format Tailwind v4 actually consumes.
The legacy tailwind-tokens.ts exporter remains for v3-style consumers.

Wire into your app's globals.css:
  @import "tailwindcss";
  @import "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-v4.css";

You then get utility classes:
  bg-bg, text-foreground, font-display, font-mono, text-magenta-500,
  rounded-control, shadow-neon-glow-magenta, p-md, etc.
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
    motion = model["tokens"]["motion"]
    effects = model["tokens"]["effects"]
    fams = typ["families"]

    def R(v):
        return resolve(v, prims) if isinstance(v, str) and v.startswith("{") else v

    sections = []

    # ─── Semantic surface aliases (highest-level convenience) ──────────
    sections.append("  /* ─── Semantic surfaces (bg-*, text-*) ─────────── */")
    sections.append(f"  --color-background: {axis['background']};")
    sections.append(f"  --color-foreground: {axis['white']};")
    sections.append(f"  --color-bg: {axis['background']};")
    sections.append(f"  --color-panel: {axis['panel']};")
    sections.append(f"  --color-off-white: {axis['off_white']};")
    sections.append(f"  --color-terminal-bg: {prims['neutral'][1000]};")

    # ─── Primitive color ramps (bg-magenta-500, text-cyan-700, etc.) ──
    for family, ramp in prims.items():
        sections.append("")
        sections.append(f"  /* {family.replace('_', ' ')} */")
        for stop, hex_v in ramp.items():
            sections.append(f"  --color-{family.replace('_','-')}-{stop}: {hex_v};")

    # ─── Role-token shortcuts (commonly-reached-for) ───────────────────
    sections.append("")
    sections.append("  /* ─── Role tokens — common reach-for shortcuts ─── */")
    role_shortcuts = {
        "cta": "cta",
        "cta-hover": "cta_hover",
        "primary": "cta",
        "secondary": "secondary_action",
        "destructive": "destructive_action",
        "success": "status_success_on_dark",
        "warn": "status_warn_on_dark",
        "error": "status_error_on_dark",
        "info": "info_on_dark",
        "link": "link_on_dark",
        "agent-active": "agent_status_active",
        "agent-thinking": "agent_thinking",
        "agent-blocked": "agent_blocked",
        "agent-error": "agent_error",
        "agent-idle": "agent_status_idle",
        "border": "border_dark",
        "border-focus": "border_focus",
    }
    for shortcut, role_key in role_shortcuts.items():
        if role_key in roles:
            sections.append(f"  --color-{shortcut}: {R(roles[role_key])};")

    # ─── Typography families (font-display, font-sans, font-mono) ──────
    sections.append("")
    sections.append("  /* ─── Typography ───────────────────────────────── */")
    sections.append(f'  --font-display: "{fams["display"]}", sans-serif;')
    sections.append(f'  --font-sans: "{fams["body"]}", system-ui, sans-serif;')
    sections.append(f'  --font-mono: "{fams["mono"]}", ui-monospace, "SF Mono", "Menlo", monospace;')

    # Type scale (size_clamp values)
    sections.append("")
    sections.append("  /* type-scale (text-display, text-h1, text-body, text-mono) */")
    for scale_key in ["display", "h1", "h2", "h3", "body_lg", "body", "small", "eyebrow", "mono", "mono_sm", "code"]:
        s = typ.get(scale_key)
        if not s or "size_clamp" not in s:
            continue
        sections.append(f"  --text-{scale_key.replace('_','-')}: {s['size_clamp']};")

    # ─── Spacing (p-md, gap-lg, etc.) ──────────────────────────────────
    sections.append("")
    sections.append("  /* ─── Spacing (p-xs, gap-md, mt-xl, etc.) ──────── */")
    for key, val in spacing.items():
        sections.append(f'  --spacing-{key}: {val}px;')

    # ─── Radii (rounded-control, rounded-component, etc.) ──────────────
    sections.append("")
    sections.append("  /* ─── Radii ────────────────────────────────────── */")
    for key, val in radii.items():
        if key == "pill":
            sections.append(f'  --radius-{key}: 9999px;')
        else:
            sections.append(f'  --radius-{key}: {val}px;')

    # ─── Box shadows (shadow-neon-glow-magenta, etc.) ──────────────────
    sections.append("")
    sections.append("  /* ─── Shadows / glows ──────────────────────────── */")
    for key, val in effects.items():
        if isinstance(val, str) and (
            "glow" in key or "focus_ring" in key or "panel_lift" in key
        ):
            resolved = resolve_deep(val, prims)
            sections.append(f'  --shadow-{key.replace("_","-")}: {resolved};')

    # ─── Transition timing + duration (ease-ek, duration-fast) ─────────
    sections.append("")
    sections.append("  /* ─── Motion ───────────────────────────────────── */")
    sections.append(f'  --ease-ek: {motion["easing"]};')
    sections.append(f'  --duration-fast: {motion["duration_fast"]};')
    sections.append(f'  --duration-normal: {motion["duration_normal"]};')
    sections.append(f'  --duration-slow: {motion["duration_slow"]};')

    body = "\n".join(sections)

    head = banner(
        model,
        regen_cmd="python3 plugins/ek-web/skills/ek-web/scripts/export-tailwind-v4.py",
    )

    return f"""{head}

/* ek-design tokens for Tailwind v4 (CSS-first config).
   Tailwind v4 deprecated tailwind.config.ts in favor of @theme blocks
   inside CSS. This file IS the config.

   Wire into your app's globals.css:
     @import "tailwindcss";
     @import "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-v4.css";

   Then in any .tsx:
     <button className="bg-magenta-500 font-display text-foreground rounded-control shadow-neon-glow-magenta">
       Run agent
     </button>

   The legacy tailwind-tokens.ts exporter (Tailwind v3 JS-config shape) remains
   for v3 consumers and for Storybook / non-Next consumers that prefer JS objects.
*/

@theme inline {{
{body}
}}
"""


def main() -> int:
    model = load_model()
    write_output("tailwind-v4.css", render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
