"""
Abstract base class for toolbox plugins with GUI support.
"""

from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .models import FormFieldSpec, PluginMetadata  # type: ignore
from .run_script import run_script  # type: ignore


class ToolPluginBase(ABC):
    """Abstract base class for all toolbox plugins."""

    name: str = "unnamed"
    version: str = "0.0.0"
    description: str = ""
    default_config: Dict[str, str] = {}

    def __init__(self) -> None:
        self._script_path: Optional[Path] = None
        self._wiki_path: Optional[Path] = None

    def setup(self, toolbox: Any) -> None:
        """
        Optional initialization hook called after plugin is loaded.

        Args:
            toolbox: Reference to the PluginManager instance
        """
        pass

    @property
    def script_path(self) -> Optional[Path]:
        """Get the path to the underlying script."""
        return self._script_path

    def set_script_path(self, p: Path) -> None:
        """
        Set the path to the underlying script.

        Args:
            p: Path to the script file
        """
        self._script_path = p

    @property
    def wiki_path(self) -> Optional[Path]:
        """Get the path to the plugin's wiki documentation."""
        return self._wiki_path

    def set_wiki_path(self, p: Path) -> None:
        """
        Set the path to the plugin's wiki documentation.

        Args:
            p: Path to the wiki markdown file
        """
        self._wiki_path = p

    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata instance
        """
        return PluginMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            default_config=self.default_config,
            script_path=self._script_path,
        )

    def run(self, args: List[str], config: Dict[str, str], toolbox: Any) -> int:
        """
        Execute the plugin (CLI mode).

        Args:
            args: Command-line arguments to pass to script
            config: Merged configuration dictionary
            toolbox: Reference to PluginManager

        Returns:
            Exit code
        """
        if not self._script_path:
            raise RuntimeError("Plugin has no script path set")
        return int(run_script(self._script_path, args))

    @abstractmethod
    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """
        Create the plugin's GUI interface.

        Args:
            parent: Parent tkinter frame
            config: Current configuration values
            on_execute: Callback to invoke when execution starts

        Returns:
            Configured frame containing the plugin UI
        """
        pass

    @abstractmethod
    def get_form_fields(self) -> List[FormFieldSpec]:
        """
        Get form field specifications for this plugin.

        Returns:
            List of form field specifications
        """
        pass

    def on_execute(
        self,
        form_data: Dict[str, Any],
        config: Dict[str, str],
        progress_callback: Callable[[str, float], None],
    ) -> int:
        """
        Execute the plugin with GUI form data.

        Args:
            form_data: Values from GUI form
            config: Configuration dictionary
            progress_callback: Callback for progress updates (message, progress_0_to_1)

        Returns:
            Exit code
        """
        # Check if plugin has embedded execute method
        if hasattr(self, 'execute') and callable(getattr(self, 'execute')):
            try:
                self.execute(form_data)  # type: ignore
                return 0
            except Exception as e:
                print(f"Error during execution: {e}")
                return 1
        
        # Fallback to script-based execution
        # Build arguments from form data
        args = self.build_args_from_form(form_data)
        
        # Execute via script
        if not self._script_path:
            raise RuntimeError("Plugin has no script path set")
        
        return int(run_script(self._script_path, args))

    def build_args_from_form(self, form_data: Dict[str, Any]) -> List[str]:
        """
        Build command-line arguments from form data.

        Args:
            form_data: Values from GUI form

        Returns:
            List of command-line arguments
        """
        # Default implementation - plugins should override for custom logic
        args: List[str] = []
        for key, value in form_data.items():
            if value is not None and value != "" and value is not False:
                args.append(f"--{key.replace('_', '-')}")
                if value is not True:  # Don't add value for boolean flags
                    args.append(str(value))
        return args
