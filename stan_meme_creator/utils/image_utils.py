from typing import Optional, Tuple
from PIL import Image
import numpy as np

def find_transparent_area(template_path: str) -> Optional[Tuple[int, int, int, int, int, int]]:
    """
    Find the transparent area in an image template.
    
    Args:
        template_path: Path to the template image
        
    Returns:
        Tuple of (left, top, right, bottom, width, height) or None if no transparent area found
    """
    with Image.open(template_path) as img:
        img = img.convert("RGBA")
        width, height = img.size
        left, right, top, bottom = width, 0, height, 0

        # Convert to numpy array for faster processing
        img_array = np.array(img)
        alpha_channel = img_array[:, :, 3]
        
        # Find coordinates where alpha is 0
        transparent_coords = np.where(alpha_channel == 0)
        
        if len(transparent_coords[0]) == 0:
            return None
            
        top = transparent_coords[0].min()
        bottom = transparent_coords[0].max()
        left = transparent_coords[1].min()
        right = transparent_coords[1].max()

        return left, top, right, bottom, right - left, bottom - top

def resize_image_to_fit_area(
    image: Image.Image,
    area_width: int,
    area_height: int,
    maintain_aspect_ratio: bool = True
) -> Image.Image:
    """
    Resize an image to fit into a specified area.
    
    Args:
        image: Source image to resize
        area_width: Target width
        area_height: Target height
        maintain_aspect_ratio: Whether to maintain the original aspect ratio
        
    Returns:
        Resized image
    """
    if maintain_aspect_ratio:
        img_width, img_height = image.size
        target_width = area_width
        target_height = int((img_height * area_width) / img_width)
        
        if target_height > area_height:
            target_height = area_height
            target_width = int((img_width * area_height) / img_height)
        
        image_resized = image.resize((target_width, target_height))
        new_image = Image.new("RGBA", (area_width, area_height), (0, 0, 0, 0))
        paste_position = ((area_width - target_width) // 2, (area_height - target_height) // 2)
        new_image.paste(image_resized, paste_position)
        return new_image
    
    return image.resize((area_width, area_height)) 