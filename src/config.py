import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN', default='')
    CHAT_ID = os.getenv('CHAT_ID', default='')
    CREDS_PATH = os.getenv('CREDS_PATH', default='creds.json')
    SHEET_NAME = os.getenv('SHEET_NAME', default='')
    DATE_COLUMN_NAME = os.getenv('DATE_COLUMN_NAME', default='Date')
    URLS_CONFIG_PATH = os.getenv('URLS_CONFIG_PATH', default='config.json')

    @classmethod
    def validate(cls):
        if not all([cls.BOT_TOKEN, cls.CHAT_ID, cls.CREDS_PATH, cls.SHEET_NAME,
            cls.DATE_COLUMN_NAME, cls.URLS_CONFIG_PATH]):
            raise ValueError('Mandatory environment variables are missing in .env')

        if not os.path.exists(cls.CREDS_PATH):
            raise FileNotFoundError(f'Credentials file not found at: {cls.CREDS_PATH}')

        if not os.path.exists(cls.URLS_CONFIG_PATH):
            raise FileNotFoundError(f'URLs config file not found at: {cls.URLS_CONFIG_PATH}')
