import os
from PIL import Image

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
    # with Image.open(template_path) as template:
        
    #     user_image = user_image.convert("RGBA")
    #     # Resize user image to fit the transparent area
    #     user_image = user_image.resize((area[4], area[5]))

    #     # Ensure template is in RGBA to support transparency
    #     template = template.convert("RGBA")

    #     # Paste the user image onto the template
    #     template.paste(user_image, (area[0], area[1]), user_image)

    #     # Save the modified template
    #     # template.save(output_path, 'PNG')
    #     return template

def process_image(user_image, selected_template_path):
    # create output folder if folder doesnt exist 
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(selected_template_path))

    area = find_transparent_area(selected_template_path)
    if area:
        offset_x, offset_y, _, _, desired_width, desired_height = area
        print(f"Transparent area found at: {offset_x}, {offset_y}, with width {desired_width} and height {desired_height}")
    else:
        print("No transparent area found.")

    template_complete = insert_image(user_image, selected_template_path, output_path, area)
    return template_complete
   
