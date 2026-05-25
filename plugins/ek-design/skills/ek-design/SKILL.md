---
name: ek-design
description: "ek-design brand SSoT and evolution workflow. Use when the user wants to inspect, update, evolve, or roll back the ek-design Neo-Tokyo cyberpunk brand — colors, typography, motion, voice, or the design-model.yaml itself. Triggers include 'show ek brand', 'show cepsra brand', 'update ek design', 'evolve ek palette', 'ek design model', 'roll back ek brand to <tag>', '/ek-design'. The skill maintains design-model.yaml — the single file every other ek-* skill (ek-web, ek-craft, ek-review) reads."
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, WebFetch]
---

# ek-design

Brand SSoT skill. Owns `design-model.yaml` — the single file that defines Eric Kazmaier's personal cyberpunk brand for agentic UI surfaces. Every other ek-* skill (ek-web, ek-craft, ek-review as they ship) reads this file. Brand changes happen here; downstream skills auto-adapt.

## Identity

ek-design is the personal brand stack for Eric's agentic UI work. First consumer is **cepsra** (cepsr.app) — Eric's internal app for tasks + CEO briefings. Architecturally inherited from `parspec-design` (industrial, B2B Construction Materials Distributors); ek-design is the **cyberpunk** counterpart, tuned for agentic surfaces where the user is the operator and the UI must surface technical state (model, tokens, latency, agent status) plainly.

Register: **Neo-Tokyo neon** — Blade Runner / Ghost in the Shell. Deep blue-black backgrounds, magenta hero, electric cyan secondary, acid lime alive/success. Not synthwave (too nostalgic), not brutalist (too monochrome), not terminal-CRT (too austere for product use).

## Locked primary axis (immovable)

| Token | Value | Role |
|---|---|---|
| `background` | `#0A0A14` | Default app + marketing surface — deep blue-black |
| `panel` | `#15151F` | Layered surface |
| `off_white` | `#F0F0F5` | Inverted (light-mode opt-in) |
| `white` | `#FFFFFF` | Text on dark |
| `magenta_cta` | `#FF2A6D` | Primary CTA monopoly |
| `cyan_secondary` | `#00D1FF` | Secondary action / info / link |
| `lime_alive` | `#A6FF00` | Success + agent active indicator |
| Display | **Chakra Petch** | Headers, eyebrows |
| Body | **Inter** | UI body |
| Mono | **JetBrains Mono** | Code, IDs, timestamps — required for agentic UI |

Signature motifs: neon edge glow (CSS box-shadow), terminal-block insets (mono content on cyan-bordered black), katakana-numeric agent IDs, optional reduced-motion-safe scanline overlay.

## What's in design-model.yaml

| Block | Purpose |
|---|---|
| `meta` | Version frontmatter — `version`, `brand_version`, `source`, `updated_by`, `supersedes`, `notes` |
| `surfaces` | Mode-per-surface bindings (app=dark, marketing=dark, light-mode=opt-in, terminal-inset=cyan-on-black) |
| `primitives` | Raw color ramps (neutral, magenta, cyan, lime, steel-violet, slate, red, amber), spacing, radii, cuts |
| `roles` | Two-tier token model — every role token references exactly one primitive. Compile-time monopoly enforcement. |
| `tokens` | Semantic mappings — light/dark color modes, typography scale, motion, iconography |
| `components` | Spec for buttons, cards, terminal-blocks, agent-status badges, code-blocks |
| `voice` | ek voice — operator-respecting, terminal-native, no AI-hype |
| `avoid` | Forbidden colors / fonts / patterns — read by ek-craft for lint |
| `primary_axis_preserved` | The locked anchors above |
| `invariants` | 7 hard rules (CTA monopoly, semantic-locked statuses, mono-for-identifiers, no consumer-indigo/purple) |

## Operations

### Inspect

When user says "show me the ek brand" or "show cepsra brand" or similar:
1. Read `design-model.yaml`
2. Summarize `meta` (version, brand_version, supersedes, notes), `primary_axis_preserved`, hue families, voice
3. If a brand portal exists at `brand-portal/`, offer to open it

### Evolve

When user says "evolve to <description>" or "lock ek brand v0.2":
1. Read current `design-model.yaml`
2. Confirm changeset with user — which blocks change, which stay locked. NEVER touch `primary_axis_preserved` without explicit override.
3. Bump `meta.version` semantically (0.1.0 → 0.1.1 for tweak, 0.2.0 for additions, 1.0.0 for major)
4. Set `meta.brand_version` (e.g., `ek-2026-Q4-v1`), set `meta.supersedes` to prior brand_version
5. Update `primitives.*`, `roles.*`, `tokens.*`, `avoid:` list to match new direction
6. Update `meta.updated`, `meta.updated_by`, `meta.notes` (one-line rationale)
7. Tell user: "Brand v<N> written. To lock it: `git add` + commit + `git tag brand-ek-<version> -m '<rationale>'`"

### Roll back

When user says "roll back to <tag>":
1. `git tag --list 'brand-ek-*'` — confirm tag exists
2. `git checkout <tag> -- plugins/ek-design/skills/ek-design/design-model.yaml`
3. Read the rolled-back file, summarize what reverted

### Lint / audit

For "is this `.tsx`/`.css` on-brand?" — delegate to **ek-craft** (when shipped). That skill reads `design-model.yaml`'s `avoid` list and `primary_axis_preserved` block and applies them as lint rules.

### Export to Tailwind/shadcn

When user says "export tokens to cepsra" or "regenerate tailwind config" — delegate to **ek-web** (when shipped). Until then, hand-write tokens into the consumer's `tailwind.config.ts`.

## Versioning convention

| `meta.version` change | When |
|---|---|
| Patch (0.1.0 → 0.1.1) | Typo, comment, or non-token edit |
| Minor (0.1.0 → 0.2.0) | Add a new tint, adjust an existing token, add a primitive ramp |
| Major (0.1.0 → 1.0.0) | Replace hue family anchor, change typography, alter primary axis (rare) |

Tag every committed brand change:

```bash
git tag -a brand-ek-2026-Q3-v1 -m "Founding: Neo-Tokyo neon (magenta CTA + cyan secondary + lime alive)"
git push origin brand-ek-2026-Q3-v1
```

## What this skill does NOT do

- Generate slides (not on roadmap; ek is web-first)
- Export to Tailwind/shadcn (that's `ek-web` — backlog v0.2)
- Lint `.tsx`/`.css` (that's `ek-craft` — backlog v0.3)
- Run design-jury review (that's `ek-review` — backlog v0.4)
- Learn brands from URLs (single-tenant — maintains ek-design's brand only)
