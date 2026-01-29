"""
Pydantic models for toolbox configuration and plugin metadata.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PluginConfig(BaseModel):
    """Configuration for a plugin instance."""

    name: str = Field(..., description="Unique plugin identifier")
    values: Dict[str, str] = Field(
        default_factory=dict, description="Configuration key-value pairs"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure plugin name is non-empty and valid."""
        if not v or not v.strip():
            raise ValueError("Plugin name cannot be empty")
        return v.strip()


class PluginMetadata(BaseModel):
    """Metadata describing a plugin's properties."""

    name: str = Field(..., description="Plugin identifier")
    version: str = Field(default="0.0.0", description="Plugin version")
    description: str = Field(default="", description="Plugin description")
    default_config: Dict[str, str] = Field(
        default_factory=dict, description="Default configuration values"
    )
    script_path: Optional[Path] = Field(
        default=None, description="Path to underlying script"
    )

    class Config:
        arbitrary_types_allowed = True


class ToolboxConfig(BaseModel):
    """Main toolbox configuration."""

    plugins_dir: Path = Field(
        default=Path("plugins"), description="Directory containing plugins"
    )
    shared_dir: Path = Field(
        default=Path("shared"), description="Directory for shared utilities"
    )
    plugin_configs: Dict[str, PluginConfig] = Field(
        default_factory=dict, description="Per-plugin configurations"
    )

    class Config:
        arbitrary_types_allowed = True


class FormFieldSpec(BaseModel):
    """Specification for a GUI form field."""

    name: str = Field(..., description="Field identifier")
    label: str = Field(..., description="Display label")
    field_type: str = Field(
        ...,
        description="Widget type: entry, spinbox, checkbox, combobox, file, directory",
    )
    default: Any = Field(default=None, description="Default value")
    required: bool = Field(default=False, description="Whether field is required")
    choices: Optional[List[str]] = Field(
        default=None, description="Choices for combobox"
    )
    help_text: Optional[str] = Field(default=None, description="Help/tooltip text")
    validation: Optional[Callable[[Any], bool]] = Field(
        default=None, description="Validation function"
    )

    class Config:
        arbitrary_types_allowed = True


class ProgressUpdate(BaseModel):
    """Progress update message from background task."""

    status: str = Field(..., description="Status message")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress 0-1")
    current: int = Field(default=0, description="Current item number")
    total: int = Field(default=0, description="Total items")
    details: Optional[str] = Field(default=None, description="Additional details")


class TaskResult(BaseModel):
    """Result from completed background task."""

    success: bool = Field(..., description="Whether task succeeded")
    exit_code: int = Field(default=0, description="Process exit code")
    output: str = Field(default="", description="Captured stdout")
    errors: str = Field(default="", description="Captured stderr")
    duration: float = Field(default=0.0, description="Execution time in seconds")
