import re
import io
import zipfile
from datetime import datetime
from PIL import Image
import os

class Utils:
    @staticmethod
    def clean_filename(name):
        """Clean filename for safe storage"""
        name = re.sub(r'[^a-z0-9\-]', '-', name.lower())
        name = re.sub(r'-+', '-', name).strip('-')
        return name[:80]
    
    @staticmethod
    def create_zip_from_images(images_data, filename_prefix="pixelboost"):
        """Create ZIP file from image data"""
        zip_buf = io.BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_name = f"{filename_prefix}_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for img_data in images_data:
                zf.writestr(img_data['filename'], img_data['data'])
        
        zip_buf.seek(0)
        return zip_buf, zip_name
    
    @staticmethod
    def get_image_size(img):
        """Get image dimensions safely"""
        if isinstance(img, Image.Image):
            return img.width, img.height
        return 0, 0
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def ensure_directory(path):
        """Create directory if it doesn't exist"""
        if not os.path.exists(path):
            os.makedirs(path)
        return path
