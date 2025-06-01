"""
GitBook integration for Walter
"""
import os
from pathlib import Path
import requests
from typing import Dict, List, Optional
import yaml
from jinja2 import Environment, FileSystemLoader

class GitBookAPI:
    """GitBook API client for Walter."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize GitBook client."""
        self.api_token = api_token or os.getenv("GITBOOK_TOKEN")
        if not self.api_token:
            raise ValueError("GitBook API token not found. Set GITBOOK_TOKEN environment variable.")
        
        self.base_url = "https://api.gitbook.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def create_page(self, space_id: str, title: str, content: str) -> Dict:
        """Create a new page in GitBook space."""
        url = f"{self.base_url}/spaces/{space_id}/content"
        data = {
            "title": title,
            "content": content,
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def update_page(self, space_id: str, page_id: str, content: str) -> Dict:
        """Update an existing GitBook page."""
        url = f"{self.base_url}/spaces/{space_id}/content/{page_id}"
        data = {"content": content}
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

class GitBookPublisher:
    """Publisher for GitBook content."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize GitBook publisher."""
        self.config_path = config_path or Path.home() / ".walter" / "gitbook.yml"
        self.api = GitBookAPI()
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def load_config(self) -> Dict:
        """Load GitBook configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"GitBook config not found at {self.config_path}")
        
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def create_summary(self, pages: List[Dict]) -> str:
        """Generate SUMMARY.md content."""
        template = self.env.get_template("gitbook_summary.md.j2")
        return template.render(pages=pages)

    def publish_content(
        self,
        content: str,
        title: str,
        space_id: Optional[str] = None,
        page_id: Optional[str] = None,
    ) -> Dict:
        """Publish content to GitBook."""
        config = self.load_config()
        space_id = space_id or config.get("default_space")
        
        if not space_id:
            raise ValueError("GitBook space ID not provided")
        
        if page_id:
            return self.api.update_page(space_id, page_id, content)
        else:
            return self.api.create_page(space_id, title, content)

    def sync_directory(self, source_dir: Path, space_id: Optional[str] = None) -> List[Dict]:
        """Sync a directory of markdown files to GitBook."""
        config = self.load_config()
        space_id = space_id or config.get("default_space")
        
        if not space_id:
            raise ValueError("GitBook space ID not provided")
        
        published_pages = []
        
        # Process all markdown files
        for md_file in source_dir.glob("**/*.md"):
            if md_file.name == "SUMMARY.md":
                continue
                
            with open(md_file) as f:
                content = f.read()
            
            # Use filename as title if not specified in frontmatter
            title = md_file.stem.replace("-", " ").title()
            
            result = self.publish_content(content, title, space_id)
            published_pages.append({
                "title": title,
                "path": str(md_file.relative_to(source_dir)),
                "id": result["id"],
            })
        
        # Generate and update SUMMARY.md
        summary = self.create_summary(published_pages)
        summary_path = source_dir / "SUMMARY.md"
        summary_path.write_text(summary)
        
        return published_pages 