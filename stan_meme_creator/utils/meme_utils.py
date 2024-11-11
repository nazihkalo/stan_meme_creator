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
import base64

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
        # Start with a larger base size - 1/8 of image height instead of 1/5
        target_height = img.height // 8
        max_width = int(img.width * max_width_ratio)
        
        # Binary search for optimal font size
        min_size = 10
        max_size = target_height
        optimal_font = None
        optimal_wrapped_text = None
        
        while min_size <= max_size:
            current_size = (min_size + max_size) // 2
            try:
                font = ImageFont.truetype("arial.ttf", current_size)
            except:
                font = ImageFont.load_default(size=current_size)
                
            # Calculate wrapped text
            avg_char_width = font.getlength('x')
            chars_per_line = max(1, int(max_width / avg_char_width))
            wrapped_text = wrap(text, width=chars_per_line)
            
            # Check if text fits width and doesn't exceed height
            max_line_width = max(font.getlength(line) for line in wrapped_text)
            total_height = len(wrapped_text) * (font.size + 10)  # Add padding between lines
            
            if max_line_width <= max_width and total_height <= target_height * 2:
                optimal_font = font
                optimal_wrapped_text = wrapped_text
                min_size = current_size + 1  # Try larger size
            else:
                max_size = current_size - 1  # Try smaller size
        
        if optimal_font is None:
            return ImageFont.load_default(), wrap(text, width=30)
        
        return optimal_font, optimal_wrapped_text

    @staticmethod
    def generate_meme(image_url: str, text: str, text_position: str = 'top') -> Image.Image:
        """
        Generate a meme by adding text to an image with dynamic sizing.
        
        Args:
            image_url: URL of the image
            text: Text to add to the image
            text_position: Where to place the text ('top', 'bottom', or 'center')
        """
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
        line_height = int(font.size * 1.2)  # Increased line spacing
        total_height = len(wrapped_text) * line_height
        
        # Position text based on text_position parameter
        padding = img.height * 0.02  # 2% padding
        if text_position == 'top':
            y = padding
        elif text_position == 'bottom':
            y = img.height - total_height - padding
        else:  # center
            y = (img.height - total_height) / 2
        
        # Draw each line of text
        for line in wrapped_text:
            # Calculate center position for this line
            text_width = draw.textlength(line, font=font)
            x = (img.width - text_width) / 2
            
            # Draw text outline
            outline_color = "black"
            outline_width = max(2, font.size // 12)
            
            # Thicker outline for better visibility
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), line, font=font, fill="white")
            
            # Move to next line
            y += line_height
        
        return img

    def find_top_images(self, prompt: str, n: int = 9) -> List[Tuple[str, str, float]]:
        # Encode the prompt and move to CPU immediately
        prompt_embedding = self.model.encode(prompt, convert_to_tensor=True).cpu()
        
        # Calculate cosine similarities
        similarities = [
            float(prompt_embedding @ tag_embedding.cpu().T / 
                 (np.linalg.norm(prompt_embedding.numpy()) * np.linalg.norm(tag_embedding.cpu().numpy())))
            for tag_embedding in self.tag_embeddings
        ]
        
        # Get indices of top N similarities
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        # Create result list
        results = []
        for idx in top_indices:
            # if similarities[idx] >= 0.3:  # Keep similarity threshold
            image_url = self.meme_data[idx]['images']
            image_id = self._extract_image_id(image_url)
            results.append((image_url, image_id, similarities[idx]))
        
        return results

    @staticmethod
    def prepare_meme_data(image_url: str) -> dict:
        """
        Prepare image data for the interactive editor without applying text.
        
        Args:
            image_url: URL of the image
            
        Returns:
            Dictionary with image data and dimensions
        """
        # Download image
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGBA if necessary
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # Convert to base64 for frontend
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image": img_str,
            "width": img.width,
            "height": img.height
        }