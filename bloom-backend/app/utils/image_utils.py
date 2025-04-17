import base64
from PIL import Image
import io
import time
import os

class ImageProcessor:
    @staticmethod
    def base64_to_image(image_base64):
        # Implementation from screenpipe.py image processing
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_data = base64.b64decode(image_base64)
        return Image.open(io.BytesIO(image_data))
    
    @staticmethod
    def save_temp_image(image):
        temp_path = f"temp_{int(time.time())}.png"
        image.save(temp_path)
        return temp_path