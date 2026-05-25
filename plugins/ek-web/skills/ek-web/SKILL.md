---
name: ek-web
description: "ek-web token exporter. Use when the user wants to export ek-design brand tokens (from design-model.yaml) into consumable web-codebase formats — Tailwind config, shadcn theme CSS variables, or flat CSS variables. Triggers include 'export ek tokens', 'regen tailwind config for cepsra', 'update shadcn theme from ek-design', 'ek-web export tailwind', 'ek-web export shadcn', 'ek-web export css-vars', 'ek-web export all', '/ek-web'. The skill reads ../../ek-design/skills/ek-design/design-model.yaml and writes to dist/."
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# ek-web

Token exporter. Reads `design-model.yaml` from the sibling `ek-design` plugin and emits three consumable artifacts for any web codebase that imports them. Brand evolution becomes: edit yaml → run exporter → downstream apps update.

## Outputs

| Output | Path | What consumes it |
|---|---|---|
| Tailwind config | `dist/tailwind-tokens.ts` | Tailwind v4 — `theme.extend` for `colors`, `fontFamily`, `spacing`, `borderRadius`, `boxShadow` |
| shadcn theme | `dist/shadcn-theme.css` | shadcn/ui — `:root` block with the standard `--background`, `--foreground`, `--primary`, etc. |
| Flat CSS vars | `dist/ek-tokens.css` | Plain CSS / marketing pages / embedded widgets — `:root { --ek-magenta-500, ... }` |

All three regenerate from one source. The yaml stays the SSoT; the exporters are deterministic.

## Operations

### Export one format

```bash
python3 scripts/export-tailwind.py     # → dist/tailwind-tokens.ts
python3 scripts/export-shadcn.py        # → dist/shadcn-theme.css
python3 scripts/export-css-vars.py      # → dist/ek-tokens.css
```

### Export all

```bash
python3 scripts/export-all.py
```

### Skill triggers

When user says:

| Phrase | Run |
|---|---|
| "ek-web export tailwind" / "regen tailwind config" | `export-tailwind.py` |
| "ek-web export shadcn" / "regen shadcn theme" | `export-shadcn.py` |
| "ek-web export css-vars" / "regen css vars" | `export-css-vars.py` |
| "ek-web export all" / "export ek tokens" | `export-all.py` |

After running, summarize what changed: which output files, how many tokens emitted, which yaml `meta.version` they're tagged with.

## How a consumer wires this in

### Tailwind (Next.js + Tailwind v4)

`tailwind.config.ts`:

```ts
import { ekTokens } from "../path/to/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-tokens"

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: ekTokens },
}
```

Then in any `.tsx`:

```tsx
<button className="bg-magenta-500 text-white font-display rounded-control">
  Run agent
</button>
```

### shadcn/ui

In your `app/globals.css` (or wherever shadcn theme lives), replace the default `:root` block with the content of `dist/shadcn-theme.css`. shadcn components automatically pick up the new tokens.

### Plain CSS

Import `dist/ek-tokens.css` once in your global stylesheet, then use:

```css
.hero {
  background: var(--ek-bg);
  color: var(--ek-white);
}
.cta {
  background: var(--ek-magenta-500);
  box-shadow: var(--ek-effect-neon-glow-magenta);
}
```

## Brand evolution workflow (consumer's perspective)

1. ek-design owner edits `design-model.yaml`, bumps `meta.version`, commits, tags
2. ek-web exporter re-runs (manual or via CI hook later)
3. Downstream apps (cepsra, etc.) pick up the regenerated `dist/*` files
4. If consumed via git submodule or pnpm-link, the update is instant; if hand-imported, the consumer copies the new file

## What this skill does NOT do

- Define brand tokens — that's `ek-design` (the SSoT)
- Lint consumer code — that's `ek-craft` (backlog v0.3)
- Visual review — that's `ek-review` (backlog v0.4)
- Mutate `design-model.yaml` — read-only consumer of it
