# @ekdesign/web

ek-design tokens for web consumers. Generated from [`design-model.yaml`](https://github.com/ejkaz/ek-design/blob/main/plugins/ek-design/skills/ek-design/design-model.yaml) via the [`ek-web`](https://github.com/ejkaz/ek-design/tree/main/plugins/ek-web) exporter.

**Brand thesis**: Dark Ledger / Neon Operator.
**Principle**: *Purple is the world. Magenta is the command. Cyan is the proof.*

Built for agentic finance cockpit surfaces (cepsra / KazOS FinanceOS + AgentOS). See the [live brand portal](https://ek-design.vercel.app) for the full taxonomy, motifs, components, and a sample cockpit layout.

## Install

```bash
pnpm add @ekdesign/web
# or: bun add @ekdesign/web · npm install @ekdesign/web
```

## Usage

### Tailwind v4 (CSS-first config) · default

In your `app/globals.css`:

```css
@import "tailwindcss";
@import "@ekdesign/web/tailwind-v4.css";
```

You immediately get utility classes:

```tsx
<button className="bg-cta text-foreground font-display rounded-control shadow-operator-layer-glow">
  Run forecast
</button>
```

Available tokens (selection):

| Tailwind class | Token |
|---|---|
| `bg-bg` | `#070711` background (deep violet-black) |
| `bg-panel` | `#171727` finance panel surface |
| `bg-magenta-500` / `bg-cta` | `#FF2A6D` command monopoly |
| `text-cyan-500` / `text-link` | `#00D1FF` proof / trace / link |
| `text-success` / `text-lime-500` | `#A6FF00` health / completion |
| `text-warn` / `text-amber-500` | `#FFB800` CFO attention / watch |
| `text-error` / `text-red-500` | `#FF003C` true risk / destructive |
| `text-finance-gain` / `text-finance-loss` | `#4ADE80` / `#F87171` variance directionality |
| `font-display` | Chakra Petch (headers, eyebrows, chrome) |
| `font-sans` | Inter (body, prose) |
| `font-mono` | JetBrains Mono (identifiers, finance numerics — required) |
| `rounded-control` / `rounded-component` | 4px / 6px |
| `shadow-neon-glow-magenta` | Stateful agent-active glow |
| `shadow-operator-layer-glow` | Reduced cockpit glow (v0.2.1) |
| `ease-ek` / `duration-fast` | Motion |

### Tailwind v3 (legacy JS config)

```ts
// tailwind.config.ts
import { ekTokens } from "@ekdesign/web/tailwind-tokens"

export default {
  content: ["./app/**/*.{ts,tsx}"],
  theme: { extend: ekTokens },
}
```

### shadcn/ui

```css
/* app/globals.css */
@import "@ekdesign/web/shadcn-theme.css";
```

Drops in the standard shadcn variables (`--background`, `--primary`, `--destructive`, `--radius`, etc.) plus ek extensions (`--status-*`, `--agent-*`, `--ek-magenta-500`, etc.).

### Plain CSS / non-Tailwind

```css
@import "@ekdesign/web/ek-tokens.css";

.hero { background: var(--ek-bg); color: var(--ek-white); }
.cta { background: var(--ek-cta); box-shadow: var(--ek-neon-glow-magenta); }
```

## Brand evolution

When ek-design ships a new brand version, this package re-publishes with the new tokens. Consumers run:

```bash
pnpm update @ekdesign/web
```

The new brand_version is in the published `package.json` and in the generator banner at the top of every dist file.

## Versioning

Package version === yaml `meta.version` (e.g. `0.2.1`). Brand evolution semantics:

| yaml change | Bump |
|---|---|
| Typo / comment / non-token edit | patch (0.2.1 → 0.2.2) |
| Add a tint, adjust a token, add a primitive ramp | minor (0.2.1 → 0.3.0) |
| Replace hue family anchor, change typography, alter primary axis | major (0.2.1 → 1.0.0) |

## Locked invariants

Reading any file from `@ekdesign/web` implicitly commits to the brand invariants. The most important:

- **magenta_cta_monopoly** · only magenta = primary action
- **cyan_for_trace_only** · cyan = proof / lineage / inspectability
- **lime_alive_and_success_only** · lime = health / completion (not brand pillar)
- **purple_is_environment_not_action** · purple = world / substrate, never CTA
- **steel_violet_is_architecture** · inactive machine structure only
- **glow_is_stateful** · neon only for active state, never decoration
- **mono_for_identifiers** · JetBrains Mono for IDs / paths / timestamps / model names
- **tabular_numerals_for_finance** · finance numerics use `font-feature-settings: "tnum"`
- **no_consumer_indigo_purple** · Tailwind indigo / violet / purple forbidden

Lint enforcement via [`@ekdesign/craft`](../ek-craft) (Python CLI; not yet on npm).

## License

MIT — see [LICENSE](LICENSE).
