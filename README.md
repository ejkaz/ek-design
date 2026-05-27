# ek-design

Eric Kazmaier's personal cyberpunk brand stack. Composable Claude Code plugin marketplace inheriting architecture from [`ejkaz/parspec-design`](https://github.com/ejkaz/parspec-design); brand tokens completely replaced with a Neo-Tokyo neon register tuned for agentic UI surfaces.

**Brand thesis**: Dark Ledger / Neon Operator.
**Principle**: *Purple is the world. Magenta is the command. Cyan is the proof.*

First consumer: [`cepsra`](https://github.com/ejkaz/cepsra) (codename for KazOS, cepsr.app).

- 📚 **Live brand portal**: [ek-design.vercel.app](https://ek-design.vercel.app) *(after first Vercel deploy)*
- 📦 **npm package**: [`@ekdesign/web`](https://www.npmjs.com/package/@ekdesign/web) *(after first publish)*

## What's in this repo

| Plugin | State | Job |
|---|---|---|
| **`ek-design`** | **v0.2.1** | Maintains `design-model.yaml` — the single brand SSoT. Brand portal generator emits 6 pages (overview, color, typography, motifs, components, cockpit reference). |
| **`ek-web`** | **v0.2.0** | Exports tokens to 4 formats: Tailwind v4 CSS-first (default), legacy Tailwind v3 JS, shadcn theme, flat CSS vars. Publishes as `@ekdesign/web` on npm. |
| **`ek-craft`** | **v0.1.0** | Lints `.tsx`/`.css` against brand rules. Data-driven from yaml (avoid list, primary axis, invariants). |
| `ek-review` | backlog | 4-juror design jury (composition, contrast, brand-fidelity, anti-slop) on rendered web UI screenshots. |

The `design-model.yaml` is the contract. Brand evolution = yaml diff + git tag → exporters re-emit → consumers pick up via `pnpm update @ekdesign/web` (web) or `/plugin update` (Claude Code skills).

## Install

### As Claude Code plugins

```bash
# Local-file marketplace (before pushing to GitHub):
/plugin marketplace add file:///Users/eric/Desktop/Parspec.b/Vault/005_The_Lab/5.3_Automation_&_Scripts/ek-design

# Or from GitHub:
/plugin marketplace add ejkaz/ek-design

# Install plugins (all four optional):
/plugin install ek-design@ek-design
/plugin install ek-web@ek-design
/plugin install ek-craft@ek-design
```

### As an npm package (web consumers)

```bash
pnpm add @ekdesign/web   # or bun add / npm install
```

Then in `app/globals.css`:

```css
@import "tailwindcss";
@import "@ekdesign/web/tailwind-v4.css";
```

See the [package README](plugins/ek-web/skills/ek-web/package/README.md) for full integration patterns (Tailwind v4, Tailwind v3, shadcn, plain CSS).

## Locked primary axis

Foundation + Operator Signal. v0.2.1 demoted lime out of axis to Semantic States.

| Token | Hex | Role |
|---|---|---|
| Background | `#070711` | Default surface — deep violet-black |
| Panel | `#171727` | Layered surface (surface_2) |
| Off-white | `#F0F0F5` | Inverted (light-mode opt-in) |
| White | `#FFFFFF` | Text on dark |
| **Magenta Command** | `#FF2A6D` | Operator Signal · agentic command monopoly |
| **Cyan Trace** | `#00D1FF` | Operator Signal · proof / lineage / inspectability |
| Display | **Chakra Petch** | Headers, eyebrows, chrome |
| Body | **Inter** | UI body |
| Mono | **JetBrains Mono** | Identifiers + finance numerics (tnum) — required |

Signature motifs: neon edge glow · terminal block inset · katakana-numeric ID · scanline overlay · diagonal cut corner · dark ledger panel · neon operator layer · trace rail (cyan proof rail) · agent event feed · forecast confidence halo · board-safe mode · executive command state · machine identifier strip · steel-violet architecture (14 total).

## How to evolve the brand

1. Edit `plugins/ek-design/skills/ek-design/design-model.yaml`
2. Bump `meta.version` (and `meta.brand_version` if it's a hue / family change)
3. Update `primitives.*`, `roles.*`, `tokens.*`, `avoid:` list as needed
4. Run the generator + exporters:
   ```bash
   python3 plugins/ek-design/skills/ek-design/scripts/generate-brand-portal.py
   python3 plugins/ek-web/skills/ek-web/scripts/build-package.py
   ```
5. Commit:
   ```bash
   git add -A
   git commit -m "Brand v<new-version> — <one-line rationale>"
   ```
6. Tag (two distinct tag spaces — schema vs brand lock):
   ```bash
   # Schema-version tag (every release; lightweight or annotated)
   git tag -a v0.X.Y -m "Schema v0.X.Y refinement"

   # Brand-version tag (only on a new locked brand)
   git tag -a brand-ek-2026-QN-vN -m "Locked brand: <rationale>"

   # npm-publish trigger tag (kicks the publish-web workflow)
   git tag -a web-v0.X.Y -m "npm: @ekdesign/web v0.X.Y"

   git push origin main v0.X.Y brand-ek-2026-QN-vN web-v0.X.Y
   ```
7. CI publishes `@ekdesign/web` to npm. Vercel auto-deploys the brand portal.

## How to roll back

```bash
# Schema-only
git checkout v0.2.0 -- plugins/ek-design/skills/ek-design/design-model.yaml

# Brand-version snapshot
git checkout brand-ek-2026-Q3-v1 -- plugins/ek-design/skills/ek-design/design-model.yaml
```

## Brand version history

| Tag | Date | Notes |
|---|---|---|
| `brand-ek-2026-Q3-v1` | 2026-05-24 | v0.1.0 founding — Neo-Tokyo neon. Magenta CTA · cyan · lime on `#0A0A14`. 7 invariants. |
| `brand-ek-2026-Q4-v1` | 2026-05-24 | v0.2.0 — Dark Ledger / Neon Operator. Surface undertone shift to `#070711`. Finance directionality family. 13 motifs. 15 invariants. |
| `v0.2.1` (schema-only) | 2026-05-25 | Lime demoted from primary axis. Principle: "Purple is the world. Magenta is the command. Cyan is the proof." Operator glow reduced ~50%. 19 invariants. Brand version unchanged. |

## Repository deployment

### npm — `@ekdesign/web`

Built and published from `plugins/ek-web/skills/ek-web/package/`. CI workflow at `.github/workflows/publish-web.yml` triggers on tag push matching `web-v*.*.*`.

Required GitHub repo secret: `NPM_TOKEN` (granular automation token with read-write access to `@ekdesign/web`).

First publish (one-time):
```bash
# 1. Create npm org @ekdesign at https://www.npmjs.com/org/create (free)
# 2. npm login locally
# 3. Manual first publish:
cd plugins/ek-web/skills/ek-web/package
python3 ../scripts/build-package.py    # builds dist/, stamps version
npm publish --access public
# 4. Generate automation token, add as NPM_TOKEN repo secret
# 5. Subsequent releases via tag push trigger CI automatically
```

### Vercel — `ek-design.vercel.app`

Brand portal hosted as a static site. Build script `scripts/build-portal-dist.sh` regenerates the portal from yaml then copies `brand-portal/*` to `public/` which Vercel serves.

First deploy (one-time):
```bash
# In repo root
vercel link              # associate with team eric-kazmaiers-projects
vercel --prod            # first production deploy
# Subsequent pushes to main auto-deploy via Vercel's GitHub integration
```

`vercel.json` declares the build command, output directory, cache headers, and a `/` → `/index` redirect. The portal serves at `https://ek-design.vercel.app` (free tier) or any custom domain you point at it.

## Credits

Architecturally forked from [`ejkaz/parspec-design`](https://github.com/ejkaz/parspec-design) — composable-plugin pattern, yaml-frontmatter versioning, data-driven invariants. Parspec brand tokens were completely replaced; only the architecture carries over. Both repos remain independent; improvements propagate via pattern, not code-sharing.

## License

MIT.
