"""
ArcGIS Online integration for Walter
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import geopandas as gpd
import json

class AGOLManager:
    """ArcGIS Online content manager for Walter."""
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        portal_url: Optional[str] = "https://www.arcgis.com",
    ):
        """Initialize AGOL manager."""
        self.username = username or os.getenv("AGOL_USERNAME")
        self.password = password or os.getenv("AGOL_PASSWORD")
        
        if not (self.username and self.password):
            raise ValueError(
                "ArcGIS Online credentials not found. Set AGOL_USERNAME and AGOL_PASSWORD environment variables."
            )
        
        self.gis = GIS(portal_url, self.username, self.password)

    def upload_data(
        self,
        file_path: Path,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """Upload data to ArcGIS Online."""
        # Determine content type
        content_type = self._get_content_type(file_path)
        
        # Use filename as title if not provided
        title = title or file_path.stem
        
        # Add default tags
        tags = tags or []
        tags.extend(["walter", "automated-upload"])
        
        # Upload the item
        item = self.gis.content.add({
            "title": title,
            "type": content_type,
            "tags": ",".join(tags),
            "description": description or f"Uploaded by Walter: {title}",
        }, data=str(file_path))
        
        return {
            "id": item.id,
            "title": item.title,
            "url": item.homepage,
            "type": item.type,
        }

    def update_metadata(
        self,
        item_id: str,
        metadata: Dict,
        thumbnail: Optional[Path] = None,
    ) -> Dict:
        """Update item metadata."""
        item = self.gis.content.get(item_id)
        
        # Update metadata
        item.update(metadata)
        
        # Update thumbnail if provided
        if thumbnail and thumbnail.exists():
            item.update(thumbnail=str(thumbnail))
        
        return {
            "id": item.id,
            "title": item.title,
            "url": item.homepage,
        }

    def create_feature_service(
        self,
        gdf: gpd.GeoDataFrame,
        title: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """Create a feature service from a GeoDataFrame."""
        # Convert GeoDataFrame to JSON
        geojson = json.loads(gdf.to_json())
        
        # Create feature collection
        features = {
            "layerDefinition": {
                "geometryType": self._get_geometry_type(gdf),
                "fields": self._get_fields_schema(gdf),
            },
            "featureSet": {
                "features": geojson["features"],
                "geometryType": self._get_geometry_type(gdf),
            },
        }
        
        # Create feature service
        service = self.gis.content.create_service(
            title,
            tags=tags or ["walter", "automated-service"],
            description=description or f"Feature service created by Walter: {title}",
        )
        
        # Add features
        layer = FeatureLayer.fromitem(service)
        layer.edit_features(adds=geojson["features"])
        
        return {
            "id": service.id,
            "title": service.title,
            "url": service.url,
            "type": service.type,
        }

    def _get_content_type(self, file_path: Path) -> str:
        """Determine AGOL content type from file extension."""
        extension_map = {
            ".shp": "Shapefile",
            ".geojson": "GeoJson",
            ".csv": "CSV",
            ".zip": "Shapefile",
            ".gpkg": "GeoPackage",
        }
        return extension_map.get(file_path.suffix.lower(), "File")

    def _get_geometry_type(self, gdf: gpd.GeoDataFrame) -> str:
        """Get AGOL geometry type from GeoDataFrame."""
        geom_type = gdf.geometry.geom_type.iloc[0]
        type_map = {
            "Point": "esriGeometryPoint",
            "LineString": "esriGeometryPolyline",
            "Polygon": "esriGeometryPolygon",
            "MultiPoint": "esriGeometryMultipoint",
            "MultiLineString": "esriGeometryPolyline",
            "MultiPolygon": "esriGeometryPolygon",
        }
        return type_map.get(geom_type, "esriGeometryPoint")

    def _get_fields_schema(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Generate AGOL fields schema from GeoDataFrame."""
        type_map = {
            "int64": "esriFieldTypeInteger",
            "float64": "esriFieldTypeDouble",
            "object": "esriFieldTypeString",
            "bool": "esriFieldTypeSmallInteger",
            "datetime64[ns]": "esriFieldTypeDate",
        }
        
        fields = []
        for col, dtype in gdf.dtypes.items():
            if col != "geometry":
                fields.append({
                    "name": col,
                    "alias": col,
                    "type": type_map.get(str(dtype), "esriFieldTypeString"),
                    "nullable": True,
                })
        
        return fields 