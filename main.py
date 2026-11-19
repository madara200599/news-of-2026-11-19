#!/usr/bin/env python3
"""Copy entry.png beside this file to the output directory.

Uses $MAKEFUN_OUTPUT_DIR when set, otherwise /output.
Standard library only, no network.
"""
import os
import shutil
from pathlib import Path


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(src, dest)
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
