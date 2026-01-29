# Plugin Development Guide

This guide explains how to create new plugins for the Pokemon Fan Game Toolbox. All plugins follow a standardized architecture that ensures consistency and maintainability.

## Plugin Architecture Overview

Every plugin is a Python class that extends `ToolPluginBase` and provides:
- **Class Attributes**: Plugin metadata (name, version, description, config)
- **Form Fields**: GUI form specifications via `get_form_fields()`
- **UI Creation**: Tkinter GUI via `create_ui()` method
- **Execution**: Business logic in the `execute()` method
- **Documentation**: A paired `.md` wiki file in `tools/plugins/wiki/`

## Creating a New Plugin: Step-by-Step

### Step 1: Choose Plugin Pattern

**Embedded Plugin** (Recommended):
- Business logic directly in the plugin file
- Dedicated class for the core functionality
- Plugin class wraps the core class for GUI/CLI integration
- Fast, maintainable, and self-contained

Example structure:
```python
class MyFunctionality:
    """Core business logic"""
    def process(self, data):
        ...

class Plugin(ToolPluginBase):
    """GUI/CLI wrapper"""
    def execute(self, form_data):
        func = MyFunctionality(...)
        func.process(...)
```

### Step 2: Create the Plugin File

Create a new file in `tools/plugins/` following the naming convention: `{snake_case_name}.py`

### Step 3: Implement the Core Business Logic

Create your main class with the business logic:

```python
class MyAnalyzer:
    """Analyzes Pokemon data and generates reports."""
    
    def __init__(self, input_dir: Union[str, Path]):
        self.input_dir = Path(input_dir)
    
    def analyze(self) -> Dict[str, Any]:
        """Main analysis logic"""
        results = {}
        # Your business logic here
        return results
```

### Step 4: Implement the Plugin Wrapper Class

```python
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class Plugin(ToolPluginBase):
    """Plugin wrapper for GUI/CLI integration."""
    
    name = "my_plugin"  # Unique identifier (snake_case)
    version = "1.0.0"   # Semantic versioning
    description = "Brief description of what the plugin does"
    default_config: Dict[str, str] = {
        "input_dir": "data",
        "output_file": "output.txt",
        "verbose": "true",
    }
    
    def setup(self, toolbox: Any) -> None:
        """Optional initialization hook called after plugin is loaded."""
        pass
    
    def get_form_fields(self) -> List[FormFieldSpec]:
        """Define the input fields for this plugin."""
        return [
            FormFieldSpec(
                name="input_dir",
                label="Input Directory",
                field_type="directory",
                required=True,
                default=self.default_config["input_dir"],
                help_text="Directory containing data to analyze"
            ),
            FormFieldSpec(
                name="output_file",
                label="Output File",
                field_type="text",
                required=False,
                default=self.default_config["output_file"],
                help_text="Where to save the results"
            ),
            FormFieldSpec(
                name="verbose",
                label="Verbose Output",
                field_type="checkbox",
                default=self.default_config["verbose"] == "true",
                help_text="Enable detailed logging"
            ),
        ]
    
    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        """Create the plugin's GUI interface."""
        frame = tk.Frame(parent)
        
        # Description
        desc = ttk.Label(
            frame,
            text=self.description,
            wraplength=700,
            font=("TkDefaultFont", 10, "bold"),
        )
        desc.pack(pady=10)
        
        # Form
        form_frame = tk.Frame(frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        self.form_builder = FormBuilder(form_frame)
        
        for field_spec in self.get_form_fields():
            # Set defaults from config if available
            if field_spec.name in config:
                field_spec.default = config[field_spec.name]
            self.form_builder.add_field(field_spec)
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)
        
        run_btn = ttk.Button(
            button_frame, text="Execute", command=on_execute, width=20
        )
        run_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame, text="Clear Form", command=self.form_builder.clear, width=15
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def execute(self, form_data: Dict[str, Any]) -> None:
        """Execute the plugin with provided form data."""
        # Extract inputs
        input_dir = Path(form_data.get("input_dir", self.default_config["input_dir"]))
        output_file = form_data.get("output_file", self.default_config["output_file"])
        verbose = form_data.get("verbose", False)
        
        # Validate inputs
        if not input_dir.exists():
            raise ValueError(f"Input directory not found: {input_dir}")
        
        # Create core functionality instance
        analyzer = MyAnalyzer(input_dir)
        
        # Execute business logic
        if verbose:
            print(f"Analyzing: {input_dir}")
        
        results = analyzer.analyze()
        
        # Save results
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                import json
                json.dump(results, f, indent=2)
            print(f"Results saved to: {output_path}")
```

