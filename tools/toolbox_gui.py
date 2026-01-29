"""
Tkinter-based GUI for the toolbox plugin system.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk
from typing import Any, Dict

# Ensure shared is importable
TOOLS_DIR = Path(__file__).parent
SHARED_DIR = TOOLS_DIR / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

# Import after path setup
from shared.models import TaskResult
from shared.plugin_base import ToolPluginBase
from shared.run_script import AsyncScriptRunner
from shared.wiki_loader import WikiLoader


class LogWindow(tk.Frame):
    """Scrollable log window for displaying output."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        
        # Create scrolled text widget
        self.text = scrolledtext.ScrolledText(
            self, height=10, width=80, wrap=tk.WORD, state=tk.DISABLED
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for different message types
        self.text.tag_config("info", foreground="black")
        self.text.tag_config("success", foreground="green")
        self.text.tag_config("error", foreground="red")
        self.text.tag_config("warning", foreground="orange")

    def log(self, message: str, level: str = "info") -> None:
        """
        Add a message to the log.

        Args:
            message: Message text
            level: Message level (info, success, error, warning)
        """
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, message + "\n", level)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def clear(self) -> None:
        """Clear the log window."""
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)


class WikiViewer:
    """Display plugin wiki documentation in a separate window."""

    def __init__(self, plugin_id: str, plugin_name: str) -> None:
        self.plugin_id = plugin_id
        self.plugin_name = plugin_name
        self.wiki_doc = WikiLoader.load_wiki(plugin_id)
        
        if not self.wiki_doc:
            messagebox.showwarning(
                "No Documentation",
                f"No wiki documentation found for {plugin_name}.\n\n"
                "See tools/plugins/wiki/{plugin_id}.md or "
                "tools/plugins/PLUGIN_DEVELOPMENT.md for more information."
            )
            return
        
        # Create window
        self.window = tk.Toplevel()
        self.window.title(f"{plugin_name} - Help")
        self.window.geometry("900x700")
        
        # Create tab structure for different sections
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._create_overview_tab()
        self._create_fields_tab()
        self._create_examples_tab()
        if self.wiki_doc.troubleshooting:
            self._create_troubleshooting_tab()
        if self.wiki_doc.related_plugins:
            self._create_related_tab()
        
        # Close button
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def _create_overview_tab(self) -> None:
        """Create overview tab."""
        if not self.wiki_doc:
            return
            
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Overview")
        
        # Title
        title = ttk.Label(frame, text=self.wiki_doc.title, font=("Helvetica", 14, "bold"))
        title.pack(padx=10, pady=5)
        
        # Description
        desc = ttk.Label(frame, text=self.wiki_doc.description, wraplength=850)
        desc.pack(padx=10, pady=5)
        
        # Overview text
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_widget = scrolledtext.ScrolledText(text_frame, height=20, width=90, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, self.wiki_doc.overview)
        text_widget.config(state=tk.DISABLED)
    
    def _create_fields_tab(self) -> None:
        """Create form fields reference tab."""
        if not self.wiki_doc:
            return
            
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Form Fields")
        
        # Create table
        tree = ttk.Treeview(
            frame,
            columns=("Type", "Required", "Description"),
            height=20,
            show="headings"
        )
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Define columns
        tree.column("#0", width=150, anchor=tk.W)
        tree.column("Type", width=100)
        tree.column("Required", width=80)
        tree.column("Description", width=400)
        
        tree.heading("#0", text="Field Name")
        tree.heading("Type", text="Type")
        tree.heading("Required", text="Required")
        tree.heading("Description", text="Description")
        
        # Add rows
        for field in self.wiki_doc.form_fields:
            tree.insert(
                "",
                "end",
                text=field.name,
                values=(
                    field.field_type,
                    "Yes" if field.required else "No",
                    field.description
                )
            )
    
    def _create_examples_tab(self) -> None:
        """Create usage examples tab."""
        if not self.wiki_doc:
            return
            
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Examples")
        
        # Create scrolled text
        text_widget = scrolledtext.ScrolledText(frame, height=30, width=100, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.config(state=tk.NORMAL)
        for example in self.wiki_doc.usage_examples:
            text_widget.insert(tk.END, f"\n{'=' * 80}\n")
            text_widget.insert(tk.END, f"{example.title}\n", "bold")
            text_widget.insert(tk.END, f"{'=' * 80}\n")
            text_widget.insert(tk.END, f"{example.content}\n\n")
        text_widget.config(state=tk.DISABLED)
        
        # Configure tags
        text_widget.tag_configure("bold", font=("Helvetica", 10, "bold"))
    
    def _create_troubleshooting_tab(self) -> None:
        """Create troubleshooting tab."""
        if not self.wiki_doc or not self.wiki_doc.troubleshooting:
            return
            
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Troubleshooting")
        
        text_widget = scrolledtext.ScrolledText(frame, height=30, width=100, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, self.wiki_doc.troubleshooting.content)
        text_widget.config(state=tk.DISABLED)
    
    def _create_related_tab(self) -> None:
        """Create related plugins tab."""
        if not self.wiki_doc:
            return
            
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Related")
        
        label = ttk.Label(frame, text="Related Plugins:", font=("Helvetica", 10, "bold"))
        label.pack(padx=10, pady=10)
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        listbox = tk.Listbox(listbox_frame, height=15)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        
        for plugin_id in self.wiki_doc.related_plugins:
            title = WikiLoader.get_wiki_title(plugin_id) or plugin_id
            listbox.insert(tk.END, title)


class PluginTab(tk.Frame):
    """Tab containing a plugin's UI."""

    def __init__(
        self,
        parent: tk.Widget,
        plugin: ToolPluginBase,
        config: Dict[str, str],
        log_window: LogWindow,
    ) -> None:
        super().__init__(parent)
        
        self.plugin = plugin
        self.config = config
        self.log_window = log_window
        self.runner = AsyncScriptRunner()
        
        # Create header with title and help button
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = tk.Label(header_frame, text=plugin.name.replace("_", " ").title(), font=("Helvetica", 12, "bold"))
        title_label.pack(side=tk.LEFT)
        
        help_button = ttk.Button(header_frame, text="Help", command=self._show_help)
        help_button.pack(side=tk.RIGHT)
        
        # Create UI container
        self.ui_frame = tk.Frame(self)
        self.ui_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create plugin-specific UI
        def on_execute() -> None:
            self.execute_plugin()
        
        try:
            self.plugin_ui = plugin.create_ui(self.ui_frame, config, on_execute)
            self.plugin_ui.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            error_label = ttk.Label(
                self.ui_frame, text=f"Failed to create plugin UI: {e}", foreground="red"
            )
            error_label.pack(padx=10, pady=10)
            self.log_window.log(f"Plugin UI creation failed: {e}", "error")

    def execute_plugin(self) -> None:
        """Execute the plugin."""
        if self.runner.is_running():
            messagebox.showwarning(
                "Already Running", "A task is already running for this plugin."
            )
            return
        
        self.log_window.log(f"Starting {self.plugin.name}...", "info")
        
        # Get form data from plugin's form builder
        try:
            if hasattr(self.plugin, "form_builder"):
                form_data = self.plugin.form_builder.get_values()  # type: ignore
            else:
                form_data = {}
        except Exception as e:
            self.log_window.log(f"Failed to get form data: {e}", "error")
            messagebox.showerror("Error", f"Failed to get form data: {e}")
            return
        
        # Build arguments
        try:
            args = self.plugin.build_args_from_form(form_data)
            self.log_window.log(f"Arguments: {' '.join(args)}", "info")
        except Exception as e:
            self.log_window.log(f"Failed to build arguments: {e}", "error")
            messagebox.showerror("Error", f"Failed to build arguments: {e}")
            return
        
        # Execute asynchronously
        def on_complete(result: TaskResult) -> None:
            if result.success:
                self.log_window.log(
                    f"✓ Completed in {result.duration:.1f}s", "success"
                )
                if result.output:
                    self.log_window.log(result.output, "info")
            else:
                self.log_window.log(
                    f"✗ Failed with exit code {result.exit_code}", "error"
                )
                if result.errors:
                    self.log_window.log(result.errors, "error")
        
        if self.plugin.script_path:
            self.runner.run(self.plugin.script_path, args, on_complete)
        else:
            self.log_window.log("Plugin has no script path", "error")

    def _show_help(self) -> None:
        """Show plugin documentation in wiki viewer."""
        # Get plugin ID from plugin attributes
        plugin_id = getattr(self.plugin, 'PLUGIN_ID', None)
        if not plugin_id:
            # Try to derive from plugin name
            plugin_id = self.plugin.name.lower().replace(" ", "_")
        
        WikiViewer(plugin_id, self.plugin.name)

    def get_form_data(self) -> Dict[str, Any]:
        """Get form data from plugin UI."""
        # Deprecated - now accessed directly through plugin.form_builder
        return {}


class ToolboxApp:
    """Main toolbox GUI application."""

    def __init__(self, plugin_manager: Any, config: Any) -> None:
        """
        Initialize the toolbox GUI.

        Args:
            plugin_manager: PluginManager instance
            config: ConfigLayer instance
        """
        self.plugin_manager = plugin_manager
        self.config = config
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Pokemon Fan Game Toolbox")
        self.root.geometry("1000x700")
        
        # Create menu bar
        self.create_menu()
        
        # Create main layout
        self.create_layout()
        
        # Load plugins
        self.load_plugins()

    def create_menu(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Plugins", command=self.refresh_plugins)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_layout(self) -> None:
        """Create main application layout."""
        # Create notebook for plugin tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create log window at bottom
        log_frame = ttk.LabelFrame(self.root, text="Output Log")
        log_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.log_window = LogWindow(log_frame)
        self.log_window.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_plugins(self) -> None:
        """Load all plugins and create tabs."""
        self.log_window.log("Loading plugins...", "info")
        
        # Clear existing tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # Load plugins
        plugin_count = 0
        for plugin_name, plugin in self.plugin_manager._plugins.items():
            try:
                # Get plugin config
                plugin_config = dict(self.config.plugin_items(plugin_name))
                
                # Create tab
                tab = PluginTab(self.notebook, plugin, plugin_config, self.log_window)
                self.notebook.add(tab, text=plugin.name.replace("_", " ").title())
                
                plugin_count += 1
                self.log_window.log(f"Loaded: {plugin.name} v{plugin.version}", "success")
            except Exception as e:
                self.log_window.log(f"Failed to load {plugin_name}: {e}", "error")
        
        self.log_window.log(f"\nLoaded {plugin_count} plugins", "success")
        self.status_var.set(f"Loaded {plugin_count} plugins")

    def refresh_plugins(self) -> None:
        """Refresh all plugins."""
        self.log_window.clear()
        self.log_window.log("Refreshing plugins...", "info")
        
        try:
            self.plugin_manager.refresh()
            self.load_plugins()
        except Exception as e:
            self.log_window.log(f"Failed to refresh plugins: {e}", "error")
            messagebox.showerror("Error", f"Failed to refresh plugins: {e}")

    def show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About Toolbox",
            "Pokemon Fan Game Toolbox\n\n"
            "A plugin-based toolbox for managing\n"
            "Pokemon data and assets.\n\n"
            "Version 1.0.0",
        )

    def run(self) -> None:
        """Start the GUI main loop."""
        self.root.mainloop()


def main() -> None:
    """Main entry point for GUI mode."""
    # Import here to avoid circular dependencies
    from toolbox import ConfigLayer, PluginManager  # type: ignore
    
    TOOLS_DIR = Path(__file__).parent
    INI_PATH = TOOLS_DIR / "toolbox.ini"
    
    # Load configuration
    config = ConfigLayer(INI_PATH)
    
    # Create plugin manager
    plugin_manager = PluginManager()
    plugin_manager.load_all()
    
    # Create and run GUI
    app = ToolboxApp(plugin_manager, config)
    app.run()


if __name__ == "__main__":
    main()
