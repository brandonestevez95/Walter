"""
Test workflow demonstrating Walter's capabilities
"""
import os
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from dotenv import load_dotenv

from walter.integrations.gitbook import GitBookPublisher
from walter.commands.describe import generate_description

# Load environment variables
load_dotenv()

def create_sample_data():
    """Create a sample GeoDataFrame for testing."""
    # Create sample points
    points = [
        Point(-122.4194, 37.7749),  # San Francisco
        Point(-118.2437, 34.0522),  # Los Angeles
        Point(-74.0060, 40.7128),   # New York
    ]
    
    # Create sample data
    data = {
        'name': ['San Francisco', 'Los Angeles', 'New York'],
        'population': [874961, 3898747, 8804190],
        'state': ['CA', 'CA', 'NY'],
    }
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(data, geometry=points, crs="EPSG:4326")
    
    # Save to file
    output_path = Path("tests/data/cities.geojson")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GeoJSON")
    
    return output_path

def main():
    """Run the test workflow."""
    print("🌍 Starting Walter test workflow...")
    
    # Create sample data
    print("\n1. Creating sample data...")
    data_path = create_sample_data()
    print(f"✓ Created sample data at: {data_path}")
    
    # Generate description
    print("\n2. Generating dataset description...")
    description = generate_description(data_path)
    print("✓ Generated description:")
    print(description)
    
    # Publish to GitBook
    if os.getenv("GITBOOK_TOKEN"):
        print("\n3. Publishing to GitBook...")
        publisher = GitBookPublisher()
        
        # Create content directory
        content_dir = Path("tests/data/gitbook")
        content_dir.mkdir(exist_ok=True)
        
        # Create markdown file
        md_path = content_dir / "cities.md"
        with open(md_path, "w") as f:
            f.write(f"# US Major Cities\n\n{description}")
        
        # Publish to GitBook
        result = publisher.sync_directory(content_dir)
        print("✓ Published to GitBook:")
        for page in result:
            print(f"  - {page['title']}: {page['path']}")
    else:
        print("\n⚠️ Skipping GitBook publish (token not found)")
    
    print("\n✨ Workflow completed!")

if __name__ == "__main__":
    main() 