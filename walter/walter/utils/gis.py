"""
GIS utility functions for Walter
"""
from typing import Dict, Any
import geopandas as gpd
from shapely.geometry import box

def get_crs_info(gdf: gpd.GeoDataFrame) -> str:
    """
    Get a human-readable description of the coordinate reference system.
    
    Args:
        gdf: GeoDataFrame to analyze
        
    Returns:
        String description of the CRS
    """
    crs = gdf.crs
    if crs is None:
        return "undefined"
    
    if isinstance(crs, str):
        return crs
        
    # Handle pyproj CRS object
    auth_name = crs.to_authority()[0] if crs.to_authority() else "Custom"
    auth_code = crs.to_authority()[1] if crs.to_authority() else "Unknown"
    
    return f"{auth_name}:{auth_code}"

def get_geometry_stats(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """
    Calculate basic geometric statistics for a GeoDataFrame.
    
    Args:
        gdf: GeoDataFrame to analyze
        
    Returns:
        Dictionary of geometry statistics
    """
    # Get the total bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    bbox = box(minx, miny, maxx, maxy)
    
    # Calculate statistics
    stats = {
        "bbox": f"({minx:.2f}, {miny:.2f}, {maxx:.2f}, {maxy:.2f})",
        "total_area": gdf.geometry.area.sum(),
        "mean_area": gdf.geometry.area.mean(),
        "bbox_area": bbox.area,
    }
    
    return stats

def validate_geometry(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """
    Validate geometry and return any issues found.
    
    Args:
        gdf: GeoDataFrame to validate
        
    Returns:
        Dictionary of validation results
    """
    results = {
        "valid": gdf.geometry.is_valid.all(),
        "issues": [],
    }
    
    # Check for common issues
    if not results["valid"]:
        invalid_geoms = gdf[~gdf.geometry.is_valid]
        results["issues"] = [
            {
                "index": idx,
                "reason": geom.validation_error
            }
            for idx, geom in invalid_geoms.geometry.items()
        ]
    
    return results 