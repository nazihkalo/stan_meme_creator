from pathlib import Path
from typing import List, Dict

from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent
STATIC_DIR = ROOT_DIR / "static"

# Template directories
MEME_TEMPLATES_DIR = STATIC_DIR / "meme_templates"
OVERLAY_TEMPLATES_DIR = STATIC_DIR / "overlay_templates"

class TemplateManager:
    """Manages template discovery and organization."""
    
    @staticmethod
    def get_template_paths() -> Dict[str, List[str]]:
        """
        Get all available template paths organized by category.
        
        Returns:
            Dictionary with template categories and their paths
        """
        return {
            "meme_templates": sorted(str(p) for p in MEME_TEMPLATES_DIR.glob("*.png")),
            "overlay_templates": sorted(str(p) for p in OVERLAY_TEMPLATES_DIR.glob("*.png"))
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