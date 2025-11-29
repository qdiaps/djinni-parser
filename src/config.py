import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN', default='')
    CHAT_ID = os.getenv('CHAT_ID', default='')
    URL = os.getenv('URL', default='')
    CREDS_PATH = os.getenv('CREDS_PATH', default='')
    SHEET_NAME = os.getenv('SHEET_NAME', default='')

    @classmethod
    def validate(cls):
        if not all([cls.BOT_TOKEN, cls.CHAT_ID, cls.URL, cls.CREDS_PATH, cls.SHEET_NAME]):
            raise ValueError('Mandatory environment variables are missing in .env')
