from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
from sentence_transformers import SentenceTransformer
from textwrap import wrap
import re
from urllib.parse import unquote

class MemeGenerator:
    def __init__(self, data_path: str):
        """Initialize MemeGenerator with path to meme data JSON."""
        self.data_path = data_path
        self.meme_data = self._load_meme_data()
        # Load the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Pre-compute embeddings for all tags
        self.tag_embeddings = self._compute_tag_embeddings()

    def _load_meme_data(self) -> List[Dict[str, str]]:
        """Load meme data from JSON file."""
        with open(self.data_path, 'r') as f:
            return json.load(f)

    def _compute_tag_embeddings(self) -> List[np.ndarray]:
        """Pre-compute embeddings for all tag sets."""
        return [
            self.model.encode(meme['tags'], convert_to_tensor=True).cpu()
            for meme in self.meme_data
        ]

    def _extract_image_id(self, image_url: str) -> str:
        """
        Extract standardized ID from image URL.
        
        Args:
            image_url: Full URL of the image
            
        Returns:
            Standardized ID string
        """
        # Get the filename without extension
        filename = unquote(image_url.split('/')[-1]).rsplit('.', 1)[0]
        # Replace spaces and special characters with underscores
        return re.sub(r'[%\s]+', '_', filename)

    def find_relevant_image(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Find most relevant image URL based on prompt using cosine similarity.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Tuple of (image_url, image_id) or None if no relevant image found
        """
        # Encode the prompt and move to CPU
        prompt_embedding = self.model.encode(prompt, convert_to_tensor=True).cpu()
        
        # Calculate cosine similarities
        similarities = [
            float(prompt_embedding @ tag_embedding.cpu().T / 
                 (np.linalg.norm(prompt_embedding.numpy()) * np.linalg.norm(tag_embedding.cpu().numpy())))
            for tag_embedding in self.tag_embeddings
        ]
        
        # Find the best match
        best_match_idx = np.argmax(similarities)
        best_score = similarities[best_match_idx]
        
        # Return None if the similarity is too low
        # if best_score < 0.3:  # Threshold can be adjusted
        #     return None
        
        image_url = self.meme_data[best_match_idx]['images']
        image_id = self._extract_image_id(image_url)
            
        return image_url, image_id

    @staticmethod
    def _calculate_font_size(img: Image.Image, text: str, max_width_ratio: float = 0.9) -> Tuple[ImageFont.FreeTypeFont, int]:
        """
        Calculate the optimal font size for the text to fit the image width.
        
        Args:
            img: The image to add text to
            text: The text to add
            max_width_ratio: Maximum width of text relative to image width
            
        Returns:
            Tuple of (font, wrapped_text_lines)
        """
        target_height = img.height // 5  # Target height is 1/5 of image height
        max_width = int(img.width * max_width_ratio)
        
        # Start with a large size and scale down
        size = target_height
        while size > 0:
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                font = ImageFont.load_default()
                
            # Calculate wrapped text
            avg_char_width = font.getlength('x')
            chars_per_line = max(1, int(max_width / avg_char_width))
            wrapped_text = wrap(text, width=chars_per_line)
            
            # Check if text fits width and doesn't exceed height
            max_line_width = max(font.getlength(line) for line in wrapped_text)
            total_height = len(wrapped_text) * (font.size + 10)  # Add padding between lines
            
            if max_line_width <= max_width and total_height <= target_height * 2:
                return font, wrapped_text
                
            size -= 1
        
        # Fallback
        return ImageFont.load_default(), wrap(text, width=30)

    @staticmethod
    def generate_meme(image_url: str, text: str) -> Image.Image:
        """Generate a meme by adding text to an image with dynamic sizing."""
        # Download image
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGBA if necessary
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        
        # Calculate font size and wrap text
        font, wrapped_text = MemeGenerator._calculate_font_size(img, text)
        
        # Calculate text positions
        line_height = font.size + 10  # Add padding between lines
        total_height = len(wrapped_text) * line_height
        
        # Position text near top with padding
        top_padding = img.height * 0.05  # 5% of image height
        y = top_padding
        
        # Draw each line of text
        for line in wrapped_text:
            # Calculate center position for this line
            text_width = draw.textlength(line, font=font)
            x = (img.width - text_width) / 2
            
            # Draw text outline
            outline_color = "black"
            outline_width = max(1, font.size // 15)  # Scale outline with font size
            
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill="white")
            
            # Move to next line
            y += line_height
        
        return img