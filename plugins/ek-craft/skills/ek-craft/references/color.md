# Color Discipline — ek-design Edition

Three rules govern every color decision:

1. **Magenta is the only primary CTA.** Cyan is secondary / info / link. Lime is alive / success. Red is error. Amber is warn. Decorative use of any of these collapses their semantic load.
2. **Mode determines the type-on-color binding.** Magenta-on-dark uses `magenta.500`; magenta-on-light uses `magenta.800`. Mixing modes is a WCAG fail and a brand fail.
3. **Tokens > primitives > hex.** Reach for role tokens (`bg-cta`, `text-info`) first. Primitives (`bg-magenta-500`, `text-cyan-700`) when the role is wrong. Hex literals only inside `:root` or the `@theme` block.

## Locked invariants (from design-model.yaml)

These can never be silently relaxed; relaxing requires a `design-model.yaml` change + a brand_version bump.

| Invariant | What it catches | Severity |
|---|---|---|
| `magenta_cta_monopoly` | Any non-magenta hex as primary button fill | error |
| `cyan_secondary_and_info` | Cyan used as primary CTA fill | error |
| `lime_alive_and_success_only` | Lime as decoration (chart non-success, hero accent) | error |
| `red_error_only` | Red as decoration (chart non-error, hero accent) | error |
| `amber_warn_only` | Amber as decoration | error |
| `no_consumer_indigo_purple` | `#6366F1` / `#8B5CF6` / `#A78BFA` anywhere | error |
| `dark_primary_register` | `app` or `marketing` surface with light background | warning |
| `accent_type_on_light_forbidden` | `magenta.500` as type on `off_white` / `white` | error |

## Banned color families

| Family | Examples | Why |
|---|---|---|
| Tailwind Indigo / consumer violet | `#6366F1`, `#8B5CF6`, `#A78BFA`, `#7C3AED` | Single biggest AI-template tell of 2024-2026 |
| Sci-fi cliché cyan | `#00FFFF` pure cyan | Reads as Tron cosplay; ek uses `#00D1FF` (cyan.500) biased toward blue |
| Pastels | Any sat<30% + light>75% | Off-register for cyberpunk; pastels collapse the neon contrast |

## Reach-for table

| Need | Use |
|---|---|
| Primary action button | `bg-cta` (= `bg-magenta-500`) |
| Hover state of primary | `hover:bg-cta-hover` (= `bg-magenta-600`) |
| Secondary action | `bg-secondary` (= `bg-cyan-500`) or ghost: `border border-cyan-500 text-cyan-500` |
| Destructive action | `bg-destructive` (= `bg-red-500`) |
| Link | `text-link` (= `text-cyan-500`) on dark; `text-link-on-light` (= `text-cyan-700`) on light |
| Success state | `text-success` (= `text-lime-500`) |
| Warning state | `text-warn` (= `text-amber-500`) |
| Error state | `text-error` (= `text-red-500`) |
| Info badge | `bg-info/10 text-info border border-info/30` |
| Agent active indicator | `text-agent-active` (= `text-lime-500`) + `shadow-neon-glow-lime` |
| Agent thinking | `text-agent-thinking` (= `text-cyan-500`) + pulse animation |
| Body background | `bg-bg` (= `bg-background`, = `#0A0A14`) |
| Panel surface | `bg-panel` (= `bg-neutral-850`, = `#15151F`) |
| Border default | `border-border` (= `#2E2E40`) |
| Focus ring | `shadow-focus-ring-magenta` for actions, `shadow-focus-ring-cyan` for inputs |
| Atmospheric hero glow | `bg-steel-violet-700` panel or `shadow-[0_0_80px_var(--color-steel-violet-500)]` |

## Common mistakes

| Mistake | Fix |
|---|---|
| `<button className="bg-indigo-500">` | `<button className="bg-cta">` |
| `<button className="bg-cyan-500">` (primary intent) | `<button className="bg-cta">` (cyan is secondary, not primary) |
| `<h1 className="text-magenta-500">` on light bg | `<h1 className="text-magenta-800">` |
| `<div className="bg-gradient-to-r from-purple-500 to-pink-500">` | `<div className="bg-bg shadow-neon-glow-magenta">` |
| `text-green-500` for success | `text-success` (semantic-locked to lime.500) |
| `text-red-500` for any accent | `text-error` only — red is locked to error semantics |
| `bg-orange-500` (any orange) | Wrong register entirely. ek has no orange. Use `bg-cta` (magenta) for primary action. |

## When in doubt

Use a role token. If no role token applies, use a primitive in the locked ramps (`magenta`, `cyan`, `lime`, `steel-violet`, `slate`, `red`, `amber`, `neutral`). If neither fits, you probably need a new role token in `design-model.yaml` — open an issue at ek-design rather than reaching for a fresh hex.
