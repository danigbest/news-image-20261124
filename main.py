"""Copy the rendered entry image to the make.fun output directory.

Stdlib only: the grader runs this with plain python3 and no Pillow.
Expects output/entry.png next to this file and MAKEFUN_OUTPUT_DIR set.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "output" / "entry.png"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if not out_dir:
        raise SystemExit("MAKEFUN_OUTPUT_DIR is not set")
    dest = Path(out_dir) / "entry.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, dest)
    print("wrote", dest)


if __name__ == "__main__":
    main()
