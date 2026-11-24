#!/usr/bin/env python3
"""Entrypoint for the News Image 24 November 2026 entry.

The grader runs this file with the standard library only. Its only job
is to place the pre-rendered image where the grader expects it.
No network access, no third-party imports, no side effects.
"""

import os
import shutil
import sys


def locate_source() -> str:
    """Return the absolute path of the bundled entry image."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "output", "entry.png")


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    src = locate_source()
    if not os.path.isfile(src):
        print(f"entry image missing: {src}", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print(f"wrote {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
