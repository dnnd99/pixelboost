import csv
import io
from datetime import datetime
from config import Config
from modules.logger import logger

class MetadataProcessor:
    def __init__(self):
        self.category_map = Config.CATEGORY_MAP
        logger.info("Metadata Processor initialized")
    
    def create_adobe_csv(self, metadata_results):
        """Generate Adobe Stock compatible CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(["Filename", "Title", "Keywords", "Category", "Releases"])
        
        for item in metadata_results:
            if item.get("status") != "success":
                continue
                
            code = self.category_map.get(item.get("category", "Abstract"), "1")
            keywords = ", ".join(item.get("keywords", [])[:49]) if isinstance(item.get("keywords"), list) else ""
            
            writer.writerow([
                item.get("filename", ""),
                item.get("title", "")[:200],
                keywords,
                code,
                ""  # Releases field
            ])
        
        return output.getvalue()
    
    def validate_metadata(self, metadata):
        """Validate metadata format"""
        required_fields = ['title', 'description', 'keywords', 'category']
        for field in required_fields:
            if field not in metadata:
                return False, f"Missing field: {field}"
        
        if len(metadata['title']) > 70:
            return False, "Title exceeds 70 characters"
        
        if len(metadata['description']) > 150:
            return False, "Description exceeds 150 characters"
        
        return True, "Valid"
