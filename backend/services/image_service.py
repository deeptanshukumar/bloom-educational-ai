import os
import tempfile
from typing import Optional
from werkzeug.datastructures import FileStorage
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

class ImageService:
    """Service for processing images, especially for math problems"""
    
    def __init__(self):
        # Initialize any necessary resources
        pass
    
    def extract_text_from_image(self, image_file: FileStorage) -> str:
        """
        Extract text from an image using Tesseract OCR
        """
        if not image_file:
            return ""
        
        try:
            # Save the file temporarily
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, image_file.filename)
            image_file.save(temp_path)
            
            # Open the image using PIL
            image = Image.open(temp_path)
            
            # Preprocess the image for better OCR results
            image = self._preprocess_image(image)
            
            # Perform OCR using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Cleanup
            os.remove(temp_path)
            
            return text.strip()  # Return the extracted text
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return ""
    
    def extract_math_expression(self, image_file: FileStorage) -> str:
        """
        Specialized function to extract math expressions from images
        """
        # For now, use the same OCR logic as extract_text_from_image
        # In a real implementation, you could use MathPix or a custom model
        return self.extract_text_from_image(image_file)
    
    def enhance_image_quality(self, image_file: FileStorage) -> bytes:
        """
        Enhance image quality for better OCR results
        """
        try:
            # Save the file temporarily
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, image_file.filename)
            image_file.save(temp_path)
            
            # Open the image using PIL
            image = Image.open(temp_path)
            
            # Apply preprocessing
            enhanced_image = self._preprocess_image(image)
            
            # Save the enhanced image to bytes
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            enhanced_image.save(temp_output.name, format="PNG")
            
            with open(temp_output.name, "rb") as f:
                enhanced_image_bytes = f.read()
            
            # Cleanup
            os.remove(temp_path)
            os.remove(temp_output.name)
            
            return enhanced_image_bytes
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return b""
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess the image for better OCR results
        """
        # Convert to grayscale
        image = image.convert("L")
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Apply a slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter())
        
        return image