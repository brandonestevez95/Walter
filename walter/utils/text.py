"""
Text formatting utilities for Walter
"""
from typing import Dict, Any

def format_markdown(components: Dict[str, str]) -> str:
    """
    Format components as Markdown text.
    
    Args:
        components: Dictionary of text components
        
    Returns:
        Formatted Markdown string
    """
    sections = []
    
    # Add each component as a section
    for title, content in components.items():
        section = f"### {title.title()}\n\n{content}\n"
        sections.append(section)
    
    return "\n".join(sections)

def format_html(components: Dict[str, str]) -> str:
    """
    Format components as HTML.
    
    Args:
        components: Dictionary of text components
        
    Returns:
        Formatted HTML string
    """
    sections = []
    
    # Add each component as a section
    for title, content in components.items():
        section = f"<h3>{title.title()}</h3>\n<p>{content}</p>"
        sections.append(section)
    
    return "\n".join([
        "<div class='walter-output'>",
        *sections,
        "</div>"
    ])

def format_text(components: Dict[str, str]) -> str:
    """
    Format components as plain text.
    
    Args:
        components: Dictionary of text components
        
    Returns:
        Formatted text string
    """
    sections = []
    
    # Add each component as a section
    for title, content in components.items():
        section = f"{title.upper()}\n{'=' * len(title)}\n{content}\n"
        sections.append(section)
    
    return "\n".join(sections)

def format_output(components: Dict[str, str], format: str = "markdown") -> str:
    """
    Format output in the specified format.
    
    Args:
        components: Dictionary of text components
        format: Output format (markdown/html/text)
        
    Returns:
        Formatted string in the requested format
    """
    formatters = {
        "markdown": format_markdown,
        "html": format_html,
        "text": format_text,
    }
    
    formatter = formatters.get(format.lower(), format_text)
    return formatter(components) 