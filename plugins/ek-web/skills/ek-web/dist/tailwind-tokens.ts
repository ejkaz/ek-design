// AUTO-GENERATED FROM ek-design design-model.yaml — DO NOT EDIT MANUALLY
// Source: ek-design v0.2.1 · brand_version: ek-2026-Q4-v1
// Generated: 2026-05-25T07:09:16Z
// Regenerate: python3 plugins/ek-web/skills/ek-web/scripts/export-tailwind.py

/**
 * ek-design tokens for Tailwind v4.
 *
 * Wire into tailwind.config.ts:
 *   import { ekTokens } from "<path>/ek-design/plugins/ek-web/skills/ek-web/dist/tailwind-tokens"
 *   export default { content: [...], theme: { extend: ekTokens } }
 *
 * After import you get utility classes:
 *   bg-magenta-500   text-cyan-500   font-display   font-mono   rounded-control
 *   shadow-neon-glow-magenta   transition-duration-fast   ease-ek   p-md
 */
export const ekTokens = {
  colors: {
    bg: "#070711",
    panel: "#171727",
    "off-white": "#F0F0F5",
    "terminal-bg": "#000000",
    "neutral": {
    0: "#FFFFFF",
    50: "#F0F0F5",
    100: "#E0E0EA",
    200: "#C8C8D6",
    300: "#A8A8BC",
    400: "#7A7A92",
    500: "#5C5C70",
    600: "#3F3F50",
    700: "#2C2A45",
    800: "#23233A",
    850: "#171727",
    900: "#10101A",
    950: "#070711",
    1000: "#000000",
    },
    "magenta": {
    50: "#FFE5EF",
    100: "#FFCCDF",
    200: "#FF99BF",
    300: "#FF7BAA",
    400: "#FF4D8C",
    500: "#FF2A6D",
    600: "#E11D5F",
    700: "#B0144A",
    800: "#7A0E33",
    900: "#4F0820",
    },
    "cyan": {
    50: "#E0FAFF",
    100: "#B8F3FF",
    200: "#80EAFF",
    300: "#5EEAFF",
    400: "#2DD9FF",
    500: "#00D1FF",
    600: "#00A3CC",
    700: "#0090B8",
    800: "#005F77",
    900: "#003344",
    },
    "lime": {
    50: "#F2FFCC",
    100: "#E5FF99",
    200: "#D2FF66",
    300: "#C8FF40",
    400: "#B3FF1A",
    500: "#A6FF00",
    600: "#86CC00",
    700: "#6B9E00",
    800: "#4A6E00",
    900: "#2A3F00",
    },
    "steel-violet": {
    300: "#6B6BC4",
    500: "#3B3B92",
    700: "#1E1E60",
    900: "#0F0F33",
    },
    "slate": {
    50: "#F2F2F7",
    100: "#E0E0E8",
    300: "#9999B0",
    500: "#5C5C70",
    700: "#2E2E40",
    900: "#15151F",
    },
    "red": {
    500: "#FF003C",
    600: "#CC0030",
    700: "#B0142D",
    },
    "amber": {
    500: "#FFB800",
    600: "#CC9300",
    700: "#8C6500",
    },
    "finance": {
    "gain": "#4ADE80",
    "loss": "#F87171",
    "watch": "#FBBF24",
    "info_blue": "#60A5FA",
    },
  },
  fontFamily: {
    display: ['"Chakra Petch"', "sans-serif"],
    sans: ['"Inter"', "system-ui", "sans-serif"],
    mono: ['"JetBrains Mono"', "ui-monospace", "SF Mono", "Menlo", "monospace"],
  },
  spacing: {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
    "4xl": "96px",
    "5xl": "128px",
  },
  borderRadius: {
    "element": "2px",
    "control": "4px",
    "component": "6px",
    "container": "8px",
    "pill": "9999px",
  },
  boxShadow: {
    "neon-glow-magenta": "0 0 8px #FF2A6D, 0 0 16px #FF2A6D40",
    "neon-glow-cyan": "0 0 8px #00D1FF, 0 0 16px #00D1FF40",
    "neon-glow-lime": "0 0 6px #A6FF00, 0 0 12px #A6FF0040",
    "focus-ring-magenta": "0 0 0 2px #070711, 0 0 0 4px #FF2A6D",
    "focus-ring-cyan": "0 0 0 2px #070711, 0 0 0 4px #00D1FF",
    "panel-lift": "0 1px 0 0 #2C2A45, 0 8px 24px -8px #00000080",
    "trace-rail-glow-cyan": "0 0 4px #00D1FF80",
    "operator-layer-glow": "0 0 0 1px #FF2A6D40, 0 0 10px #FF2A6D33",
    "board-safe-neon-glow-magenta": "inset 0 0 0 1px #FF2A6D",
    "board-safe-neon-glow-cyan": "inset 0 0 0 1px #00D1FF",
    "board-safe-neon-glow-lime": "inset 0 0 0 1px #A6FF00",
    "board-safe-focus-ring": "0 0 0 2px #FF2A6D",
  },
  transitionTimingFunction: {
    ek: "cubic-bezier(0.2, 0.8, 0.2, 1)",
  },
  transitionDuration: {
    fast: "100ms",
    normal: "200ms",
    slow: "400ms",
  },
} as const

export type EkTokens = typeof ekTokens
