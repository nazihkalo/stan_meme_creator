from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent
STATIC_DIR = ROOT_DIR / "static"
OUTPUT_DIR = ROOT_DIR / "output"

# Template directories
MEME_TEMPLATES_DIR = STATIC_DIR / "meme_templates"
OVERLAY_TEMPLATES_DIR = STATIC_DIR / "overlay_templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True) 