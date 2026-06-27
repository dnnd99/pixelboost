from PIL import Image, ImageFilter
import numpy as np
import cv2
from modules.logger import logger
import time

class Upscaler:
    def __init__(self):
        self.supported_formats = ['jpg', 'jpeg', 'png']
        logger.info("Upscaler initialized")
    
    def upscale_image(self, image, scale=4, sharpen=True, use_ai=True):
        """
        Upscale image using either AI or traditional methods
        """
        try:
            start_time = time.time()
            
            if use_ai:
                # AI-based upscaling (placeholder for Real-ESRGAN)
                result = self._ai_upscale(image, scale)
            else:
                # Traditional upscaling
                result = self._traditional_upscale(image, scale)
            
            # Apply sharpening if requested
            if sharpen:
                result = self._apply_sharpen(result)
            
            logger.info(f"Upscaled image in {time.time() - start_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Upscale failed: {str(e)}")
            # Fallback to traditional upscaling
            return self._traditional_upscale(image, scale)
    
    def _ai_upscale(self, image, scale):
        """AI-based upscaling using Real-ESRGAN"""
        # Placeholder: In production, integrate Real-ESRGAN
        # For now, use traditional method as fallback
        return self._traditional_upscale(image, scale)
    
    def _traditional_upscale(self, image, scale):
        """Traditional Lanczos resampling"""
        width, height = image.size
        new_size = (int(width * scale), int(height * scale))
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def _apply_sharpen(self, image):
        """Apply unsharp mask sharpening"""
        return image.filter(
            ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)
        )
    
    def process_batch(self, images, scale=4, sharpen=True, use_ai=True):
        """Process multiple images"""
        results = []
        total = len(images)
        
        for idx, img_data in enumerate(images):
            try:
                logger.info(f"Processing {idx+1}/{total}")
                img = Image.open(img_data)
                
                # Upscale
                upscaled = self.upscale_image(img, scale, sharpen, use_ai)
                
                # Convert to RGB if needed
                if upscaled.mode in ('RGBA', 'LA', 'P'):
                    upscaled = upscaled.convert('RGB')
                
                results.append({
                    'original': img_data,
                    'upscaled': upscaled,
                    'original_size': img.size,
                    'new_size': upscaled.size
                })
                
            except Exception as e:
                logger.error(f"Error processing {img_data.name}: {str(e)}")
                continue
        
        return results
