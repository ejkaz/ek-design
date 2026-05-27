#!/usr/bin/env bash
# build-portal-dist.sh
#
# Vercel build command. Runs on every deploy.
#
# 1. (Optional) regenerate the brand portal from yaml — only if Python is
#    available in the Vercel build image. Vercel's default Node image has
#    python3 available, so this works.
# 2. Copy the generated brand-portal/*.html into ./public/ which Vercel
#    then serves.
#
# Locally you can also run:
#   bash scripts/build-portal-dist.sh
# to verify the publish root before deploying.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORTAL_SRC="$REPO_ROOT/plugins/ek-design/skills/ek-design/brand-portal"
GEN_SCRIPT="$REPO_ROOT/plugins/ek-design/skills/ek-design/scripts/generate-brand-portal.py"
OUT_DIR="$REPO_ROOT/public"

echo "→ ek-design brand portal build"
echo "  REPO_ROOT: $REPO_ROOT"

# 1) Regenerate if Python is available (CI gets fresh; local dev relies on
#    the committed portal HTML being current).
if command -v python3 >/dev/null 2>&1; then
  echo "→ Python detected; ensuring pyyaml is installed"
  python3 -m pip install --quiet --upgrade pip pyyaml || true
  echo "→ Regenerating brand portal from design-model.yaml"
  python3 "$GEN_SCRIPT"
else
  echo "→ Python not available; serving committed brand portal HTML as-is"
fi

# 2) Copy to ./public for Vercel.
mkdir -p "$OUT_DIR"
rm -rf "$OUT_DIR"/*
cp -R "$PORTAL_SRC"/* "$OUT_DIR/"

# 3) Sanity: ensure index.html exists
if [ ! -f "$OUT_DIR/index.html" ]; then
  echo "ERROR: $OUT_DIR/index.html missing after build" >&2
  exit 1
fi

PAGE_COUNT=$(find "$OUT_DIR" -maxdepth 1 -name "*.html" | wc -l | tr -d ' ')
BYTES=$(du -sh "$OUT_DIR" | awk '{print $1}')
echo "✓ Built $PAGE_COUNT portal pages ($BYTES) into $OUT_DIR"
ls -la "$OUT_DIR"
