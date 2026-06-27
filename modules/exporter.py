import io
from PIL import Image
from modules.logger import logger
from config import Config

class Exporter:
    def __init__(self):
        self.jpeg_quality = Config.JPEG_QUALITY
        self.png_compress = Config.PNG_COMPRESS_LEVEL
        logger.info("Exporter initialized")
    
    def export_image(self, image, format_type="PNG", optimize=True):
        """Export image to bytes"""
        try:
            buf = io.BytesIO()
            
            if format_type.upper() == "PNG":
                image.save(
                    buf,
                    format='PNG',
                    optimize=optimize,
                    compress_level=self.png_compress
                )
                ext = ".png"
            else:  # JPEG
                # Convert to RGB for JPEG
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                image.save(
                    buf,
                    format='JPEG',
                    quality=self.jpeg_quality,
                    optimize=optimize
                )
                ext = ".jpg"
            
            buf.seek(0)
            return buf, ext
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return None, None
    
    def prepare_export_data(self, images, format_type="PNG", scale=4):
        """Prepare images for batch export"""
        export_data = []
        
        for img_data in images:
            filename = img_data.get('filename', 'image')
            image = img_data.get('image')
            
            if not image:
                continue
            
            # Export image
            buf, ext = self.export_image(image, format_type)
            if buf:
                export_data.append({
                    'filename': f"{filename}_{scale}x{ext}",
                    'data': buf.getvalue()
                })
        
        return export_data
