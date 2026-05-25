# Typography Discipline — ek-design Edition

Three families. Three jobs. No overlap.

| Family | CSS var | Tailwind | Job |
|---|---|---|---|
| **Chakra Petch** | `--font-display` | `font-display` | Headers, hero, eyebrows, UI chrome (buttons, badges). Cyber-coded angled cuts at production legibility. |
| **Inter** | `--font-sans` | `font-sans` (default) | UI body, labels, prose. Neutral workhorse. |
| **JetBrains Mono** | `--font-mono` | `font-mono` | Code, file paths, IDs, timestamps, model names, hashes, token counts. **Mandatory for any identifier.** |

## Locked invariants

### `mono_for_identifiers` (error)

Any identifier — anything a human would copy/paste to debug or reference — must be `font-mono`. This is the single biggest UX win in operator interfaces.

What counts as an identifier:
- File paths: `/Users/eric/cepsra/src/app/page.tsx`
- IDs / hashes: `agent_0042`, `pr_00139`, `7a8b9c2d`
- Timestamps: `2026-05-24T22:35:54.013Z`, `212ms`
- Model names: `claude-opus-4-7`, `gpt-image-2`
- Token / cost counts: `4,247 tokens`, `$0.0089`
- Tool names in agent output: `bash`, `web_search`
- API endpoints: `POST /api/agents/invoke`
- Environment variables: `EMAIL_ALLOWLIST`

How to render:
```tsx
{/* preferred — semantic */}
<code className="font-mono text-cyan-500">{model}</code>

{/* acceptable — span + mono class */}
<span className="font-mono">{agentId}</span>

{/* WRONG — identifier in body font */}
<span>{agentId}</span>
```

### Display register

Headers (`<h1>` through `<h3>`), eyebrows, buttons, badges, and UI chrome use Chakra Petch via `font-display`. Body text uses Inter (the Tailwind `font-sans` default, which resolves to Inter via the locked `--font-sans` token).

```tsx
{/* hero */}
<h1 className="font-display text-display font-bold">Boot the agent</h1>

{/* section header */}
<h2 className="font-display text-h2 font-semibold">Recent runs</h2>

{/* eyebrow */}
<p className="font-display text-eyebrow uppercase tracking-[0.18em] text-magenta-500">
  Agent · 0042
</p>

{/* button */}
<button className="font-display font-semibold text-sm tracking-wide bg-cta">
  Run
</button>

{/* body */}
<p className="text-body text-foreground">{taskDescription}</p>
```

## Banned fonts

| Font | Why banned |
|---|---|
| `Roboto` | Material-default; not ek register |
| `Arial` | System default; never as display |
| `Helvetica` | Reads corporate; not ek |
| `system-ui` | Inherits OS default; loses brand identity |
| `Comic Sans MS` | Obvious |
| `Orbitron` | Sci-fi cosplay; too costume-y |
| `Press Start 2P` | 8-bit pixel; wrong register |
| `VT323` / `Audiowide` / `Bungee` | Same — costume cyberpunk, not production |

Inter is NOT banned — it's `font-sans`. Only flag Inter if it appears on `<h*>`, hero copy, or display roles.

## Scale ladder

Use Tailwind type-scale utility classes pinned to the locked clamp values:

| Class | Resolves to | Use |
|---|---|---|
| `text-display` | `clamp(2.5rem, 6vw, 5.5rem)` | Hero |
| `text-h1` | `clamp(1.875rem, 4.5vw, 3.75rem)` | Page title |
| `text-h2` | `clamp(1.5rem, 3vw, 2.5rem)` | Section header |
| `text-h3` | `clamp(1.125rem, 2vw, 1.5rem)` | Subsection |
| `text-body-lg` | `clamp(1rem, 1.6vw, 1.125rem)` | Lead paragraph |
| `text-body` | `clamp(0.875rem, 1.4vw, 1rem)` | Body |
| `text-small` | `clamp(0.75rem, 1vw, 0.875rem)` | Meta, labels |
| `text-eyebrow` | `clamp(0.7rem, 0.9vw, 0.85rem)` | Section eyebrows |
| `text-mono` | `clamp(0.8125rem, 1.1vw, 0.9375rem)` | Mono inline |
| `text-mono-sm` | `clamp(0.6875rem, 0.85vw, 0.8125rem)` | Small mono (badges, timestamps) |
| `text-code` | `clamp(0.8125rem, 1.1vw, 0.9375rem)` | Code blocks |

Never hardcode `text-[1.2rem]` or `text-2xl` — use the locked scale or extend `design-model.yaml` upstream.

## Common mistakes

| Mistake | Fix |
|---|---|
| `<h1 className="font-sans">` | `<h1 className="font-display">` |
| `<span>{userId}</span>` | `<code className="font-mono">{userId}</code>` |
| `<h1 className="text-4xl">` | `<h1 className="text-display">` |
| `<p style={{ fontFamily: "Inter" }}>` | Drop the inline; body inherits Inter via `font-sans` default |
| `<button className="font-sans">` | `<button className="font-display">` (UI chrome is display register) |
