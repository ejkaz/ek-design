#!/usr/bin/env python3
"""
export-shadcn.py

Reads design-model.yaml and writes dist/shadcn-theme.css — a `:root` block
in shadcn/ui's standard CSS-variable naming convention so any shadcn
component (Button, Card, Input, Dialog, ...) is themed ek-design out of
the box.

Wire into your app's globals.css:
  @import "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/shadcn-theme.css";
"""

from __future__ import annotations

import sys
from _lib import banner, load_model, resolve, resolve_deep, write_output


def render(model: dict) -> str:
    prims = model["primitives"]["colors"]
    roles = model["roles"]
    effects = model["tokens"]["effects"]
    fams = model["tokens"]["typography"]["families"]

    # Resolve helper bound to these primitives
    def R(v):
        return resolve(v, prims) if isinstance(v, str) and v.startswith("{") else v

    # ─── shadcn standard variables ──────────────────────────────────────
    shadcn = {
        "background":             R(roles["surface_app"]),
        "foreground":             R(roles["text_dark_primary"]),
        "card":                   R(roles["surface_panel"]),
        "card-foreground":        R(roles["text_dark_primary"]),
        "popover":                R(roles["surface_panel"]),
        "popover-foreground":     R(roles["text_dark_primary"]),
        "primary":                R(roles["cta"]),
        "primary-foreground":     R(roles["cta_text"]),
        "secondary":              R(roles["secondary_action"]),
        "secondary-foreground":   R(roles["surface_app"]),
        "muted":                  R(roles["surface_panel"]),
        "muted-foreground":       R(roles["text_dark_secondary"]),
        "accent":                 R(roles["status_success_on_dark"]),
        "accent-foreground":      R(roles["surface_app"]),
        "destructive":            R(roles["destructive_action"]),
        "destructive-foreground": R(roles["text_dark_primary"]),
        "border":                 R(roles["border_dark"]),
        "input":                  R(roles["surface_panel"]),
        "ring":                   R(roles["cta"]),
    }
    shadcn_lines = "\n".join(f"  --{k}: {v};" for k, v in shadcn.items())

    # ─── ek-design extensions (non-shadcn) ──────────────────────────────
    # Status semantics + agent state — make consumers reach for these
    # instead of hard-coding hexes when they need richer semantics than
    # shadcn's three (primary/secondary/destructive) provides.
    status_lines = "\n".join([
        f"  --status-success: {R(roles['status_success_on_dark'])};",
        f"  --status-warn: {R(roles['status_warn_on_dark'])};",
        f"  --status-error: {R(roles['status_error_on_dark'])};",
        f"  --status-info: {R(roles['info_on_dark'])};",
    ])
    # v0.2: role names tightened — agent_complete replaces agent_status_complete
    agent_lines = "\n".join([
        f"  --agent-active: {R(roles['agent_status_active'])};",
        f"  --agent-thinking: {R(roles['agent_thinking'])};",
        f"  --agent-tool-use: {R(roles['agent_tool_use'])};",
        f"  --agent-complete: {R(roles.get('agent_complete', roles.get('agent_status_complete', '#A6FF00')))};",
        f"  --agent-blocked: {R(roles['agent_blocked'])};",
        f"  --agent-error: {R(roles['agent_error'])};",
        f"  --agent-idle: {R(roles.get('agent_status_idle', '#5C5C70'))};",
        # v0.2 additions
        f"  --agent-command: {R(roles.get('agent_command', '#FF2A6D'))};",
        f"  --agent-trace: {R(roles.get('agent_trace', '#00D1FF'))};",
        f"  --agent-attention: {R(roles.get('agent_attention', '#FFB800'))};",
        f"  --agent-risk: {R(roles.get('agent_risk', '#FF003C'))};",
    ])

    # ─── ek-primitive aliases (so consumers can reach beyond shadcn's set) ─
    prim_lines = []
    for family, ramp in prims.items():
        for stop, hex_v in ramp.items():
            prim_lines.append(f"  --ek-{family.replace('_','-')}-{stop}: {hex_v};")
    prim_block = "\n".join(prim_lines)

    # ─── Effects ────────────────────────────────────────────────────────
    eff_lines = []
    for key, val in effects.items():
        if isinstance(val, str):
            resolved = resolve_deep(val, prims)
            eff_lines.append(f"  --ek-{key.replace('_','-')}: {resolved};")
    eff_block = "\n".join(eff_lines)

    # ─── Typography ─────────────────────────────────────────────────────
    type_lines = "\n".join([
        f'  --font-display: "{fams["display"]}", sans-serif;',
        f'  --font-sans: "{fams["body"]}", system-ui, sans-serif;',
        f'  --font-mono: "{fams["mono"]}", ui-monospace, "SF Mono", "Menlo", monospace;',
    ])

    head = banner(
        model,
        regen_cmd="python3 plugins/ek-web/skills/ek-web/scripts/export-shadcn.py",
    )

    return f"""{head}

/* ek-design shadcn/ui theme — drop into your app's globals.css.
   Use shadcn components directly; they reference --background, --foreground,
   --primary, --secondary, --accent, --destructive, --border, --ring, --radius.
   ek-design extensions are below the shadcn block (status, agent state,
   primitive aliases, effects, fonts). */

:root {{
  /* ─── shadcn standard ──────────────────────────────────────────── */
{shadcn_lines}

  --radius: 6px;

  /* ─── status semantics (locked) ────────────────────────────────── */
{status_lines}

  /* ─── agent state ──────────────────────────────────────────────── */
{agent_lines}

  /* ─── typography ───────────────────────────────────────────────── */
{type_lines}

  /* ─── ek-primitive aliases (for cases shadcn's set doesn't cover) ─ */
{prim_block}

  /* ─── effects ──────────────────────────────────────────────────── */
{eff_block}
}}
"""


def main() -> int:
    model = load_model()
    write_output("shadcn-theme.css", render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
