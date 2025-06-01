"""
LLM integration for Walter using Ollama
"""
import os
from typing import Optional, Dict, List, Any
import json
import warnings

class LLMManager:
    """Manager for LLM interactions."""
    
    DEFAULT_MODEL = "phi"  # Microsoft's Phi-2 model
    DEFAULT_CONTEXT = 2048  # Default context window
    
    def __init__(
        self,
        model: Optional[str] = None,
        context_window: Optional[int] = None,
        temperature: float = 0.7,
        require_llm: bool = False
    ):
        """Initialize LLM manager."""
        self.model = model or os.getenv("WALTER_MODEL", self.DEFAULT_MODEL)
        self.context_window = context_window or self.DEFAULT_CONTEXT
        self.temperature = temperature
        self.llm_available = False
        
        try:
            import ollama
            self.ollama = ollama
            self._ensure_model()
            self.llm_available = True
        except ImportError as e:
            if require_llm:
                raise ImportError("Ollama is required but not available") from e
            warnings.warn("Ollama not available. LLM features will be disabled.")
            self.ollama = None
    
    def _ensure_model(self):
        """Ensure the selected model is available in Ollama."""
        if not self.llm_available:
            return
            
        try:
            models = self.ollama.list()
            model_names = [m['name'] for m in models['models']]
            
            if self.model not in model_names:
                print(f"Model {self.model} not found. Pulling from Ollama...")
                self.ollama.pull(self.model)
        except Exception as e:
            self.llm_available = False
            warnings.warn(f"Failed to initialize Ollama: {str(e)}")
    
    def generate_description(self, data: Dict[str, Any]) -> str:
        """
        Generate a natural language description of GIS data.
        
        Args:
            data: Dictionary containing dataset information
            
        Returns:
            Generated description or fallback message if LLM is not available
        """
        if not self.llm_available:
            return self._generate_fallback_description(data)
            
        prompt = self._create_description_prompt(data)
        
        try:
            response = self.ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
            )
            return response['response'].strip()
        except Exception as e:
            warnings.warn(f"LLM generation failed: {str(e)}")
            return self._generate_fallback_description(data)
    
    def suggest_tags(self, description: str, count: int = 5) -> List[str]:
        """
        Suggest tags based on dataset description.
        
        Args:
            description: Dataset description
            count: Number of tags to generate
            
        Returns:
            List of suggested tags or basic tags if LLM is not available
        """
        if not self.llm_available:
            return self._generate_fallback_tags(description)
            
        prompt = f"""
        Based on this GIS dataset description, suggest {count} relevant tags:
        
        {description}
        
        Format the tags as a comma-separated list, using lowercase and hyphens for spaces.
        Example: urban-planning, demographics, transportation
        
        Tags:
        """
        
        try:
            response = self.ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
            )
            
            # Clean and format tags
            tags = [
                tag.strip().lower().replace(" ", "-")
                for tag in response['response'].split(",")
            ]
            
            return tags[:count]
        except Exception as e:
            warnings.warn(f"Tag generation failed: {str(e)}")
            return self._generate_fallback_tags(description)
    
    def explain_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a natural language explanation of analysis results.
        
        Args:
            analysis_results: Dictionary of analysis results
            
        Returns:
            Natural language explanation or basic summary if LLM is not available
        """
        if not self.llm_available:
            return self._generate_fallback_analysis(analysis_results)
            
        prompt = f"""
        Explain these GIS analysis results in clear, natural language:
        
        {json.dumps(analysis_results, indent=2)}
        
        Focus on key insights and patterns. Use professional but accessible language.
        """
        
        try:
            response = self.ollama.generate(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
            )
            return response['response'].strip()
        except Exception as e:
            warnings.warn(f"Analysis explanation failed: {str(e)}")
            return self._generate_fallback_analysis(analysis_results)
    
    def _generate_fallback_description(self, data: Dict[str, Any]) -> str:
        """Generate a basic description without LLM."""
        feature_count = data.get('feature_count', 'Unknown')
        geometry_type = ', '.join(data.get('geometry_type', ['Unknown']))
        columns = ', '.join(data.get('columns', []))
        
        return f"""
        Dataset contains {feature_count} features of type {geometry_type}.
        Available attributes: {columns}.
        """.strip()
    
    def _generate_fallback_tags(self, description: str) -> List[str]:
        """Generate basic tags without LLM."""
        return ['gis', 'spatial-data', 'geospatial', 'vector-data', 'analysis']
    
    def _generate_fallback_analysis(self, results: Dict[str, Any]) -> str:
        """Generate basic analysis summary without LLM."""
        return f"""
        Analysis Results Summary:
        - Feature Count: {results.get('feature_count', 'Unknown')}
        - Geometry Types: {', '.join(results.get('geometry_types', ['Unknown']))}
        - Available Attributes: {', '.join(results.get('attributes', []))}
        """.strip()
    
    def _create_description_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for dataset description."""
        return f"""
        Generate a professional description of this GIS dataset:
        
        Dataset Information:
        - Name: {data.get('filename')}
        - Format: {data.get('format')}
        - Features: {data.get('feature_count')} {', '.join(data.get('geometry_type', [])).lower()}
        - CRS: {data.get('crs')}
        - Attributes: {', '.join(data.get('columns', []))}
        
        Statistics:
        {json.dumps(data.get('geometry_stats', {}), indent=2)}
        
        Write a clear, professional description that a GIS analyst would find helpful.
        Focus on the key characteristics and potential uses of the dataset.
        Use natural, flowing language rather than just listing facts.
        """ 