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
| **Tailwind v4 (CSS-first)** | `dist/tailwind-v4.css` | **Default for Tailwind v4 apps** — `@theme inline` block. cepsra uses this. |
| Tailwind v3 (JS config) | `dist/tailwind-tokens.ts` | Legacy Tailwind v3 — `theme.extend` JS object. Storybook, non-Next.js consumers. |
| shadcn theme | `dist/shadcn-theme.css` | shadcn/ui — `:root` block with standard `--background`, `--primary`, etc. + ek extensions |
| Flat CSS vars | `dist/ek-tokens.css` | Plain CSS / marketing pages / embedded widgets — `:root { --ek-magenta-500, ... }` |

All four regenerate from one source. The yaml stays the SSoT; the exporters are deterministic.

## Operations

### Export one format

```bash
python3 scripts/export-tailwind-v4.py   # → dist/tailwind-v4.css      (default for Tailwind v4)
python3 scripts/export-tailwind.py      # → dist/tailwind-tokens.ts   (legacy v3 JS config)
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

### Tailwind v4 (Next.js / CSS-first config) ★ default

In `app/globals.css`:

```css
@import "tailwindcss";

/* paste the contents of dist/tailwind-v4.css here, OR @import it */
@theme inline {
  --color-background: #0A0A14;
  --color-magenta-500: #FF2A6D;
  /* ... full set from dist/tailwind-v4.css ... */
}
```

Then in any `.tsx`:

```tsx
<button className="bg-magenta-500 text-foreground font-display rounded-control shadow-neon-glow-magenta">
  Run agent
</button>
```

cepsra uses the inline-paste approach because the ek-design repo is gitignored
from the cepsra repo; pasting at brand-evolution time is the manual-but-mechanical
flow. When ek-design ships as a published npm package, switch to `@import`.

### Tailwind v3 (legacy / Storybook)

`tailwind.config.ts`:

```ts
import { ekTokens } from "<path>/dist/tailwind-tokens"
export default { content: [...], theme: { extend: ekTokens } }
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
