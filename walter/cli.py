"""
Walter - Your AI GIS Assistant
Command-line interface for geospatial workflow automation
"""
import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from .commands import describe

# Initialize Typer app
app = typer.Typer(
    name="walter",
    help="Walter - Your AI GIS Assistant for geospatial workflows",
    add_completion=False,
)

console = Console()

def version_callback(value: bool):
    """Print version information."""
    if value:
        print("[bold blue]Walter[/bold blue] version 0.1.0")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show Walter's version information."
    ),
):
    """
    Walter - Your AI GIS Assistant 🌍
    
    Automate geospatial workflows with natural language processing.
    """
    pass

@app.command()
def describe_data(
    input_file: Path = typer.Argument(..., help="Path to the input GIS file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path for the description"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format (markdown/html/text)"),
):
    """Generate professional descriptions for maps and datasets."""
    try:
        result = describe.generate_description(input_file, format)
        if output:
            output.write_text(result)
            console.print(f"✨ Description saved to: {output}")
        else:
            console.print(Panel(result, title="📝 Generated Description"))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    app() 