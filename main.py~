import argparse
import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

def get_image_metadata(image_path):
    """Extract metadata from an image file, including EXIF data and ICC profiles."""
    try:
        image = Image.open(image_path)
        metadata = {}
        
        # Extract EXIF data
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif_data = image._getexif()
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                metadata[tag_name] = value
        
        # Extract ICC profile data
        if image.info.get("icc_profile"):
            metadata["ICC_Profile"] = "Present"
        else:
            metadata["ICC_Profile"] = "Not Present"
        
        # Extract image mode and format
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = image.size  # (width, height)
        
        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        return {}

def resize_image(input_path, output_path, size, quality, optimize):
    """Resize image while maintaining aspect ratio."""
    try:
        with Image.open(input_path) as img:
            img.thumbnail(size, Image.LANCZOS)
            img.save(output_path, optimize=optimize, quality=quality)
            print(f"Resized image saved to {output_path}")
    except Exception as e:
        logging.error(f"Error resizing image: {e}")

def resize_by_filesize(input_path, output_path, target_size_kb, quality, optimize):
    """Resize image to meet a target file size."""
    try:
        with Image.open(input_path) as img:
            factor = 1.0
            while True:
                img_resized = img.copy()
                img_resized.thumbnail((int(img.width * factor), int(img.height * factor)), Image.LANCZOS)
                img_resized.save(output_path, optimize=optimize, quality=quality)
                if os.path.getsize(output_path) / 1024 <= target_size_kb:
                    print(f"Resized image saved to {output_path}, target file size reached.")
                    break
                factor -= 0.05
                if factor <= 0:
                    logging.error("Error: Unable to reach target file size without excessive quality loss.")
                    break
    except Exception as e:
        logging.error(f"Error resizing image by file size: {e}")

def get_image_resolution(image_path):
    """Returns the resolution of the given image."""
    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        logging.error(f"Error getting image resolution: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Proportional Image Resizer with Metadata Extraction")
    parser.add_argument("image_path", nargs="?", help="Path to the image file")
    parser.add_argument("-s", "--size", nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Target size in pixels")
    parser.add_argument("-fs", "--file-size", type=int, metavar="KB", help="Target file size in KB")
    parser.add_argument("-q", "--quality", type=int, default=95, help="Quality of output image (1-100, default: 95)")
    parser.add_argument("-o", "--optimize", action="store_true", help="Enable image optimization")
    parser.add_argument("-r", "--resolution", action="store_true", help="Output image resolution if no other params are added")
    args = parser.parse_args()
    
    if args.image_path:
        if not os.path.exists(args.image_path):
            logging.error("Error: Image file not found.")
            return
        
        if not os.path.splitext(args.image_path)[1].lower() in VALID_IMAGE_EXTENSIONS:
            logging.error("Error: Unsupported file type. Please provide a valid image file.")
            return
        
        try:
            with Image.open(args.image_path) as img:
                img.verify()  # Ensure the file is a valid image
            
            # Reopen the image after verification to fully load it
            with Image.open(args.image_path) as img:
                img.load()
        except Exception as e:
            logging.error(f"Error: Invalid image file. {e}")
            return

        metadata = get_image_metadata(args.image_path)
        print("Image Metadata:")
        for key, value in metadata.items():
            print(f"{key}: {value}")
        
        if args.size:
            output_path = f"resized_{os.path.basename(args.image_path)}"
            resize_image(args.image_path, output_path, tuple(args.size), args.quality, args.optimize)
        
        if args.file_size:
            output_path = f"resized_{os.path.basename(args.image_path)}"
            resize_by_filesize(args.image_path, output_path, args.file_size, args.quality, args.optimize)
        
        if args.resolution:
            resolution = get_image_resolution(args.image_path)
            if resolution:
                print(f"Image resolution: {resolution[0]}x{resolution[1]}")
    
    elif args.resolution:
        logging.error("Error: No image file provided for resolution check.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
