"""
Walter describe command - Generate professional descriptions for GIS data
"""
import geopandas as gpd
from pathlib import Path
from typing import Optional, Dict, Any
import json

from ..utils.gis import get_crs_info, get_geometry_stats
from ..utils.text import format_output

def analyze_dataset(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a GIS dataset and extract key information.
    
    Args:
        file_path: Path to the GIS file
        
    Returns:
        Dictionary containing dataset analysis
    """
    # Read the dataset
    gdf = gpd.read_file(file_path)
    
    # Basic information
    info = {
        "filename": file_path.name,
        "format": file_path.suffix,
        "feature_count": len(gdf),
        "columns": list(gdf.columns),
        "crs": get_crs_info(gdf),
        "geometry_type": gdf.geometry.geom_type.unique().tolist(),
        "geometry_stats": get_geometry_stats(gdf),
        "attribute_sample": gdf.head(1).to_dict(orient="records")[0],
    }
    
    return info

def generate_description(
    file_path: Path,
    format: str = "markdown",
    include_stats: bool = True,
) -> str:
    """
    Generate a professional description of a GIS dataset.
    
    Args:
        file_path: Path to the GIS file
        format: Output format (markdown/html/text)
        include_stats: Whether to include detailed statistics
        
    Returns:
        Formatted description string
    """
    # Analyze the dataset
    info = analyze_dataset(file_path)
    
    # Generate description components
    components = {
        "overview": f"This dataset ({info['filename']}) contains {info['feature_count']} {', '.join(info['geometry_type']).lower()} features.",
        "spatial": f"The data uses the {info['crs']} coordinate system.",
        "attributes": f"Available attributes include: {', '.join(info['columns'])}.",
    }
    
    if include_stats:
        stats = info['geometry_stats']
        components["statistics"] = (
            f"The features cover an area of {stats['total_area']:.2f} {stats['area_unit']}, "
            f"with a bounding box extent of {stats['bbox']}."
        )
    
    # Format the output
    return format_output(components, format)

if __name__ == "__main__":
    # Example usage
    description = generate_description(Path("example.shp"))
    print(description) 