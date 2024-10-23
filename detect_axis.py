import os
from PIL import Image

def crop_images_in_folder(input_folder, output_folder, crop_box=(246, 90, 820, 400)):
    """Crops all images in a folder using the specified bounding box.

    Args:
        input_folder: Path to the folder containing the images.
        output_folder: Path to the folder where cropped images will be saved.
        crop_box: A tuple (left, upper, right, lower) specifying the cropping region.
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if not filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):  # Add more extensions if needed
            continue  # Skip files that are not images

        filepath = os.path.join(input_folder, filename)
        try:
            img = Image.open(filepath)
            cropped_img = img.crop(crop_box)
            output_filepath = os.path.join(output_folder, filename)
            cropped_img.save(output_filepath)
            print(f"Cropped and saved: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Example usage:
input_folder = "image"  # Replace with the actual input folder
output_folder = "cropped_images" # Replace with the desired output folder
crop_images_in_folder(input_folder, output_folder)