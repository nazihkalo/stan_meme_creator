from typing import Optional, Tuple, BinaryIO
from PIL import Image, ImageSequence
import io
from pathlib import Path

from stan_meme_creator.utils.image_utils import find_transparent_area, resize_image_to_fit_area

class ImageProcessor:
    """Handles all image processing operations for the meme creator."""
    
    @staticmethod
    def process_image(
        user_image: Image.Image,
        template_path: str,
        maintain_aspect_ratio: bool = False
    ) -> Image.Image | BinaryIO:
        """
        Process an image with the selected template.
        
        Args:
            user_image: The user's uploaded image
            template_path: Path to the template to apply
            maintain_aspect_ratio: Whether to maintain aspect ratio when fitting image
            
        Returns:
            Processed image or GIF binary stream
        """
        area = find_transparent_area(template_path)
        if not area:
            raise ValueError("No transparent area found in template")

        if template_path.lower().endswith('.gif'):
            return ImageProcessor._process_gif_template(user_image, template_path, area)
        else:
            return ImageProcessor._process_static_template(
                user_image, template_path, area, maintain_aspect_ratio
            )

    @staticmethod
    def _process_static_template(
        user_image: Image.Image,
        template_path: str,
        area: Tuple[int, int, int, int, int, int],
        maintain_aspect_ratio: bool
    ) -> Image.Image:
        """Process a static image template."""
        with Image.open(template_path) as template:
            template = template.convert("RGBA")
            user_image_resized = resize_image_to_fit_area(
                user_image, area[4], area[5], maintain_aspect_ratio
            )
            
            base_layer = Image.new("RGBA", template.size)
            base_layer.paste(user_image_resized, (area[0], area[1]))
            base_layer.paste(template, (0, 0), template)
            
            return base_layer

    @staticmethod
    def _process_gif_template(
        user_image: Image.Image,
        template_path: str,
        area: Tuple[int, int, int, int, int, int]
    ) -> BinaryIO:
        """Process a GIF template."""
        with Image.open(template_path) as template:
            frames = []
            for frame in ImageSequence.Iterator(template):
                frame = frame.convert("RGBA")
                user_image_resized = user_image.resize((area[4], area[5]))
                
                base_layer = Image.new("RGBA", frame.size)
                base_layer.paste(user_image_resized, (area[0], area[1]))
                base_layer.paste(frame, (0, 0), frame)
                base_layer = base_layer.convert("P", palette=Image.ADAPTIVE)
                
                frames.append(base_layer)
            
            gif_bytes_io = io.BytesIO()
            frames[0].save(
                gif_bytes_io,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=template.info.get('duration', 100),
                optimize=False
            )
            gif_bytes_io.seek(0)
            
            return gif_bytes_io 