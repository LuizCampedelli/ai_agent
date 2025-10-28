import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()

        # Google Gemini
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_model = os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')

        # Fallbacks
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # App config
        self.environment = os.getenv('APP_ENVIRONMENT', 'development')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        # Feature detection
        self.gemini_available = bool(self.google_api_key)

    def get_gemini_config(self):
        """Get Gemini configuration"""
        if not self.google_api_key:
            return None

        return {
            'provider': 'google',
            'model': self.google_model,
            'api_key': self.google_api_key
        }

    def get_llm_config(self):
        """Get LLM configuration with Gemini as priority"""
        # Priority: Gemini → Groq → OpenAI → Local
        if self.google_api_key:
            return self.get_gemini_config()
        elif self.groq_api_key:
            return {
                'provider': 'groq',
                'model': 'llama3-70b-8192',
                'api_key': self.groq_api_key
            }
        elif self.openai_api_key:
            return {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'api_key': self.openai_api_key
            }
        else:
            return {
                'provider': 'local',
                'model': 'crewai/default',
                'api_key': None
            }

config = Config()