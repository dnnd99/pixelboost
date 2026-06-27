import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Model paths
    MODEL_DIR = "models/realesrgan"
    CHECKPOINT_DIR = "models/checkpoints"
    
    # Output directories
    OUTPUT_DIR = "output"
    TEMP_DIR = "temp"
    CACHE_DIR = "cache"
    ASSETS_DIR = "assets"
    
    # Default settings
    DEFAULT_SCALE = 4
    DEFAULT_FORMAT = "PNG"
    DEFAULT_SHARPEN = True
    DEFAULT_LANGUAGE = "English"
    DEFAULT_MAX_KEYWORDS = 30
    DEFAULT_MEDIA_TYPE = "Photo"
    
    # Adobe Stock categories
    CATEGORY_MAP = {
        "Abstract": "1", "Animals/Wildlife": "2", "Arts/Entertainment": "3",
        "Backgrounds/Textures": "4", "Beauty/Fashion": "5", "Buildings/Landmarks": "6",
        "Business/Finance": "7", "Education": "8", "Food/Drink": "9",
        "Healthcare/Medical": "10", "Holidays": "11", "Industrial": "12",
        "Landscapes": "13", "Lifestyle": "14", "Nature": "15",
        "Objects": "16", "People": "17", "Religion": "18",
        "Science": "19", "Sports/Recreation": "20", "Technology": "21",
        "Transportation": "22", "Travel": "23"
    }
    
    # Quality settings
    JPEG_QUALITY = 90
    PNG_COMPRESS_LEVEL = 6
    
    # Processing limits
    MAX_BATCH_SIZE = 10
    MAX_KEYWORDS = 50
    
    # Upscale limits
    MIN_SCALE = 2
    MAX_SCALE = 8
    
    # ADS URL
    SPONSOR_URL = "https://www.effectivecpmnetwork.com/hetg54us4?key=052b147073a8a1411c3b8815ecc9fa2e"
