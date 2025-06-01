"""
Walter GUI using Streamlit
"""
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import tempfile
import os
import json
import pandas as pd

from walter.commands.describe import analyze_dataset, generate_description
from walter.integrations.llm import LLMManager
from walter.utils.gis import validate_geometry

def init_session_state():
    """Initialize session state variables."""
    if 'llm' not in st.session_state:
        st.session_state.llm = LLMManager()
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None

def render_sidebar():
    """Render the sidebar with LLM settings."""
    with st.sidebar:
        st.title("🤖 LLM Settings")
        
        # Model selection
        model = st.selectbox(
            "Select LLM Model",
            ["phi", "llama2", "mistral", "codellama"],
            index=0,
        )
        
        # Temperature
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
        )
        
        if st.button("Apply Settings"):
            st.session_state.llm = LLMManager(
                model=model,
                temperature=temperature,
            )
            st.success("✅ Settings applied!")

def render_file_upload():
    """Render the file upload section."""
    st.title("📁 Load GIS Data")
    
    uploaded_file = st.file_uploader(
        "Choose a GIS file",
        type=["shp", "geojson", "gpkg"],
        help="Upload a shapefile (as ZIP), GeoJSON, or GeoPackage file",
    )
    
    if uploaded_file:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = Path(tmp.name)
        
        try:
            # Read the data
            gdf = gpd.read_file(tmp_path)
            st.session_state.current_file = tmp_path
            st.session_state.current_data = gdf
            
            st.success(f"✅ Loaded {uploaded_file.name}")
            
            # Show preview
            st.subheader("📊 Data Preview")
            st.dataframe(gdf.head())
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
        finally:
            # Clean up temp file
            os.unlink(tmp_path)

def render_map():
    """Render the interactive map."""
    if st.session_state.current_data is not None:
        st.title("🗺️ Interactive Map")
        
        gdf = st.session_state.current_data
        
        # Create map centered on data
        center = [
            gdf.geometry.centroid.y.mean(),
            gdf.geometry.centroid.x.mean()
        ]
        m = folium.Map(location=center, zoom_start=10)
        
        # Add GeoJSON layer
        folium.GeoJson(
            gdf.__geo_interface__,
            name="Data",
            style_function=lambda x: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            }
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Display map
        folium_static(m)

def render_statistics():
    """Render statistical analysis and charts."""
    if st.session_state.current_data is not None:
        st.title("📈 Statistical Analysis")
        
        gdf = st.session_state.current_data
        
        # Select columns for analysis
        numeric_cols = gdf.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            selected_col = st.selectbox(
                "Select column for analysis",
                numeric_cols
            )
            
            col1, col2 = st.columns(2)
            
            # Basic statistics
            with col1:
                st.subheader("📊 Summary Statistics")
                stats = gdf[selected_col].describe()
                st.dataframe(stats)
            
            # Distribution plot
            with col2:
                st.subheader("📉 Distribution")
                fig = go.Figure(data=[go.Histogram(x=gdf[selected_col])])
                fig.update_layout(
                    title=f"Distribution of {selected_col}",
                    xaxis_title=selected_col,
                    yaxis_title="Count"
                )
                st.plotly_chart(fig)
            
            # Box plot
            st.subheader("📦 Box Plot")
            fig = px.box(gdf, y=selected_col)
            fig.update_layout(title=f"Box Plot of {selected_col}")
            st.plotly_chart(fig)
            
            # Spatial correlation
            if st.checkbox("Show Spatial Pattern"):
                st.subheader("🗺️ Spatial Pattern")
                choropleth = folium.Map(
                    location=[
                        gdf.geometry.centroid.y.mean(),
                        gdf.geometry.centroid.x.mean()
                    ],
                    zoom_start=10
                )
                
                folium.Choropleth(
                    geo_data=gdf.__geo_interface__,
                    data=gdf,
                    columns=[gdf.index, selected_col],
                    key_on='feature.id',
                    fill_color='YlOrRd',
                    legend_name=selected_col
                ).add_to(choropleth)
                
                folium_static(choropleth)

