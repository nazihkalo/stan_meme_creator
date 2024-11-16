from pathlib import Path
from typing import List, Dict
import streamlit as st

from stan_meme_creator.config import MEME_TEMPLATES_DIR, OVERLAY_TEMPLATES_DIR

class TemplateManager:
    """Manages template discovery and organization."""
    
    @staticmethod
    def get_template_paths() -> Dict[str, List[str]]:
        """
        Get all available template paths organized by category.
        
        Returns:
            Dictionary with template categories and their paths
        """
        def safe_glob(directory: Path, pattern: str) -> List[str]:
            if not directory.exists():
                st.warning(f"Template directory not found: {directory}")
                return []
            return sorted(str(p) for p in directory.glob(pattern))

        return {
            "meme_templates": safe_glob(MEME_TEMPLATES_DIR, "*.png"),
            "overlay_templates": safe_glob(OVERLAY_TEMPLATES_DIR, "*.png")
        }

    @staticmethod
    def get_template_names() -> Dict[str, List[str]]:
        """
        Get all template names organized by category.
        
        Returns:
            Dictionary with template categories and their names
        """
        return {
            category: [Path(p).stem for p in paths]
            for category, paths in TemplateManager.get_template_paths().items()
        } 