### Step 5: FormFieldSpec Types

Available field types:

- **text**: Single-line text input
- **textarea**: Multi-line text input
- **spinbox**: Integer input
- **combobox**: Dropdown selection (requires `choices` parameter)
- **checkbox**: Boolean true/false
- **file**: File picker
- **directory**: Directory picker

Example with choices:

```python
FormFieldSpec(
    name="mode",
    label="Analysis Mode",
    field_type="combobox",
    choices=["Summary", "Detailed", "Export"],
    default="Summary",
    required=True,
    help_text="Choose analysis mode"
)
```

### Step 6: Create Documentation Wiki

Create a file at `tools/plugins/wiki/{plugin_id}.md`:

```markdown
# {Plugin Name}

Brief description.

## Overview

Detailed explanation of purpose and use.

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| input_dir | Directory | Yes | Input directory |
| output_file | Text | No | Output file path |
| verbose | Checkbox | No | Enable verbose output |

## Usage Examples

### Example 1: Basic Analysis

Steps:
1. Select input directory
2. Leave output file empty for console output
3. Check verbose for detailed logging
4. Click Execute

Result: Analysis results displayed in console.

## Advanced Options

Configure default values in `toolbox.ini`:

```ini
[plugin:my_plugin]
input_dir = data
output_file = results.json
verbose = true
```

## Troubleshooting

### Issue: "Input directory not found"

**Solution:** Ensure the path exists and you have read permissions.

## Related Plugins

- [Other Plugin](other_plugin.md)

## Version History

- **1.0.0**: Initial release
```

### Step 7: Testing Your Plugin

Create `tests/test_my_plugin.py`:

```python
import pytest
from pathlib import Path
from tools.plugins.my_plugin import Plugin, MyAnalyzer


class TestMyPlugin:
    
    @pytest.fixture
    def plugin(self):
        return Plugin()
    
    @pytest.fixture
    def sample_data(self, tmp_path):
        """Create sample test data"""
        (tmp_path / "test.json").write_text('{"test": true}')
        return tmp_path
    
    def test_plugin_attributes(self, plugin):
        """Test plugin metadata"""
        assert plugin.name == "my_plugin"
        assert plugin.version == "1.0.0"
        assert hasattr(plugin, 'execute')
        assert hasattr(plugin, 'create_ui')
    
    def test_form_fields(self, plugin):
        """Test form field definitions"""
        fields = plugin.get_form_fields()
        assert len(fields) > 0
        field_names = [f.name for f in fields]
        assert "input_dir" in field_names
    
    def test_execute(self, plugin, sample_data):
        """Test plugin execution"""
        form_data = {
            "input_dir": str(sample_data),
            "output_file": "results.json",
            "verbose": True
        }
        plugin.execute(form_data)
    
    def test_core_functionality(self, sample_data):
        """Test core business logic"""
        analyzer = MyAnalyzer(sample_data)
        results = analyzer.analyze()
        assert isinstance(results, dict)
```

## Common Patterns

### Pattern 1: File Processing Loop

```python
class FileProcessor:
    def __init__(self, input_dir: Path):
        self.input_dir = Path(input_dir)
    
    def process_all(self) -> Dict[str, Any]:
        results = {}
        for file_path in self.input_dir.glob("*.json"):
            if file_path.name.startswith("_"):
                continue
            try:
                data = json.loads(file_path.read_text())
                results[file_path.stem] = self._process_file(data)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        return results
    
    def _process_file(self, data: Dict[str, Any]) -> Any:
        # Implementation
        return data
```

### Pattern 2: Configuration from toolbox.ini

