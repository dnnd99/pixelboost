import google.generativeai as genai
import json
import re
from modules.logger import logger
from config import Config

class AIVision:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-lite")
            logger.info("AI Vision initialized")
    
    def is_available(self):
        return self.model is not None
    
    def generate_metadata(self, filename, media_type="Photo", language="English", max_keywords=30):
        """
        Generate metadata using Gemini AI
        """
        if not self.is_available():
            logger.error("AI Vision not available")
            return None
        
        try:
            prompt = self._build_prompt(filename, media_type, language, max_keywords)
            response = self.model.generate_content(prompt)
            
            # Clean response
            text = re.sub(r'```json|```', '', response.text.strip())
            data = json.loads(text)
            
            return {
                "filename": filename,
                "media_type": media_type,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "keywords": data.get("keywords", []),
                "category": data.get("category", "Abstract"),
                "language": language,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {str(e)}")
            return {
                "filename": filename,
                "status": f"error: {str(e)[:30]}"
            }
    
    def _build_prompt(self, filename, media_type, language, max_keywords):
        """Build prompt for Gemini"""
        return f"""Generate metadata for Adobe Stock based on filename: "{filename}"
Media type: {media_type}
Language: {language}
Max keywords: {max_keywords}

Return JSON only:
{{
  "title": "descriptive title max 70 chars",
  "description": "compelling description max 150 chars",
  "keywords": [{max_keywords} keywords in {language}],
  "category": "Abstract, Animals, Arts, Backgrounds, Beauty, Buildings, Business, Education, Food, Healthcare, Holidays, Industrial, Landscapes, Lifestyle, Nature, Objects, People, Religion, Science, Sports, Technology, Transportation, Travel"
}}"""
