import sys
import runpy
from pathlib import Path
from typing import List


def run_script(script_path: Path, args: List[str]) -> int:
    old_argv = list(sys.argv)
    sys.argv = [str(script_path)] + list(args)
    try:
        runpy.run_path(str(script_path), run_name="__main__")
        return 0
    except SystemExit as e:
        # Propagate exit codes from scripts
        code = e.code if isinstance(e.code, int) else 1
        return int(code)
    finally:
        sys.argv = old_argv
