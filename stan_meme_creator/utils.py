import io
import os
from PIL import Image, ImageSequence

OUTPUT_FOLDER = './output'

def find_transparent_area(template_path):
    with Image.open(template_path) as img:
        # Ensure image is in RGBA format to have an alpha channel
        img = img.convert("RGBA")
        
        width, height = img.size
        left, right, top, bottom = width, 0, height, 0

        for x in range(width):
            for y in range(height):
                r, g, b, a = img.getpixel((x, y))
                if a == 0:  # Transparent pixel
                    left = min(left, x)
                    right = max(right, x)
                    top = min(top, y)
                    bottom = max(bottom, y)

        # Check if no transparent area was found
        if left >= right or top >= bottom:
            return None

        return left, top, right, left, right - left, bottom - top

def is_gif_image(template_path):
    return template_path.lower().endswith('.gif')

def process_gif_template(user_image, template_path, output_path, area):
    with Image.open(template_path) as template:
        frames = []
        for frame in ImageSequence.Iterator(template):
            frame = frame.convert("RGBA")
            user_image_resized = user_image.resize((area[4], area[5]))
            
            # Create a new frame
            base_layer = Image.new("RGBA", frame.size)
            base_layer.paste(user_image_resized, (area[0], area[1]))
            base_layer.paste(frame, (0, 0), frame)
            
            # Convert the frame back to P mode with a palette for GIF compatibility
            base_layer = base_layer.convert("P", palette=Image.ADAPTIVE)
            
            frames.append(base_layer)
        
        # Save the frames as a new animated GIF
        # frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=template.info['duration'], optimize=False)
        # Save the frames as a new animated GIF into a BytesIO object
        gif_bytes_io = io.BytesIO()
        frames[0].save(gif_bytes_io, format='GIF', save_all=True, append_images=frames[1:], loop=0, duration=template.info.get('duration', 100), optimize=False)
        gif_bytes_io.seek(0)  # Rewind to the start of the BytesIO object
        
        return gif_bytes_io

def process_image(user_image, selected_template_path):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(selected_template_path))
    # user_image = Image.open(user_image_path).convert("RGBA")

    area = find_transparent_area(selected_template_path)
    if area:
        print(f"Transparent area found at: {area[0]}, {area[1]}, with width {area[4]} and height {area[5]}")
    else:
        print("No transparent area found.")
        return

    if is_gif_image(selected_template_path):
        gif_bytes_io = process_gif_template(user_image, selected_template_path, output_path, area)
        return gif_bytes_io
    else:
        # For non-GIF templates, use the existing insert_image function
        template_complete = insert_image(user_image, selected_template_path, output_path, area)
        # template_complete.save(output_path)  # Make sure to save the result
        return template_complete


def insert_image(user_image, template_path, output_path, area):

    with Image.open(template_path) as template:
        template = template.convert("RGBA")
        
        # Resize the user image to fit the transparent area
        user_image_resized = user_image.resize((area[4], area[5]))
        
        # Create a new image for the base layer that matches the template size
        base_layer = Image.new("RGBA", template.size)
        
        # Paste the resized user image onto the base layer at the specified area
        base_layer.paste(user_image_resized, (area[0], area[1]))
        
        # Now paste the template onto the base layer, using the template's alpha channel as the mask
        base_layer.paste(template, (0, 0), template)
        
        # Optionally, save the result if needed
        # base_layer.save(output_path, 'PNG')
        
        return base_layer


# def process_image(user_image, selected_template_path):
#     # create output folder if folder doesnt exist 
#     if not os.path.exists(OUTPUT_FOLDER):
#         os.makedirs(OUTPUT_FOLDER)

#     output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(selected_template_path))

#     area = find_transparent_area(selected_template_path)
#     if area:
#         offset_x, offset_y, _, _, desired_width, desired_height = area
#         print(f"Transparent area found at: {offset_x}, {offset_y}, with width {desired_width} and height {desired_height}")
#     else:
#         print("No transparent area found.")

#     template_complete = insert_image(user_image, selected_template_path, output_path, area)
#     return template_complete
   
