import os
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from rembg import remove
from typing import Optional

# Configure logging (consistent with your previous scripts)
log_file = os.path.expanduser('~/mac_resource_cleaner.log')
logger = logging.getLogger('BackgroundRemover')
logger.setLevel(logging.INFO)

# Create and configure file handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Create and configure stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Clear existing handlers and add new ones
logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class BackgroundRemover:
    """Class to remove backgrounds from images and apply optional edits."""

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = os.path.expanduser(input_dir)
        self.output_dir = os.path.expanduser(output_dir)
        self.supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

    def ensure_output_dir(self):
        """Ensure the output directory exists."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Output directory ensured: {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to create output directory {self.output_dir}: {e}")
            raise

    def remove_background(self, input_path: str, background_color: Optional[tuple] = None) -> Optional[Image.Image]:
        """Remove background from an image and optionally set a solid background color."""
        try:
            with open(input_path, 'rb') as f:
                input_image = f.read()
            output_image = remove(input_image)
            img = Image.open(io.BytesIO(output_image)).convert('RGBA')

            if background_color:
                # Create a new image with the specified background color
                bg = Image.new('RGBA', img.size, background_color)
                bg.paste(img, (0, 0), img)  # Use alpha channel as mask
                img = bg

            return img
        except Exception as e:
            logger.error(f"Failed to process {input_path}: {e}")
            return None

    def process_images(self, background_color: Optional[tuple] = None):
        """Process all images in the input directory."""
        logger.info(f"Starting background removal for images in {self.input_dir}")
        self.ensure_output_dir()

        processed = 0
        failed = 0
        for file in os.listdir(self.input_dir):
            if file.lower().endswith(self.supported_formats):
                input_path = os.path.join(self.input_dir, file)
                output_filename = f"nobg_{file.rsplit('.', 1)[0]}.png"  # Save as PNG for transparency
                output_path = os.path.join(self.output_dir, output_filename)

                logger.info(f"Processing {input_path}")
                img = self.remove_background(input_path, background_color)
                if img:
                    try:
                        img.save(output_path, 'PNG')
                        logger.info(f"Saved output to {output_path}")
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to save {output_path}: {e}")
                        failed += 1
                else:
                    failed += 1

        print(f"\nProcessed {processed} images, {failed} failed. Check {log_file} for details.")
        logger.info(f"Completed processing: {processed} images processed, {failed} failed")

def run_background_removal():
    """Run background removal and log results."""
    input_dir = '~/Pictures/input'
    output_dir = '~/Pictures/output'
    # Optional: Set background_color to a tuple (R, G, B, A), e.g., (255, 255, 255, 255) for white
    background_color = None  # Set to None for transparent background
    remover = BackgroundRemover(input_dir, output_dir)
    remover.process_images(background_color)

def main():
    """Main function to schedule and run background removal."""
    try:
        logger.info("Starting background remover script")
        print("Starting background remover...")
        # Schedule background removal every 3 hours
        schedule.every(3).hours.do(run_background_removal)
        # Run first scan immediately
        run_background_removal()
        # Keep script running for scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Script stopped by user")
        print("Script stopped by user")
    except Exception as e:
        logger.error(f"Script error: {e}")
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
