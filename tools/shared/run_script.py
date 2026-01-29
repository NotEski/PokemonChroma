"""
Script execution utilities with async support for GUI.
"""

from __future__ import annotations

import io
import queue
import runpy
import sys
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Callable, List, Optional

from .models import ProgressUpdate, TaskResult  # type: ignore


def run_script(script_path: Path, args: List[str]) -> int:
    """
    Run a Python script synchronously (for CLI mode).

    Args:
        script_path: Path to the script to run
        args: Command-line arguments

    Returns:
        Exit code
    """
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


class AsyncScriptRunner:
    """Runs scripts asynchronously with progress tracking."""

    def __init__(self) -> None:
        self.thread: Optional[threading.Thread] = None
        self.cancel_event = threading.Event()
        self.output_queue: queue.Queue[str] = queue.Queue()
        self.progress_queue: queue.Queue[ProgressUpdate] = queue.Queue()

    def run(
        self,
        script_path: Path,
        args: List[str],
        on_complete: Callable[[TaskResult], None],
        on_progress: Optional[Callable[[ProgressUpdate], None]] = None,
        on_output: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Run script asynchronously in background thread.

        Args:
            script_path: Path to script
            args: Command-line arguments
            on_complete: Callback when execution completes
            on_progress: Optional callback for progress updates
            on_output: Optional callback for output lines
        """
        self.cancel_event.clear()

        def worker() -> None:
            start_time = time.time()
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            exit_code = 0

            old_argv = list(sys.argv)
            sys.argv = [str(script_path)] + list(args)

            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    runpy.run_path(str(script_path), run_name="__main__")
            except SystemExit as e:
                exit_code = e.code if isinstance(e.code, int) else 1
            except Exception as e:
                stderr_capture.write(f"Error: {e}\n")
                exit_code = 1
            finally:
                sys.argv = old_argv

            duration = time.time() - start_time

            result = TaskResult(
                success=(exit_code == 0),
                exit_code=exit_code,
                output=stdout_capture.getvalue(),
                errors=stderr_capture.getvalue(),
                duration=duration,
            )

            on_complete(result)

        self.thread = threading.Thread(target=worker, daemon=True)
        self.thread.start()

    def cancel(self) -> None:
        """Cancel the running script."""
        self.cancel_event.set()

    def is_running(self) -> bool:
        """Check if script is currently running."""
        return self.thread is not None and self.thread.is_alive()

