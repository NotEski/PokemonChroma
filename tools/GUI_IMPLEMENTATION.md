# Toolbox GUI Implementation Summary

## Overview

The toolbox has been converted from a CLI-only application to a tkinter-based GUI application with full plugin support. The GUI is now the default interface, with CLI mode available via the `--cli` flag.

## Architecture Changes

### Core Components

1. **Pydantic Models** (`shared/models.py`)
   - `PluginConfig`: Configuration for plugin instances
   - `PluginMetadata`: Plugin metadata and properties
   - `ToolboxConfig`: Main toolbox configuration
   - `FormFieldSpec`: GUI form field specifications
   - `ProgressUpdate`: Progress tracking messages
   - `TaskResult`: Task execution results

2. **Dynamic Form Builder** (`shared/gui_builder.py`)
   - `FormBuilder`: Generates tkinter widgets from specifications
   - Supports: entry, spinbox, checkbox, combobox, file/directory pickers, text areas
   - Automatic validation and value extraction
   - Pre-population from configuration

3. **Enhanced Plugin Base** (`shared/plugin_base.py`)
   - Now uses ABC (Abstract Base Class)
   - Added abstract methods:
     - `create_ui()`: Generate plugin's GUI interface
     - `get_form_fields()`: Return form field specifications
   - Added `build_args_from_form()`: Convert form data to CLI arguments
   - Full type hints following PyRight standards

4. **Async Script Runner** (`shared/run_script.py`)
   - `AsyncScriptRunner`: Thread-safe script execution
   - Captures stdout/stderr
   - Progress tracking support
   - Cancellation support
   - Non-blocking GUI operation

5. **Main GUI Application** (`toolbox_gui.py`)
   - `ToolboxApp`: Main window with notebook tabs
   - `PluginTab`: Individual plugin tab with form and execution
   - `LogWindow`: Scrollable output log with colored messages
   - Auto-refresh plugins
   - Configuration dialog support

## Updated Plugins

All plugins now implement the full GUI interface:

1. **asset_downloader** - Download Pokemon sprites and cries
   - Mode selection: Range, Names, or All
   - ID range picker
   - Pokemon name list
   - Output directory selection

2. **pokeapi_downloader** - Download PokeAPI data
   - Mode: Common Endpoints, All, or Custom
   - Custom endpoint list
   - Worker count configuration

3. **pokemon_data** - Generate game data files
   - Source directory
   - Output directories for pokemon/moves/items
   - Overwrite option

4. **type_chart** - Generate type effectiveness chart
   - Output file selection

## New Plugins

Created plugins for previously standalone tools:

5. **json_converter** - Convert JSON to PKMN format
   - Input directory/file selection
   - Output directory

6. **consolidate_files** - Consolidate Pokemon files
   - Source directory
   - Output directory

7. **move_converter** - Convert moves to metadata format
   - Moves directory selection

## Usage

### GUI Mode (Default)

```bash
# Launch GUI (default)
python tools/toolbox.py

# Or explicitly
cd tools
python toolbox.py
```

The GUI features:
- Plugin tabs in notebook interface
- Dynamic forms for each plugin
- Real-time output log
- Color-coded messages (info/success/error/warning)
- Refresh plugins button
- Status bar

### CLI Mode (Legacy)

```bash
# Use CLI mode
python tools/toolbox.py --cli list
python tools/toolbox.py --cli run asset_downloader -- --range 1 151
python tools/toolbox.py --cli interactive
```

## Configuration

Plugins can still be configured via `toolbox.ini`:

```ini
[toolbox]
plugins_dir = plugins
shared_dir = shared

[plugin:asset_downloader]
output_dir = assets
concurrency = 4

[plugin:pokeapi_downloader]
database_dir = pokeapi_database

[plugin:pokemon_data]
source = pokeapi_database
out_pokemon = data/pokemon
out_moves = data/moves
out_items = data/items
```

Configuration values are automatically loaded into GUI forms as defaults.

