"""
Dynamic GUI form builder for generating tkinter widgets from field specifications.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any, Dict, Optional

from .models import FormFieldSpec


class FormBuilder:
    """Builds dynamic forms from field specifications."""

    def __init__(self, parent: tk.Frame) -> None:
        """
        Initialize form builder.

        Args:
            parent: Parent frame for the form
        """
        self.parent = parent
        self.widgets: Dict[str, tk.Widget] = {}
        self.field_specs: Dict[str, FormFieldSpec] = {}
        self._row = 0

    def add_field(self, spec: FormFieldSpec) -> tk.Widget:
        """
        Add a form field based on specification.

        Args:
            spec: Field specification

        Returns:
            Created widget
        """
        self.field_specs[spec.name] = spec

        # Create label
        label_text = spec.label
        if spec.required:
            label_text += " *"

        label = ttk.Label(self.parent, text=label_text)
        label.grid(row=self._row, column=0, sticky="w", padx=5, pady=5)

        # Create appropriate widget based on field type
        widget: tk.Widget

        if spec.field_type == "entry":
            widget = self._create_entry(spec)
        elif spec.field_type == "spinbox":
            widget = self._create_spinbox(spec)
        elif spec.field_type == "checkbox":
            widget = self._create_checkbox(spec)
        elif spec.field_type == "combobox":
            widget = self._create_combobox(spec)
        elif spec.field_type == "file":
            widget = self._create_file_picker(spec)
        elif spec.field_type == "directory":
            widget = self._create_directory_picker(spec)
        elif spec.field_type == "text":
            widget = self._create_text(spec)
        else:
            raise ValueError(f"Unknown field type: {spec.field_type}")

        widget.grid(row=self._row, column=1, sticky="ew", padx=5, pady=5)

        # Add help text if provided
        if spec.help_text:
            help_label = ttk.Label(
                self.parent, text=spec.help_text, font=("TkDefaultFont", 8), foreground="gray"
            )
            help_label.grid(row=self._row, column=2, sticky="w", padx=5)

        self.widgets[spec.name] = widget
        self._row += 1

        return widget

    def _create_entry(self, spec: FormFieldSpec) -> ttk.Entry:
        """Create text entry widget."""
        var = tk.StringVar(value=str(spec.default) if spec.default else "")
        entry = ttk.Entry(self.parent, textvariable=var, width=40)
        return entry

    def _create_spinbox(self, spec: FormFieldSpec) -> ttk.Spinbox:
        """Create spinbox widget for numeric input."""
        var = tk.StringVar(value=str(spec.default) if spec.default else "0")
        spinbox = ttk.Spinbox(self.parent, from_=0, to=10000, textvariable=var, width=20)
        return spinbox

    def _create_checkbox(self, spec: FormFieldSpec) -> ttk.Checkbutton:
        """Create checkbox widget."""
        var = tk.BooleanVar(value=bool(spec.default) if spec.default else False)
        checkbox = ttk.Checkbutton(self.parent, variable=var)
        return checkbox

    def _create_combobox(self, spec: FormFieldSpec) -> ttk.Combobox:
        """Create combobox widget with choices."""
        var = tk.StringVar(value=str(spec.default) if spec.default else "")
        combobox = ttk.Combobox(
            self.parent,
            textvariable=var,
            values=spec.choices or [],
            state="readonly",
            width=37,
        )
        if spec.default:
            combobox.set(str(spec.default))
        return combobox

    def _create_file_picker(self, spec: FormFieldSpec) -> tk.Frame:
        """Create file picker with entry and browse button."""
        frame = tk.Frame(self.parent)

        var = tk.StringVar(value=str(spec.default) if spec.default else "")
        entry = ttk.Entry(frame, textvariable=var, width=30)
        entry.pack(side=tk.LEFT, padx=(0, 5))

        def browse() -> None:
            filename = filedialog.askopenfilename(
                title=f"Select {spec.label}", parent=self.parent
            )
            if filename:
                var.set(filename)

        button = ttk.Button(frame, text="Browse...", command=browse, width=10)
        button.pack(side=tk.LEFT)

        # Store the variable for later retrieval
        frame._var = var  # type: ignore

        return frame

    def _create_directory_picker(self, spec: FormFieldSpec) -> tk.Frame:
        """Create directory picker with entry and browse button."""
        frame = tk.Frame(self.parent)

        var = tk.StringVar(value=str(spec.default) if spec.default else "")
        entry = ttk.Entry(frame, textvariable=var, width=30)
        entry.pack(side=tk.LEFT, padx=(0, 5))

        def browse() -> None:
            dirname = filedialog.askdirectory(
                title=f"Select {spec.label}", parent=self.parent
            )
            if dirname:
                var.set(dirname)

        button = ttk.Button(frame, text="Browse...", command=browse, width=10)
        button.pack(side=tk.LEFT)

        # Store the variable for later retrieval
        frame._var = var  # type: ignore

        return frame

    def _create_text(self, spec: FormFieldSpec) -> tk.Text:
        """Create multi-line text widget."""
        text = tk.Text(self.parent, height=5, width=40)
        if spec.default:
            text.insert("1.0", str(spec.default))
        return text

    def get_values(self) -> Dict[str, Any]:
        """
        Extract values from all form fields.

        Returns:
            Dictionary mapping field names to their values
        """
        values: Dict[str, Any] = {}

        for name, widget in self.widgets.items():
            spec = self.field_specs[name]

            if spec.field_type == "entry":
                entry = widget
                assert isinstance(entry, ttk.Entry)
                values[name] = entry.get()

            elif spec.field_type == "spinbox":
                spinbox = widget
                assert isinstance(spinbox, ttk.Spinbox)
                values[name] = int(spinbox.get())

            elif spec.field_type == "checkbox":
                checkbox = widget
                assert isinstance(checkbox, ttk.Checkbutton)
                var = checkbox.cget("variable")  # type: ignore
                values[name] = bool(checkbox.getvar(var))  # type: ignore

            elif spec.field_type == "combobox":
                combobox = widget
                assert isinstance(combobox, ttk.Combobox)
                values[name] = combobox.get()

            elif spec.field_type in ("file", "directory"):
                frame = widget
                assert isinstance(frame, tk.Frame)
                var = getattr(frame, "_var", None)
                if var:
                    values[name] = var.get()

            elif spec.field_type == "text":
                text = widget
                assert isinstance(text, tk.Text)
                values[name] = text.get("1.0", tk.END).strip()

        return values

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate all form fields.

        Returns:
            Tuple of (is_valid, error_message)
        """
        values = self.get_values()

        for name, spec in self.field_specs.items():
            value = values.get(name)

            # Check required fields
            if spec.required and not value:
                return False, f"{spec.label} is required"

            # Run custom validation if provided
            if spec.validation and value:
                try:
                    if not spec.validation(value):
                        return False, f"{spec.label} validation failed"
                except Exception as e:
                    return False, f"{spec.label} validation error: {e}"

        return True, None

    def set_value(self, name: str, value: Any) -> None:
        """
        Set the value of a specific field.

        Args:
            name: Field name
            value: Value to set
        """
        if name not in self.widgets:
            return

        widget = self.widgets[name]
        spec = self.field_specs[name]

        if spec.field_type == "entry":
            entry = widget
            assert isinstance(entry, ttk.Entry)
            var = entry.cget("textvariable")  # type: ignore
            entry.setvar(var, str(value))  # type: ignore

        elif spec.field_type == "spinbox":
            spinbox = widget
            assert isinstance(spinbox, ttk.Spinbox)
            var = spinbox.cget("textvariable")  # type: ignore
            spinbox.setvar(var, str(value))  # type: ignore

        elif spec.field_type == "checkbox":
            checkbox = widget
            assert isinstance(checkbox, ttk.Checkbutton)
            var = checkbox.cget("variable")  # type: ignore
            checkbox.setvar(var, bool(value))  # type: ignore

        elif spec.field_type == "combobox":
            combobox = widget
            assert isinstance(combobox, ttk.Combobox)
            combobox.set(str(value))

        elif spec.field_type in ("file", "directory"):
            frame = widget
            assert isinstance(frame, tk.Frame)
            var = getattr(frame, "_var", None)
            if var:
                var.set(str(value))

        elif spec.field_type == "text":
            text = widget
            assert isinstance(text, tk.Text)
            text.delete("1.0", tk.END)
            text.insert("1.0", str(value))

    def clear(self) -> None:
        """Clear all form fields to their defaults."""
        for name, spec in self.field_specs.items():
            self.set_value(name, spec.default if spec.default else "")
