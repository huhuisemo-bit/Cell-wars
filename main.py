# /// script
# dependencies = ["pygame-ce"]
# ///

import os
import runpy
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)
runpy.run_path(os.path.join(SRC, "main.py"), run_name="__main__")
