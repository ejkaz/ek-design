#!/usr/bin/env python3
"""
export-tailwind.py

Reads design-model.yaml from the sibling ek-design plugin and writes
dist/tailwind-tokens.ts — a Tailwind v4 `theme.extend` block.

Consumed by:
  // tailwind.config.ts
  import { ekTokens } from "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-tokens"
  export default { theme: { extend: ekTokens } }
"""

from __future__ import annotations

import sys
from _lib import banner_line, load_model, resolve_deep, write_output


def _color_ramp(family_name: str, ramp: dict) -> str:
    """Render a single ramp as a JSON-ish object literal."""
    lines = []
    for stop, hex_v in ramp.items():
        # Tailwind keys are strings; numeric stops fine as-is for JS object literals
        key = f'"{stop}"' if not str(stop).isdigit() else str(stop)
        lines.append(f"    {key}: \"{hex_v}\",")
    return "\n".join(lines)


def render(model: dict) -> str:
    prims = model["primitives"]["colors"]
    typ = model["tokens"]["typography"]
    spacing = model["tokens"]["spacing"]
    radii = model["tokens"]["radii"]
    motion = model["tokens"]["motion"]
    effects = model["tokens"]["effects"]
    axis = model["primary_axis_preserved"]

    # ─── Colors ──────────────────────────────────────────────────────────
    color_lines = []
    # Top-level convenience aliases pulled from primary_axis_preserved
    color_lines.append(f'    bg: "{axis["background"]}",')
    color_lines.append(f'    panel: "{axis["panel"]}",')
    color_lines.append(f'    "off-white": "{axis["off_white"]}",')
    color_lines.append(f'    "terminal-bg": "{prims["neutral"][1000]}",')

    # Primitive ramps
    for family, ramp in prims.items():
        tw_family = family.replace("_", "-")
        color_lines.append(f'    "{tw_family}": {{')
        color_lines.append(_color_ramp(family, ramp))
        color_lines.append("    },")

    colors_block = "\n".join(color_lines)

    # ─── Typography ──────────────────────────────────────────────────────
    fams = typ["families"]
    font_family_block = (
        f'    display: [\'"{fams["display"]}"\', "sans-serif"],\n'
        f'    sans: [\'"{fams["body"]}"\', "system-ui", "sans-serif"],\n'
        f'    mono: [\'"{fams["mono"]}"\', "ui-monospace", "SF Mono", "Menlo", "monospace"],'
    )

    # ─── Spacing ─────────────────────────────────────────────────────────
    spacing_lines = []
    for key, val in spacing.items():
        # numeric → px; string keys with numeric vals → px
        spacing_lines.append(f'    "{key}": "{val}px",')
    spacing_block = "\n".join(spacing_lines)

    # ─── Radii ───────────────────────────────────────────────────────────
    radii_lines = []
    for key, val in radii.items():
        if key == "pill":
            radii_lines.append(f'    "{key}": "9999px",')
        else:
            radii_lines.append(f'    "{key}": "{val}px",')
    radii_block = "\n".join(radii_lines)

    # ─── Box shadows (resolve {token.x} → hex inside the string) ─────────
    shadow_lines = []
    for key, val in effects.items():
        if "glow" in key or "focus_ring" in key or "panel_lift" in key:
            resolved = resolve_deep(val, prims)
            tw_key = key.replace("_", "-")
            shadow_lines.append(f'    "{tw_key}": "{resolved}",')
    shadow_block = "\n".join(shadow_lines)

    # ─── Transition timing + duration ───────────────────────────────────
    transition_block = f'''  transitionTimingFunction: {{
    ek: "{motion['easing']}",
  }},
  transitionDuration: {{
    fast: "{motion['duration_fast']}",
    normal: "{motion['duration_normal']}",
    slow: "{motion['duration_slow']}",
  }},'''

    head = banner_line(
        model,
        regen_cmd="python3 plugins/ek-web/skills/ek-web/scripts/export-tailwind.py",
    )

    return f"""{head}

/**
 * ek-design tokens for Tailwind v4.
 *
 * Wire into tailwind.config.ts:
 *   import {{ ekTokens }} from "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-tokens"
 *   export default {{ content: [...], theme: {{ extend: ekTokens }} }}
 *
 * After import you get utility classes:
 *   bg-magenta-500   text-cyan-500   font-display   font-mono   rounded-control
 *   shadow-neon-glow-magenta   transition-duration-fast   ease-ek   p-md
 */
export const ekTokens = {{
  colors: {{
{colors_block}
  }},
  fontFamily: {{
{font_family_block}
  }},
  spacing: {{
{spacing_block}
  }},
  borderRadius: {{
{radii_block}
  }},
  boxShadow: {{
{shadow_block}
  }},
{transition_block}
}} as const

export type EkTokens = typeof ekTokens
"""


def main() -> int:
    model = load_model()
    write_output("tailwind-tokens.ts", render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