```python
def execute(self, form_data: Dict[str, Any]) -> None:
    # Use form data first, fall back to defaults
    setting = form_data.get("setting", self.default_config.get("setting"))
```

### Pattern 3: Progress Tracking

```python
def execute(self, form_data: Dict[str, Any]) -> None:
    items = list(self.input_dir.glob("*.json"))
    for i, item in enumerate(items):
        print(f"Processing {i+1}/{len(items)}: {item.name}")
        # Process item
```

## Naming Conventions

- **Plugin File**: `tools/plugins/{plugin_id}.py` (snake_case)
- **Plugin name attribute**: `plugin_id` (snake_case)
- **Form Field Names**: `field_name` (snake_case)
- **Wiki File**: `tools/plugins/wiki/{plugin_id}.md`
- **Core Class**: `ClassName` (PascalCase)
- **Plugin Wrapper Class**: `Plugin` (always use this name)

## Quality Checklist

Before committing:

- [ ] Plugin file: `{plugin_id}.py` in `tools/plugins/`
- [ ] Class named `Plugin` extends `ToolPluginBase`
- [ ] Attributes: `name`, `version`, `description`, `default_config`
- [ ] Methods: `get_form_fields()`, `create_ui()`, `execute()`
- [ ] `get_form_fields()` returns list of `FormFieldSpec`
- [ ] `create_ui()` returns configured frame with form_builder
- [ ] `execute()` has proper error handling and validation
- [ ] Core business logic in separate class
- [ ] Wiki file created: `tools/plugins/wiki/{plugin_id}.md`
- [ ] Wiki includes: Overview, Form Fields, Examples, Troubleshooting
- [ ] Unit tests in `tests/test_{plugin_id}.py`
- [ ] Code follows PEP 8 style
- [ ] All public methods have docstrings
- [ ] **PyRight compliant** (see PyRight Compliance section below)

## PyRight Compliance

All plugins must pass PyRight type checking to ensure code quality and IDE support.

### Type Annotations

Use explicit type annotations for all parameters and return types:

```python
def analyze_data(self, data: Dict[str, Any]) -> Dict[str, int]:
    """Analyze data and return counts."""
    results: Dict[str, int] = {}
    return results

def get_items(self) -> List[str]:
    """Get items."""
    return sorted(self.items)
```

### Common Type Annotation Patterns

**Return types must be explicit:**
```python
# Good ✓
def process(self) -> Tuple[List[str], Dict[str, int]]:
    results: List[str] = []
    counts: Dict[str, int] = {}
    return results, counts

# Bad ✗
def process(self):  # Missing return type
    return results, counts
```

**Parameter types must be explicit:**
```python
# Good ✓
def update(self, name: str, value: int) -> None:
    self.data[name] = value

# Bad ✗
def update(self, name, value):  # Missing parameter types
    self.data[name] = value
```

**Collection types should be specific:**
```python
# Good ✓
from typing import Dict, List, Optional, Set, Tuple

def analyze(self) -> Tuple[List[str], Dict[str, Any]]:
    items: Set[str] = set()
    mapping: Dict[str, int] = {}
    result: Optional[str] = None
    return sorted(list(items)), mapping

# Bad ✗
def analyze(self):  # Wrong return type mixing Set/List
    items = set()  # Implicit type
    return items, {}  # Set instead of List
```

### PyRight Validation

Run PyRight before committing:

```bash
# Check single plugin
pyright tools/plugins/my_plugin.py

# Check all plugins
pyright tools/plugins/analyze_*.py tools/plugins/consolidate_*.py tools/plugins/convert_*.py

# Check entire plugins directory
pyright tools/plugins/
```

**Expected output:**
```
0 errors, 0 warnings, 0 informations
```

### Common PyRight Errors and Fixes

**Error: Type not assignable**
```python
# ❌ Wrong - Set returned as List
def get_effects(self) -> List[str]:
    return self.effects  # Set[str]

# ✅ Correct - Convert Set to List
def get_effects(self) -> List[str]:
    return sorted(list(self.effects))
```