def export_results():
    """Export analysis results in various formats."""
    if st.session_state.current_data is not None:
        st.title("📤 Export Results")
        
        export_format = st.selectbox(
            "Select export format",
            ["CSV", "GeoJSON", "Excel", "PDF Report"]
        )
        
        if st.button("Export"):
            gdf = st.session_state.current_data
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                if export_format == "CSV":
                    gdf.to_csv(tmp.name, index=False)
                    mime = "text/csv"
                    extension = "csv"
                elif export_format == "GeoJSON":
                    gdf.to_file(tmp.name, driver="GeoJSON")
                    mime = "application/json"
                    extension = "geojson"
                elif export_format == "Excel":
                    gdf.to_excel(tmp.name, index=False)
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    extension = "xlsx"
                elif export_format == "PDF Report":
                    # Generate PDF report with analysis results
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    
                    # Add title
                    pdf.cell(200, 10, txt="Walter GIS Analysis Report", ln=1, align='C')
                    
                    # Add dataset info
                    pdf.cell(200, 10, txt=f"Dataset: {st.session_state.current_file.name}", ln=1, align='L')
                    pdf.cell(200, 10, txt=f"Features: {len(gdf)}", ln=1, align='L')
                    
                    # Add statistics
                    pdf.cell(200, 10, txt="Summary Statistics:", ln=1, align='L')
                    for col in gdf.select_dtypes(include=['float64', 'int64']).columns:
                        stats = gdf[col].describe()
                        pdf.cell(200, 10, txt=f"{col}:", ln=1, align='L')
                        for stat, value in stats.items():
                            pdf.cell(200, 10, txt=f"  {stat}: {value:.2f}", ln=1, align='L')
                    
                    pdf.output(tmp.name)
                    mime = "application/pdf"
                    extension = "pdf"
                
                with open(tmp.name, "rb") as f:
                    data = f.read()
                    st.download_button(
                        f"Download {export_format}",
                        data=data,
                        file_name=f"walter_analysis.{extension}",
                        mime=mime
                    )
                
                os.unlink(tmp.name)

def render_llm_analysis():
    """Render LLM-powered analysis features."""
    if st.session_state.current_data is not None:
        st.title("🤖 AI Analysis")
        
        # Pattern detection
        if st.button("Detect Patterns"):
            with st.spinner("Analyzing patterns..."):
                gdf = st.session_state.current_data
                stats = {
                    "feature_count": len(gdf),
                    "attributes": list(gdf.columns),
                    "geometry_types": gdf.geometry.type.unique().tolist(),
                    "numeric_stats": gdf.describe().to_dict()
                }
                
                prompt = f"""
                Analyze these GIS dataset statistics and identify interesting patterns:
                
                {json.dumps(stats, indent=2)}
                
                Focus on:
                1. Distribution patterns
                2. Spatial relationships
                3. Potential correlations
                4. Anomalies or outliers
                """
                
                analysis = st.session_state.llm.explain_analysis(stats)
                st.markdown(analysis)
        
        # Recommendations
        if st.button("Get Recommendations"):
            with st.spinner("Generating recommendations..."):
                gdf = st.session_state.current_data
                data = {
                    "columns": list(gdf.columns),
                    "geometry_type": gdf.geometry.type.unique().tolist(),
                    "feature_count": len(gdf)
                }
                
                prompt = f"""
                Based on this GIS dataset structure, suggest analysis approaches:
                
                {json.dumps(data, indent=2)}
                
                Recommend:
                1. Useful visualizations
                2. Statistical analyses
                3. Spatial operations
                4. Additional data that could enhance the analysis
                """
                
                recommendations = st.session_state.llm.generate_description(data)
                st.markdown(recommendations)

def render_analysis():
    """Render the analysis section."""
    if st.session_state.current_data is not None:
        st.title("📊 Analysis")
        
        # Generate description
        if st.button("Generate Description"):
            with st.spinner("Generating description..."):
                data = analyze_dataset(st.session_state.current_file)
                description = st.session_state.llm.generate_description(data)
                st.markdown(description)
        
        # Generate tags
        if st.button("Suggest Tags"):
            with st.spinner("Generating tags..."):
                data = analyze_dataset(st.session_state.current_file)
                description = generate_description(st.session_state.current_file)
                tags = st.session_state.llm.suggest_tags(description)
                
                for tag in tags:
                    st.markdown(f"🏷️ `{tag}`")
        
        # Validate geometry
        if st.button("Validate Geometry"):
            with st.spinner("Validating geometry..."):
                results = validate_geometry(st.session_state.current_data)
                
                if results['valid']:
                    st.success("✅ All geometries are valid!")
                else:
                    st.error("❌ Found invalid geometries:")
                    for issue in results['issues']:
                        st.markdown(f"- Feature {issue['index']}: {issue['reason']}")

def main():
    """Main GUI application."""
    st.set_page_config(
        page_title="Walter - Your AI GIS Assistant",
        page_icon="🌍",
        layout="wide",
    )
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.title("🌍 Walter - Your AI GIS Assistant")
    st.markdown("""
    Welcome to Walter! I'm your AI-powered GIS assistant, ready to help you:
    - 📝 Generate professional descriptions for your spatial data
    - 🏷️ Suggest relevant tags and categories
    - 🔍 Validate and analyze geometries
    - 🗺️ Visualize your data interactively
    - 📊 Generate statistical insights
    - 📈 Create beautiful visualizations
    - 🤖 Get AI-powered recommendations
    - 📤 Export results in various formats
    """)
    
    # Render main sections
    render_file_upload()
    render_map()
    render_statistics()
    render_llm_analysis()
    render_analysis()
    export_results()

if __name__ == "__main__":
    main() 