## Key Features

### Thread-Safe Execution
- Scripts run in background threads
- GUI remains responsive during long operations
- Progress updates in real-time
- Clean output capture

### Dynamic Form Generation
- Forms generated from FormFieldSpec definitions
- Automatic widget type selection
- Built-in validation
- Pre-population from config

### Extensibility
- New plugins just need to implement abstract methods
- Form fields defined declaratively
- Argument building customizable per plugin
- Hot-reload support (refresh plugins button)

### Type Safety
- Full Pydantic models for data validation
- PyRight-compliant type hints throughout
- ABC enforcement for plugin contracts

## Development

### Creating a New Plugin

1. Create `tools/plugins/my_plugin.py`
2. Implement required methods:

```python
from plugin_base import ToolPluginBase
from models import FormFieldSpec
import tkinter as tk
from typing import List, Dict, Any, Callable

class Plugin(ToolPluginBase):
    name = "my_plugin"
    version = "1.0.0"
    description = "My plugin description"
    default_config: Dict[str, str] = {}
    
    def setup(self, toolbox: Any) -> None:
        base = Path(__file__).resolve().parents[1]
        self.set_script_path(base / "my_script.py")
    
    def get_form_fields(self) -> List[FormFieldSpec]:
        return [
            FormFieldSpec(
                name="my_field",
                label="My Field",
                field_type="entry",
                default="",
                required=True
            )
        ]
    
    def create_ui(
        self, parent: tk.Frame, 
        config: Dict[str, str], 
        on_execute: Callable[[], None]
    ) -> tk.Frame:
        frame = tk.Frame(parent)
        # Create form
        self.form_builder = FormBuilder(frame)
        for field in self.get_form_fields():
            self.form_builder.add_field(field)
        # Add run button
        ttk.Button(frame, text="Run", command=on_execute).pack()
        return frame
    
    def build_args_from_form(self, form_data: Dict[str, Any]) -> List[str]:
        return ["--my-field", str(form_data["my_field"])]
```

3. Refresh plugins in GUI (File → Refresh Plugins)

### Testing

Run the GUI:
```bash
cd tools
python toolbox.py
```

Test a specific plugin:
1. Select plugin tab
2. Fill in form fields
3. Click execute button
4. Monitor output log

## Migration Notes

### For Users
- **No action required** - GUI is now default
- Old CLI commands still work with `--cli` flag
- All existing scripts work unchanged
- Configuration file format unchanged

### For Developers
- Plugin base class now requires implementing abstract methods
- Add `create_ui()` and `get_form_fields()` to existing plugins
- Use Pydantic models for type safety
- Follow PyRight type checking standards

## Benefits

1. **User Experience**
   - Visual interface easier for non-technical users
   - Interactive prompts moved to GUI
   - Real-time feedback
   - No need to remember CLI arguments

2. **Development**
   - Type-safe with Pydantic
   - ABC enforcement prevents interface violations
   - Easier to add new plugins
   - Better code organization

3. **Maintainability**
   - Centralized form building logic
   - Consistent UI across plugins
   - Configuration management simplified
   - Hot-reload during development

## Troubleshooting

### GUI won't start
- Fallback to CLI mode is automatic
- Check tkinter installation: `python -m tkinter`
- Try explicit CLI mode: `python toolbox.py --cli list`

### Plugin not showing
- Check plugin file is in `tools/plugins/`
- Ensure it implements required abstract methods
- Use "Refresh Plugins" in GUI File menu
- Check output log for error messages

### Form not working
- Verify `get_form_fields()` returns valid FormFieldSpec list
- Check `build_args_from_form()` processes form data correctly
- Store FormBuilder instance as `self.form_builder`

## Future Enhancements

Potential improvements:
- Progress bars for long operations
- Plugin dependencies and workflow automation
- Configuration editor dialog
- Help system with script documentation
- Task history and logs
- Preset configurations
- Batch execution
