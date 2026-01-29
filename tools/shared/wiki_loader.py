"""
Wiki Loader - Parse and load plugin documentation from markdown files.

This module provides functionality to read plugin wiki markdown files and convert
them into structured data that can be used by the GUI, CLI, and AI agents.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


@dataclass
class WikiSection:
    """Represents a section of a wiki document."""
    title: str
    content: str
    subsections: List['WikiSection'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "content": self.content,
            "subsections": [s.to_dict() for s in self.subsections]
        }


@dataclass
class FormFieldInfo:
    """Represents a form field from wiki documentation."""
    name: str
    field_type: str
    required: bool
    description: str


@dataclass
class WikiDocument:
    """Represents a complete wiki document."""
    plugin_id: str
    title: str
    description: str
    overview: str
    form_fields: List[FormFieldInfo]
    usage_examples: List[WikiSection]
    advanced_options: Optional[WikiSection] = None
    troubleshooting: Optional[WikiSection] = None
    related_plugins: List[str] = field(default_factory=list)
    version_history: List[str] = field(default_factory=list)
    technical_details: Optional[WikiSection] = None
    raw_content: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "plugin_id": self.plugin_id,
            "title": self.title,
            "description": self.description,
            "overview": self.overview,
            "form_fields": [asdict(f) for f in self.form_fields],
            "usage_examples": [s.to_dict() for s in self.usage_examples],
            "advanced_options": self.advanced_options.to_dict() if self.advanced_options else None,
            "troubleshooting": self.troubleshooting.to_dict() if self.troubleshooting else None,
            "related_plugins": self.related_plugins,
            "version_history": self.version_history,
            "technical_details": self.technical_details.to_dict() if self.technical_details else None,
        }


class WikiLoader:
    """Load and parse plugin wiki markdown files."""
    
    WIKI_DIR = Path(__file__).parent.parent / "plugins" / "wiki"
    
    @classmethod
    def get_wiki_dir(cls) -> Path:
        """Get the wiki directory path."""
        return cls.WIKI_DIR
    
    @classmethod
    def load_wiki(cls, plugin_id: str) -> Optional[WikiDocument]:
        """
        Load a wiki document for a specific plugin.
        
        Args:
            plugin_id: The plugin ID (e.g., "asset_downloader")
            
        Returns:
            WikiDocument if found, None otherwise
        """
        wiki_file = cls.WIKI_DIR / f"{plugin_id}.md"
        if not wiki_file.exists():
            return None
        
        content = wiki_file.read_text(encoding="utf-8")
        return cls.parse_wiki_markdown(plugin_id, content)
    
    @classmethod
    def parse_wiki_markdown(cls, plugin_id: str, content: str) -> WikiDocument:
        """
        Parse a wiki markdown file into a structured document.
        
        Args:
            plugin_id: The plugin ID
            content: Raw markdown content
            
        Returns:
            WikiDocument with parsed content
        """
        lines = content.split("\n")
        
        # Extract main title (first H1)
        title = ""
        description = ""
        for i, line in enumerate(lines):
            if line.startswith("# ") and not title:
                title = line[2:].strip()
                # Next non-empty line is usually the brief description
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        description = lines[j].strip()
                        break
                break
        
        # Parse sections
        sections = cls._parse_sections(lines)
        
        # Extract specific sections
        overview = cls._extract_section_text(sections, "Overview")
        form_fields = cls._extract_form_fields(sections)
        usage_examples = cls._extract_examples(sections)
        advanced_options = cls._extract_section(sections, "Advanced Options")
        troubleshooting = cls._extract_section(sections, "Troubleshooting")
        related_plugins = cls._extract_related_plugins(sections)
        version_history = cls._extract_version_history(sections)
        technical_details = cls._extract_section(sections, "Technical Details")
        
        return WikiDocument(
            plugin_id=plugin_id,
            title=title,
            description=description,
            overview=overview,
            form_fields=form_fields,
            usage_examples=usage_examples,
            advanced_options=advanced_options,
            troubleshooting=troubleshooting,
            related_plugins=related_plugins,
            version_history=version_history,
            technical_details=technical_details,
            raw_content=content
        )
    
    @staticmethod
    def _parse_sections(lines: List[str]) -> Dict[str, List[str]]:
        """Parse markdown into sections by H2 headers."""
        sections = {}
        current_section = "Introduction"
        sections[current_section] = []
        
        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].strip()
                sections[current_section] = []
            elif line.startswith("# "):
                # Skip main title
                continue
            else:
                sections[current_section].append(line)
        
        return sections
    
    @staticmethod
    def _extract_section_text(sections: Dict[str, List[str]], section_name: str) -> str:
        """Extract text content from a section."""
        if section_name not in sections:
            return ""
        
        lines = sections[section_name]
        # Skip empty lines at start
        start = 0
        for i, line in enumerate(lines):
            if line.strip():
                start = i
                break
        
        # Find end (before any code blocks or special markers)
        text_lines = []
        for line in lines[start:]:
            if line.startswith("```") or line.startswith("|"):
                break
            if line.strip():
                text_lines.append(line)
        
        return "\n".join(text_lines).strip()
    
    @staticmethod
    def _extract_form_fields(sections: Dict[str, List[str]]) -> List[FormFieldInfo]:
        """Extract form field information from Form Fields section."""
        form_fields = []
        
        if "Form Fields" not in sections:
            return form_fields
        
        lines = sections["Form Fields"]
        in_table = False
        
        for line in lines:
            # Look for table rows
            if line.startswith("|") and not in_table:
                in_table = True
                continue
            
            if in_table and line.startswith("|"):
                # Parse table row
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4 and not parts[0].startswith("-"):
                    try:
                        form_fields.append(FormFieldInfo(
                            name=parts[0],
                            field_type=parts[1],
                            required=parts[2].lower() == "yes",
                            description=parts[3]
                        ))
                    except (IndexError, ValueError):
                        pass
            elif in_table and not line.strip():
                in_table = False
        
        return form_fields
    
    @staticmethod
    def _extract_examples(sections: Dict[str, List[str]]) -> List[WikiSection]:
        """Extract usage examples as structured sections."""
        examples = []
        
        if "Usage Examples" not in sections:
            return examples
        
        lines = sections["Usage Examples"]
        current_example = None
        current_content = []
        
        for line in lines:
            if line.startswith("### Example"):
                if current_example:
                    examples.append(WikiSection(
                        title=current_example,
                        content="\n".join(current_content).strip()
                    ))
                current_example = line[4:].strip()
                current_content = []
            elif current_example:
                current_content.append(line)
        
        if current_example:
            examples.append(WikiSection(
                title=current_example,
                content="\n".join(current_content).strip()
            ))
        
        return examples
    
    @staticmethod
    def _extract_section(sections: Dict[str, List[str]], section_name: str) -> Optional[WikiSection]:
        """Extract a section as a WikiSection."""
        if section_name not in sections:
            return None
        
        content = "\n".join(sections[section_name]).strip()
        if not content:
            return None
        
        return WikiSection(title=section_name, content=content)
    
    @staticmethod
    def _extract_related_plugins(sections: Dict[str, List[str]]) -> List[str]:
        """Extract related plugin links."""
        related = []
        
        if "Related Plugins" not in sections:
            return related
        
        lines = sections["Related Plugins"]
        for line in lines:
            # Look for markdown links [Name](id.md)
            match = re.search(r'\[([^\]]+)\]\(([^)]+\.md)\)', line)
            if match:
                plugin_id = match.group(2).replace(".md", "")
                related.append(plugin_id)
        
        return related
    
    @staticmethod
    def _extract_version_history(sections: Dict[str, List[str]]) -> List[str]:
        """Extract version history."""
        history = []
        
        if "Version History" not in sections:
            return history
        
        lines = sections["Version History"]
        for line in lines:
            if line.strip().startswith("- **"):
                history.append(line.strip()[2:])  # Remove "- "
        
        return history
    
    @classmethod
    def list_all_wikis(cls) -> List[str]:
        """
        List all available wiki plugin IDs.
        
        Returns:
            List of plugin IDs that have wiki files
        """
        if not cls.WIKI_DIR.exists():
            return []
        
        wiki_files = cls.WIKI_DIR.glob("*.md")
        return [f.stem for f in wiki_files]
    
    @classmethod
    def get_wiki_title(cls, plugin_id: str) -> Optional[str]:
        """
        Get just the title of a wiki without full parsing.
        
        Args:
            plugin_id: The plugin ID
            
        Returns:
            Wiki title or None if not found
        """
        wiki_file = cls.WIKI_DIR / f"{plugin_id}.md"
        if not wiki_file.exists():
            return None
        
        with open(wiki_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("# "):
                    return line[2:].strip()
        
        return None
    
    @classmethod
    def get_wiki_description(cls, plugin_id: str) -> Optional[str]:
        """
        Get the brief description (second line after title) of a wiki.
        
        Args:
            plugin_id: The plugin ID
            
        Returns:
            Brief description or None if not found
        """
        wiki_file = cls.WIKI_DIR / f"{plugin_id}.md"
        if not wiki_file.exists():
            return None
        
        with open(wiki_file, 'r', encoding='utf-8') as f:
            found_title = False
            for line in f:
                if line.startswith("# "):
                    found_title = True
                elif found_title and line.strip() and not line.startswith("#"):
                    return line.strip()
                    
        return None


# Convenience functions for easy access
def load_wiki(plugin_id: str) -> Optional[WikiDocument]:
    """Load a plugin wiki by ID."""
    return WikiLoader.load_wiki(plugin_id)


def list_wikis() -> List[str]:
    """List all available plugin wikis."""
    return WikiLoader.list_all_wikis()


def get_wiki_title(plugin_id: str) -> Optional[str]:
    """Get wiki title by plugin ID."""
    return WikiLoader.get_wiki_title(plugin_id)
