import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings
from typing import Optional

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Telegram Bot settings
    TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN', '')
    
    # Kaggle settings
    KAGGLE_USERNAME: str = os.getenv('KAGGLE_USERNAME', '')
    KAGGLE_KEY: str = os.getenv('KAGGLE_KEY', '')
    KAGGLE_NOTEBOOK_URL: str = os.getenv('KAGGLE_NOTEBOOK_URL', '')
    
    # GitHub settings
    GITHUB_TOKEN: Optional[str] = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO: Optional[str] = os.getenv('GITHUB_REPO')
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    WORKFLOWS_DIR: Path = BASE_DIR / 'workflows'
    LOGS_DIR: Path = BASE_DIR / 'logs'
    
    # Create necessary directories
    def create_directories(self):
        self.WORKFLOWS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create global settings instance
settings = Settings()
settings.create_directories()
