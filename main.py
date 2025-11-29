import sys
import logging
import requests

from requests.exceptions import RequestException

from src.config import Config
from src.bot import send_message
from src.parser import parse_vacancies_count
from src.sheets import get_worksheet, get_last_vacancies, add_vacancies

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_alert(text: str):
    try:
        full_text = f'ERROR IN SCRIPT\n\n{text}'
        if Config.BOT_TOKEN and Config.CHAT_ID:
            send_message(Config.BOT_TOKEN, Config.CHAT_ID, full_text)
    except Exception as e:
        logger.error(f'Failed to send alert to Telegram: {e}')

def main():
    logger.info('Script started')

    try:
        Config.validate()
    except ValueError as e:
        logger.critical(f'Config validation error: {e}')
        sys.exit(1)

    try:
        logger.info(f'Requesting URL: {Config.URL}')
        response = requests.get(Config.URL, timeout=10)
        response.raise_for_status()
    except RequestException as e:
        err_msg = f'Network error or Bad Status: {e}'
        logger.error(err_msg)
        send_alert(err_msg)
        return

    try:
        vacancies_now = parse_vacancies_count(response.text)
        logger.info(f'Parsed successfully: {vacancies_now} vacancies')
    except ValueError as e:
        err_msg = f'Parsing failed: {e}'
        logger.error(err_msg)
        send_alert(err_msg)
        return

    try:
        logger.info('Connecting to Google Sheets...')
        worksheet = get_worksheet(Config.CREDS_PATH, Config.SHEET_NAME)
        last_vacancies = get_last_vacancies(worksheet)

        add_vacancies(worksheet, vacancies_now)
        logger.info('Data saved to Google Sheets')
    except Exception as e:
        err_msg = f'Google Sheets error: {e}'
        logger.error(err_msg)
        send_alert(err_msg)
        return

    try:
        diff = vacancies_now - last_vacancies
        msg = f'Vacancies: {vacancies_now} ({diff:+} compared to yesterday)'

        send_message(Config.BOT_TOKEN, Config.CHAT_ID, msg)
        logger.info('Success message sent to Telegram')
    except Exception as e:
        logger.error(f'Failed to send final report: {e}')

    logger.info('Script finished successfully')

if __name__ == '__main__':
    main()