**Error: Undefined variable**
```python
# ❌ Wrong - Variable name mismatch
def process(self) -> None:
    items = []
    print(len(item))  # Wrong variable name

# ✅ Correct - Consistent naming
def process(self) -> None:
    items: List[str] = []
    print(len(items))  # Correct variable name
```

**Error: Argument type mismatch**
```python
# ❌ Wrong - Set passed to List parameter
def analyze(self, effects: List[str]) -> None:
    pass

effects_set: Set[str] = {"fire", "water"}
self.analyze(effects_set)  # Type error

# ✅ Correct - Convert to correct type
self.analyze(sorted(list(effects_set)))
```

### Type Hints for Plugin Methods

**`get_form_fields()` should return `List[FormFieldSpec]`:**
```python
def get_form_fields(self) -> List[FormFieldSpec]:
    """Define the input fields for this plugin."""
    return [
        FormFieldSpec(...),
        FormFieldSpec(...),
    ]
```

**`create_ui()` should return `tk.Frame`:**
```python
def create_ui(
    self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
) -> tk.Frame:
    """Create the plugin's GUI."""
    frame = tk.Frame(parent)
    # ... setup widgets ...
    return frame
```

**`execute()` should return `None`:**
```python
def execute(self, form_data: Dict[str, Any]) -> None:
    """Execute the plugin with provided form data."""
    # ... execution logic ...
```

### IDE Support

With proper type annotations, you get:
- ✓ Code completion in VS Code
- ✓ Parameter hints while typing
- ✓ Type checking before runtime
- ✓ Automatic error detection
- ✓ Better code documentation

## Example: Complete Minimal Plugin

```python
"""Example minimal plugin"""
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, Callable, Dict, List

from shared.gui_builder import FormBuilder
from shared.models import FormFieldSpec
from shared.plugin_base import ToolPluginBase


class ExampleProcessor:
    """Core business logic"""
    def process(self, value: str) -> str:
        return f"Processed: {value}"


class Plugin(ToolPluginBase):
    """Example plugin wrapper"""
    
    name = "example_plugin"
    version = "1.0.0"
    description = "A minimal example plugin"
    default_config = {"input": ""}
    
    def get_form_fields(self) -> List[FormFieldSpec]:
        return [
            FormFieldSpec(
                name="input",
                label="Input",
                field_type="text",
                required=True
            )
        ]
    
    def create_ui(
        self, parent: tk.Frame, config: Dict[str, str], on_execute: Callable[[], None]
    ) -> tk.Frame:
        frame = tk.Frame(parent)
        ttk.Label(frame, text=self.description).pack(pady=10)
        
        self.form_builder = FormBuilder(tk.Frame(frame))
        self.form_builder.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for field in self.get_form_fields():
            self.form_builder.add_field(field)
        
        ttk.Button(frame, text="Process", command=on_execute).pack(pady=10)
        return frame
    
    def execute(self, form_data: Dict[str, Any]) -> None:
        value = form_data.get("input")
        if not value:
            raise ValueError("Input is required")
        
        processor = ExampleProcessor()
        result = processor.process(value)
        print(result)
```

## Plugin Discovery

Plugins are auto-discovered by the toolbox:

1. Plugin file must be in `tools/plugins/` directory
2. Plugin file must have a class named `Plugin`
3. Plugin class must extend `ToolPluginBase`
4. Plugin must implement `name`, `get_form_fields()`, `create_ui()`, `execute()`
5. Wiki file at `tools/plugins/wiki/{name}.md` will be auto-loaded for Help button

## Debugging Tips

**Plugin not showing up:**
- Check file is in `tools/plugins/` directory
- Check class is named exactly `Plugin`
- Check class extends `ToolPluginBase`
- Check `name` attribute is set

**Form not displaying:**
- Check `get_form_fields()` returns non-empty list
- Check `FormFieldSpec` objects have all required parameters
- Check `create_ui()` creates `FormBuilder` and adds fields

**Execute not working:**
- Check form data extraction uses correct field names
- Check error handling for all user inputs
- Check all required form fields are validated

---

**Last Updated:** January 2026
**Version:** 2.0 (Updated to match actual plugin implementation)
