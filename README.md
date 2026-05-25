# ek-design

Eric Kazmaier's personal cyberpunk brand stack. Composable Claude Code plugin marketplace inheriting architecture from [`ejkaz/parspec-design`](https://github.com/ejkaz/parspec-design); brand tokens completely replaced with a Neo-Tokyo neon register tuned for agentic UI surfaces.

First consumer: [`cepsra`](https://github.com/ejkaz/cepsra) (cepsr.app).

## What's in this repo

| Plugin | State | Job |
|---|---|---|
| **`ek-design`** | **v0.1.0 shipped** | Maintains `design-model.yaml` — the single brand SSoT. Versioned via YAML frontmatter + git tags; rollback is one command. |
| `ek-web` | backlog | Exports tokens to Tailwind config / shadcn theme / flat CSS vars. v0.2 target. |
| `ek-craft` | backlog | Lints `.tsx`/`.css` against brand rules. Data-driven from yaml. v0.3 target. |
| `ek-review` | backlog | 4-juror design jury (composition, contrast, brand-fidelity, anti-slop) on rendered web UI screenshots. v0.4 target. |

The `design-model.yaml` is the contract. Brand evolution = yaml diff + git tag. Downstream skills auto-adapt as they ship.

## Install

```bash
# Local-file marketplace (before pushing to GitHub):
/plugin marketplace add file:///Users/eric/Desktop/Parspec.b/Vault/005_The_Lab/5.3_Automation_&_Scripts/ek-design

# After GitHub push:
/plugin marketplace add ejkaz/ek-design

# Then:
/plugin install ek-design@ek-design
```

Then in any Claude Code session:

| You say | Skill activates |
|---|---|
| "Show me the ek-design brand" | `ek-design` |
| "Update ek-design palette" | `ek-design` |
| "Roll back to ek-2026-Q3-v1" | `ek-design` |

## Locked primary axis

The immovable anchors. Any palette evolution may change tints / atmospheric secondaries / motifs — but never these:

| Token | Hex | Role |
|---|---|---|
| Background | `#0A0A14` | Default surface — deep blue-black Tokyo night |
| Panel | `#15151F` | Layered surface |
| Off-white | `#F0F0F5` | Inverted (light-mode opt-in) |
| White | `#FFFFFF` | Text on dark |
| Magenta CTA | `#FF2A6D` | Primary CTA monopoly |
| Cyan Secondary | `#00D1FF` | Secondary action / info / link |
| Lime Alive | `#A6FF00` | Success state + agent active indicator |
| Display | **Chakra Petch** | Headers, eyebrows |
| Body | **Inter** | UI body |
| Mono | **JetBrains Mono** | Code, IDs, timestamps — required for agentic UI |

Signature motifs: neon edge glow (CSS box-shadow), terminal-block insets (mono content on cyan-bordered black), scanline overlays (optional, reduced-motion-safe), katakana-numeric agent IDs.

## How to evolve the brand

1. Edit `plugins/ek-design/skills/ek-design/design-model.yaml`
2. Bump `meta.version` and `meta.brand_version`; set `meta.supersedes`
3. Update `primitives.*`, `roles.*`, `tokens.*`, `avoid:` list
4. Commit + tag:
   ```bash
   git tag -a brand-ek-2026-Q4-v1 -m "Q4 evolution: <rationale>"
   git push origin main brand-ek-2026-Q4-v1
   ```
5. Run `/plugin update` — downstream skills (when they ship) pick up new tokens automatically

## How to roll back

```bash
git checkout brand-ek-2026-Q3-v1 -- plugins/ek-design/skills/ek-design/design-model.yaml
```

## Brand version history

| Tag | Date | Notes |
|---|---|---|
| `brand-ek-2026-Q3-v1` | 2026-05-24 | v0.1.0 founding — Neo-Tokyo neon palette ratified. Magenta CTA `#FF2A6D`, cyan `#00D1FF`, lime `#A6FF00` on `#0A0A14`. Chakra Petch + Inter + JetBrains Mono. 7 invariants. |

## Credits

Architecturally forked from [`ejkaz/parspec-design`](https://github.com/ejkaz/parspec-design) — composable-plugin pattern, yaml-frontmatter versioning, data-driven invariants. Parspec brand tokens were completely replaced; only the architecture carries over. Both repos remain independent; improvements propagate via pattern, not code-sharing.

## License

MIT.
