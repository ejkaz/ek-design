#!/usr/bin/env python3
"""
build-package.py — assemble the @ekdesign/web npm package directory.

What it does:
  1. Runs all 4 ek-web exporters (tailwind-v4 / tailwind / shadcn / css-vars)
  2. Copies dist/* into package/dist/
  3. Stamps the yaml meta.version into package/package.json (in-place edit)
  4. Validates the result with `npm pack --dry-run` if npm is on PATH

After this runs, package/ is publishable:
  cd package && npm publish    # one-time `npm login` first

Used by CI (.github/workflows/publish-web.yml) on tag push.
Used locally when you want to dry-run a publish.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DIST_DIR = SKILL_DIR / "dist"
PACKAGE_DIR = SKILL_DIR / "package"
PACKAGE_DIST = PACKAGE_DIR / "dist"
EK_DESIGN_YAML = SKILL_DIR.parents[2] / "ek-design" / "skills" / "ek-design" / "design-model.yaml"


def run_exporters():
    """Run all 4 exporters. Each writes to dist/."""
    print("→ Running ek-web exporters...")
    for name in ["export-tailwind-v4", "export-tailwind", "export-shadcn", "export-css-vars"]:
        path = SCRIPT_DIR / f"{name}.py"
        result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: {name} failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(2)
        print(f"  {result.stdout.strip()}")


def copy_dist_to_package():
    """Mirror dist/* → package/dist/."""
    if PACKAGE_DIST.exists():
        shutil.rmtree(PACKAGE_DIST)
    PACKAGE_DIST.mkdir(parents=True)
    for f in DIST_DIR.iterdir():
        if f.is_file():
            shutil.copy(f, PACKAGE_DIST / f.name)
    print(f"→ Copied {len(list(PACKAGE_DIST.iterdir()))} files into package/dist/")


def load_yaml_version() -> str:
    with EK_DESIGN_YAML.open() as f:
        model = yaml.safe_load(f)
    return str(model["meta"]["version"])


def stamp_package_version():
    """Set package.json `version` to match yaml meta.version."""
    pkg_path = PACKAGE_DIR / "package.json"
    pkg = json.loads(pkg_path.read_text())
    new_version = load_yaml_version()
    old_version = pkg.get("version", "?")
    pkg["version"] = new_version
    pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
    print(f"→ Stamped package.json version: {old_version} → {new_version}")


def validate_with_npm():
    """Optional: run `npm pack --dry-run` to validate the publishable shape."""
    if shutil.which("npm") is None:
        print("→ npm not on PATH; skipping validation")
        return
    print("→ Validating with `npm pack --dry-run`...")
    result = subprocess.run(
        ["npm", "pack", "--dry-run", "--json"],
        cwd=PACKAGE_DIR, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"WARNING: npm pack reported issues:\n{result.stderr}", file=sys.stderr)
    else:
        try:
            data = json.loads(result.stdout)
            files = data[0]["files"] if data else []
            print(f"  → would publish {len(files)} files, total {data[0]['size'] // 1024}KB unpacked")
            for f in files[:10]:
                print(f"     · {f['path']}")
            if len(files) > 10:
                print(f"     · ... +{len(files) - 10} more")
        except (json.JSONDecodeError, KeyError, IndexError):
            print(f"  → npm pack succeeded but output unparseable; first 500 chars:\n{result.stdout[:500]}")


def main() -> int:
    run_exporters()
    copy_dist_to_package()
    stamp_package_version()
    validate_with_npm()
    print(f"\n✓ Package ready at: {PACKAGE_DIR}")
    print(f"  To publish:  cd {PACKAGE_DIR} && npm publish")
    print(f"  To dry-run:  cd {PACKAGE_DIR} && npm publish --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
