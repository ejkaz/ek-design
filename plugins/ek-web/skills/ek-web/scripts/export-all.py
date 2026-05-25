#!/usr/bin/env python3
"""
export-all.py — run all three ek-web exporters in sequence.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


def main() -> int:
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))

    modules = ["export_tailwind", "export_shadcn", "export_css_vars"]
    # Hyphen → underscore for python module names
    for mod_name in ["export-tailwind", "export-shadcn", "export-css-vars"]:
        py_name = mod_name.replace("-", "_")
        # Import the .py file directly since filenames use hyphens
        path = here / f"{mod_name}.py"
        spec_globals = {"__name__": "__not_main__", "__file__": str(path)}
        with open(path) as f:
            code = compile(f.read(), str(path), "exec")
        exec(code, spec_globals)
        spec_globals["main"]()

    print("\nAll exporters complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
