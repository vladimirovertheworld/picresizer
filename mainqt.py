import argparse
import os
import logging
import sys
from PyQt6.QtWidgets import (QApplication, QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QSpinBox, QComboBox, QCheckBox, QMessageBox)
from PyQt6.QtGui import QPixmap
from PIL import Image
from PIL.ExifTags import TAGS
import cairosvg

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"}

def get_image_metadata(image_path):
    """Extract metadata from an image file, including EXIF data, ICC profiles, DPI, bit depth, and color profile."""
    try:
        if image_path.lower().endswith(".svg"):
            return {"Format": "SVG", "Message": "Vector image - no raster metadata available."}
        
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
        
        # Extract image mode, format, and resolution
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = image.size  # (width, height)
        metadata["DPI"] = image.info.get("dpi", "Unknown")
        metadata["Bit Depth"] = image.mode if image.mode in ("1", "L", "P") else "8-bit or higher"
        
        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata: {e}")
        return {}

def convert_svg_to_png(input_path, output_path):
    """Convert an SVG file to PNG format."""
    try:
        cairosvg.svg2png(url=input_path, write_to=output_path)
        return output_path
    except Exception as e:
        logging.error(f"Error converting SVG: {e}")
        return None

class ImageResizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Image Resizer")
        layout = QVBoxLayout()
        
        # Image preview
        self.image_label = QLabel("No Image Selected")
        layout.addWidget(self.image_label)
        
        # Image selection button
        self.button = QPushButton("Choose Image")
        self.button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.button)
        
        # Width and Height inputs
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setPrefix("Width: ")
        size_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setPrefix("Height: ")
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpeg", "png", "gif", "bmp", "tiff", "webp"])
        layout.addWidget(self.format_combo)
        
        # Quality selection
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(95)
        self.quality_spin.setPrefix("Quality: ")
        layout.addWidget(self.quality_spin)
        
        # Optimization and Upscaling options
        self.optimize_check = QCheckBox("Optimize Image")
        layout.addWidget(self.optimize_check)
        
        self.upscale_check = QCheckBox("Allow Upscaling")
        layout.addWidget(self.upscale_check)
        
        # Resize Button
        self.resize_button = QPushButton("Resize and Save")
        self.resize_button.clicked.connect(self.resize_image)
        layout.addWidget(self.resize_button)
        
        self.setLayout(layout)
    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.svg)")
        if file_path:
            self.image_label.setText(f"Selected: {file_path}")
            self.selected_image = file_path
    
    def resize_image(self):
        if not hasattr(self, 'selected_image'):
            QMessageBox.warning(self, "Error", "No Image Selected")
            return
        
        output_path = f"resized_{os.path.basename(self.selected_image)}"
        size = (self.width_spin.value(), self.height_spin.value())
        output_format = self.format_combo.currentText()
        
        if self.selected_image.lower().endswith(".svg"):
            converted_path = convert_svg_to_png(self.selected_image, output_path.replace(".svg", ".png"))
            if converted_path:
                QMessageBox.information(self, "Success", f"SVG converted and saved as {converted_path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to convert SVG")
            return
        
        try:
            img = Image.open(self.selected_image)
            img = img.resize(size, Image.LANCZOS)
            img.save(output_path, format=output_format.upper())
            QMessageBox.information(self, "Success", f"Image saved as {output_path}")
        except Exception as e:
            logging.error(f"Error resizing image: {e}")
            QMessageBox.warning(self, "Error", "Failed to resize image")


def main():
    app = QApplication(sys.argv)
    ex = ImageResizerApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()