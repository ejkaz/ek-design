# Anti-AI-Slop Rules — ek-design Edition

Universal rules that distinguish "designed by an ek-aware human" from "default LLM output." These apply regardless of which brand version is active. Palette-specific forbidden colors / fonts live in `design-model.yaml` `avoid:` — those are read at runtime.

> Adapted from parspec-craft's anti-ai-slop, retargeted from industrial-distributor decks to cyberpunk web UI.

## Cardinal sins (severity: error)

These are the patterns ek-craft blocks at P0 (must-fix):

1. **Tailwind Indigo / consumer purple as accent** — `#6366F1`, `#4F46E5`, `#4338CA`, `#3730A3`, `#8B5CF6`, `#7C3AED`, `#A855F7`, and the entire Tailwind-indigo / Linear / Notion register. The single biggest "AI starter template" tell of 2024-2026. ek's primary action color is **Magenta `#FF2A6D`** (`bg-magenta-500` / `bg-cta` / `bg-primary`). Atmospheric purple is **steel-violet `#3B3B92`** (`bg-steel-violet-500`), distinct from indigo by hue and value.

2. **Trust gradient** — purple→pink, blue→cyan, indigo→pink, mesh-gradient hero backgrounds. ek hero atmosphere = flat near-black + neon edge accents + optional scanline overlay. A flat surface plus intentional type beats a gradient mesh every time.

3. **Emoji as feature icon** — `✨`, `🚀`, `🎯`, `⚡`, `🔥`, `💡`, etc. inside `<h*>`, `<button>`, `<li>`, or `className*="icon"`. Use Lucide SVG with `currentColor` instead. Cyberpunk register is precise machine glyphs, not playful emoji.

4. **Costume cyberpunk fonts** — `Orbitron`, `Press Start 2P`, `VT323`, `Audiowide`, `Bungee`. These read as Tron-cosplay / 8-bit-game / brand-mascot, not production agentic UI. ek display is **Chakra Petch** (`font-display`) — cyber-coded angled cuts at production legibility.

5. **Non-locked display font** — `<h*>` or hero copy in `Inter`, `Roboto`, `Arial`, `system-ui`, `Helvetica`, `SF Pro`. Locked display is Chakra Petch. Inter is body only. Generic `font-sans` is fine (it resolves to Inter via the locked `--font-sans` token).

6. **Drop-shadow as elevation** — `box-shadow: 0 4px 12px rgba(0,0,0,0.1)` and similar gray drop shadows. Cyberpunk elevation = neon edge glow (`shadow-neon-glow-magenta` / `shadow-neon-glow-cyan` / `shadow-neon-glow-lime`) bound to focus / hover / agent-active. Gray drop-shadow is a 2018-Material-Design holdover; it flattens the cyberpunk register.

7. **Glassmorphism heavy blur** — `backdrop-filter: blur(24px)` or larger with frosted-glass surfaces. Reads as Apple-2020, not Neo-Tokyo. If you need a frosted surface, use a 4–8px blur max plus subtle border-glow.

8. **Gradient-mesh background** — iridescent / mesh-gradient hero backgrounds. Quintessential AI-template visual. ek-design backgrounds are flat near-black surfaces with optional scanline overlay (`var(--scanline-overlay)`) for hero atmospheric texture.

9. **Magenta-as-type on light surfaces** — `text-magenta-500` on `bg-off-white` / `bg-white` fails WCAG AA (3.21:1). On light surfaces, use `text-magenta-800` (`accent_type_on_light` role, 8.27:1 AAA). Locked invariant: `accent_type_on_light_forbidden`.

10. **Identifier text in non-mono** — model names, agent IDs, file paths, timestamps, hashes, token counts in `font-sans` or `font-display`. Locked invariant `mono_for_identifiers`: always `font-mono` (`var(--font-mono)` → JetBrains Mono). The single biggest UX win in operator interfaces.

## Soft tells (severity: warning)

- **Standard "Hero → Features → Pricing → FAQ → CTA" sequence with no variation** — the AI-template skeleton. ek consumers (especially cepsra and any marketing site) should introduce at least one unconventional move: agent-console preview embedded in hero, terminal-block "live transcript" section, comparison-against-status-quo in pricing.

- **External placeholder image CDNs** (`unsplash.com`, `placehold.co`, `picsum.photos`) — fragile and obviously template. Use SVG line illustrations, terminal-block mockups, or honest `[screenshot pending]` placeholders.

- **More than ~10 raw hex values outside `:root` / CSS variables in a single file** — tokens were not honoured. Move to `var(--color-*)` or `bg-*` Tailwind utility classes that reference the @theme block. Per ek-design `prefer_role_tokens` invariant, prefer role tokens (`bg-cta`, `text-info`) over primitives (`bg-magenta-500`, `text-cyan-700`) when the role is semantically right.

- **`bg-cta` or magenta CTA color used 4+ times in the rendered body** — cap at 1–2 visible primary CTAs per surface so the action signal stays a signal. Secondary actions: `bg-secondary` (cyan) or `border-cyan-500` ghost. Locked invariant `magenta_cta_monopoly` enforces single fill color.

- **Faux-handwritten signatures or "made with ❤️" footer copy** — wrong register. Operator-facing brand. If you need a footer, surface the agentic state: model version, build hash, last-deployed timestamp.

- **AI-hype copy** — "powered by AI", "AI-first", "intelligent", "smart", "delight", "magic", "effortless", "unlock", "empower", "transform", "revolutionize". Locked in `design-model.yaml` `voice.avoid`. Use concrete metrics ("212ms", "4.2k tokens", "47 actions/hr") and direct verbs ("Run", "Send", "Apply", "Cancel").

- **Cyberpunk cosplay vocabulary** — "jacked in", "the matrix", "neural", "synaptic". The brand is visually cyberpunk; the copy stays grounded.

## How to fix

Each finding should suggest a remediation. Examples:

| Finding | Fix |
|---|---|
| `#6366F1` (Tailwind Indigo) | Replace with `bg-magenta-500` (primary action) or `bg-steel-violet-500` (atmospheric) |
| `font-family: "Inter"` on `<h1>` | Swap to `font-display` (Chakra Petch) |
| `box-shadow: 0 4px 12px rgba(0,0,0,0.1)` | Use `shadow-neon-glow-magenta` (action) or `shadow-panel-lift` (passive elevation) |
| `<span>{modelId}</span>` (no mono class) | Wrap as `<code>` or add `font-mono` |
| `text-magenta-500` on `bg-off-white` | Switch to `text-magenta-800` (AA-safe) |
| `bg-gradient-to-r from-purple-500 to-pink-500` | Solid `bg-bg` + accent component(s); save gradients for explicit motif (scanline overlay) |
