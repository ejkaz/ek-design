---
name: ek-craft
description: "Brand-compliance lint for ek-design consumers. Lints .tsx / .jsx / .css / .html / .md against universal anti-AI-slop rules (cyberpunk-web register) + data-driven rules read from the sibling ek-design plugin's design-model.yaml (avoid list, primary axis, invariants). Use when reviewing a cepsra PR, auditing a marketing page, or checking any output for brand drift. Triggers: 'lint this for ek brand', 'is this on-brand', 'ek-craft check', 'audit this tsx', 'ek compliance', '/ek-craft'."
version: 0.1.0
allowed-tools: [Read, Glob, Grep, Bash]
---

# ek-craft

Brand compliance lint. Two layers, one purpose.

## How it works

| Layer | Source | What it catches |
|---|---|---|
| **Universal** | `references/anti-ai-slop.md`, `color.md`, `typography.md` | Generic AI-template tells in a web/React context: Tailwind-indigo accent, gradient-mesh hero, glassmorphism heavy blur, drop-shadow-as-elevation, emoji-as-icon, lorem ipsum |
| **Data-driven** | `../../ek-design/skills/ek-design/design-model.yaml` `avoid:` + `primary_axis_preserved:` + `invariants:` | Brand-version-specific: forbidden hex codes, forbidden fonts, hex literals where role tokens exist, magenta-CTA monopoly violations, mono-for-identifiers misses, semantic-locked-status leaks |

The data-driven layer is the load-bearing one. When the ek brand evolves (yaml diff + git tag), this skill auto-adapts — no code changes here.

## Two ways to invoke

### A) Python linter (deterministic, CI-friendly, recommended)

```bash
# Lint a single file
python3 scripts/ek-craft.py /path/to/cepsra/src/app/page.tsx

# Lint a glob
python3 scripts/ek-craft.py /path/to/cepsra/src/**/*.tsx

# JSONL output for machine consumption
python3 scripts/ek-craft.py --format jsonl /path/to/files

# Severity filter
python3 scripts/ek-craft.py --severity error /path/to/files

# Point at a specific design-model.yaml
python3 scripts/ek-craft.py --model /path/to/design-model.yaml /path/to/files
```

Exit code 0 = clean (no errors); 1 = errors present; 2 = lint crashed.

### B) Claude-driven review (qualitative, narrative)

When the user says "lint this for ek brand" without invoking the script:

1. **Locate `design-model.yaml`.** Try in order:
   - `../../ek-design/skills/ek-design/design-model.yaml` (sibling plugin in this repo)
   - `~/.claude/plugins/ek-design/skills/ek-design/design-model.yaml`
   - User-supplied path
2. **Read** the target file(s) + design-model.yaml.
3. **Universal rules** — apply `references/anti-ai-slop.md` + `color.md` + `typography.md`.
4. **Data-driven rules** — for every entry in `avoid:`, `primary_axis_preserved:`, `invariants:`, apply matchers below.
5. **Report** as a table: `file:line · severity · rule · finding · suggestion`.

## What the linter checks

| Rule | Source | What it catches | Severity |
|---|---|---|---|
| `avoid.color` | yaml `avoid[].color` | hex literal anywhere in file (case-insensitive) | error/warning |
| `avoid.color_family` | yaml `avoid[].color_family` | hex in the named family range | error/warning |
| `avoid.font_family` | yaml `avoid[].font_family` | `font-family:` declaration or `font-<name>` Tailwind class | error/warning |
| `avoid.pattern` | yaml `avoid[].pattern` | named pattern (emoji-as-icon, gradient-mesh, etc.) | error/warning |
| `magenta_cta_monopoly` | yaml `invariants` | non-magenta hex used as primary button bg | error |
| `mono_for_identifiers` | yaml `invariants` | `<code>` or `<pre>` without `font-mono`; identifier-looking text in non-mono | warning |
| `no_consumer_indigo_purple` | yaml `invariants` | Tailwind classes `bg-indigo-*`, `bg-violet-*`, `bg-purple-*` | error |
| `prefer_role_tokens` | yaml `roles` keys | hex literal that exactly matches a role-resolved hex (suggest `bg-magenta-500` etc.) | info |
| `reduced_motion_required` | yaml `invariants` | CSS file with `@keyframes` but no `prefers-reduced-motion` override | warning |
| `accent_type_on_light_forbidden` | yaml `invariants` | `text-magenta-500` on `bg-off-white` (AA fail) | warning |

## Output format

Default (human):
```
src/app/page.tsx:42  error    avoid.color           #6366F1 (Tailwind Indigo 500) — forbidden
                                                     → use --color-magenta-500 / bg-magenta-500
src/app/page.tsx:55  warning  mono_for_identifiers  identifier-looking <span> not in font-mono
                                                     → wrap in font-mono or use <code>
```

JSONL (`--format jsonl`):
```json
{"file":"src/app/page.tsx","line":42,"col":18,"severity":"error","rule":"avoid.color","value":"#6366F1","message":"Forbidden color: Tailwind Indigo 500","suggestion":"use --color-magenta-500 / bg-magenta-500"}
```

## What this skill does NOT do

- Refactor — the linter reports; the consumer (you or Claude) fixes.
- Auto-fix — explicit by design. Brand violations should be conscious.
- Visual review (rendered pixels) — that's `ek-review` (backlog v0.4).
- Mutate `design-model.yaml` — read-only consumer.
- Validate `design-model.yaml` itself — that's `ek-design` (the SSoT).

## Related references

- `references/anti-ai-slop.md` — 10 cardinal sins + soft tells, cyberpunk-web register
- `references/color.md` — color discipline (magenta monopoly, semantic-locked statuses, no consumer indigo)
- `references/typography.md` — Chakra Petch / Inter / JetBrains Mono, mono-for-identifiers invariant
