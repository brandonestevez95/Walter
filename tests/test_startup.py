"""
Startup test script for Walter
Tests all major components and dependencies
"""
import sys
import importlib
from pathlib import Path
import os

def test_dependency(name):
    """Test if a dependency can be imported."""
    try:
        importlib.import_module(name)
        return True
    except ImportError as e:
        return False, str(e)

def main():
    # Check if LLM testing is enabled
    test_llm = os.getenv("WALTER_TEST_LLM", "").lower() == "true"
    
    # Core dependencies to test
    DEPENDENCIES = {
        'Core GIS': ['geopandas', 'shapely', 'fiona', 'pyogrio'],
        'Visualization': ['plotly', 'folium', 'streamlit'],
        'Export': ['fpdf', 'openpyxl'],
        'Analysis': ['scipy', 'statsmodels'],
        'Utils': ['markdown', 'yaml', 'jinja2', 'rich', 'typer']
    }
    
    # Only test Ollama if LLM testing is enabled
    if test_llm:
        DEPENDENCIES['LLM Integration'] = ['ollama']
    
    print("🔍 Running Walter startup tests...")
    print("\n1. Testing Python version...")
    python_version = sys.version_info
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Error: Python 3.9 or higher is required")
        sys.exit(1)
    print("✅ Python version OK")
    
    print("\n2. Testing dependencies...")
    all_passed = True
    
    for category, deps in DEPENDENCIES.items():
        print(f"\n📦 Testing {category} dependencies:")
        for dep in deps:
            result = test_dependency(dep)
            if isinstance(result, tuple):
                print(f"❌ {dep}: Failed - {result[1]}")
                all_passed = False
            else:
                print(f"✅ {dep}: OK")
    
    print("\n3. Testing Walter package structure...")
    walter_root = Path(__file__).parent.parent / 'walter'
    required_dirs = ['commands', 'utils', 'integrations']
    required_files = [
        'gui.py',
        'integrations/llm.py',
        'integrations/gitbook.py',
        'utils/gis.py',
    ]
    
    for dir_name in required_dirs:
        dir_path = walter_root / dir_name
        if not dir_path.is_dir():
            print(f"❌ Missing directory: {dir_name}")
            all_passed = False
        else:
            print(f"✅ Found directory: {dir_name}")
    
    for file_name in required_files:
        file_path = walter_root / file_name
        if not file_path.is_file():
            print(f"❌ Missing file: {file_name}")
            all_passed = False
        else:
            print(f"✅ Found file: {file_name}")
    
    print("\n4. Testing LLM integration...")
    if test_llm:
        try:
            from walter.integrations.llm import LLMManager
            llm = LLMManager(require_llm=True)
            print("✅ LLM integration OK")
        except Exception as e:
            print(f"❌ LLM integration error: {str(e)}")
            all_passed = False
    else:
        try:
            from walter.integrations.llm import LLMManager
            llm = LLMManager(require_llm=False)
            print("✅ LLM integration OK (running in fallback mode)")
        except Exception as e:
            print(f"❌ LLM integration error: {str(e)}")
            all_passed = False
    
    print("\n5. Testing GUI startup...")
    try:
        import streamlit as st
        from walter.gui import main
        print("✅ GUI components OK")
    except Exception as e:
        print(f"❌ GUI startup error: {str(e)}")
        all_passed = False
    
    print("\nFinal Results:")
    if all_passed:
        if test_llm:
            print("🎉 All tests passed! Walter is ready to run with full LLM support.")
        else:
            print("🎉 All tests passed! Walter is ready to run (LLM features in fallback mode).")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 