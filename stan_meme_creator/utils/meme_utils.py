from typing import List, Dict, Optional
import json
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import io

class MemeGenerator:
    def __init__(self, data_path: str):
        """Initialize MemeGenerator with path to meme data JSON."""
        self.data_path = data_path
        self.meme_data = self._load_meme_data()

    def _load_meme_data(self) -> List[Dict[str, str]]:
        """Load meme data from JSON file."""
        with open(self.data_path, 'r') as f:
            return json.load(f)

    def find_relevant_image(self, prompt: str) -> Optional[str]:
        """
        Find most relevant image URL based on prompt by matching tags.
        Basic implementation - can be enhanced with better matching logic.
        """
        prompt_words = set(prompt.lower().split())
        
        best_match = None
        best_score = 0
        
        for meme in self.meme_data:
            tags = set(tag.strip().lower() for tag in meme['tags'].split(','))
            score = len(tags.intersection(prompt_words))
            if score > best_score:
                best_score = score
                best_match = meme['images']
                
        return best_match

    @staticmethod
    def generate_meme(image_url: str, text: str) -> Image.Image:
        """Generate a meme by adding text to an image."""
        # Download image
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        
        # Load a font (you'll need to provide a path to a font file)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add text with outline
        text_width = draw.textlength(text, font=font)
        x = (img.width - text_width) / 2
        y = img.height - 100  # Position text near bottom
        
        # Draw text outline
        outline_color = "black"
        for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill="white")
        
        return img 