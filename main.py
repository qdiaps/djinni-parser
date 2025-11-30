import sys
import time
import random
import logging
import requests

from requests.exceptions import RequestException
from datetime import datetime

from src.config import Config
from src.loader import load_urls_config
from src.bot import send_message
from src.parser import parse_vacancies_count
from src.sheets import get_worksheet, get_headers, validate_columns, save_results

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_alert(text: str) -> None:
    try:
        full_text = f'ERROR IN SCRIPT\n\n{text}'
        if Config.BOT_TOKEN and Config.CHAT_ID:
            send_message(Config.BOT_TOKEN, Config.CHAT_ID, full_text)
    except Exception as e:
        logger.error(f'Failed to send alert to Telegram: {e}')

def send_error(err_msg: str) -> None:
    logger.error(err_msg)
    send_alert(err_msg)

def main() -> None:
    logger.info('Script started')

    try:
        Config.validate()
    except (ValueError, FileNotFoundError) as e:
        logger.critical(f'Config validation error: {e}')
        sys.exit(1)

    try:
        urls_config = load_urls_config(Config.URLS_CONFIG_PATH)
        logger.info(f'Config loaded successfully. Found {len(urls_config)} items.')

        worksheet = get_worksheet(Config.CREDS_PATH, Config.SHEET_NAME)
        sheet_headers = get_headers(worksheet)
        validate_columns(worksheet, urls_config, Config.DATE_COLUMN_NAME, sheet_headers)
        logger.info('Spreadheet structure validated successfully.')
    except (ValueError, TypeError, KeyError) as e:
        send_error(f'URLs config validation error: {e}')
        return

    results = {}
    for item in urls_config:
        name = item['name']
        url = item['url']

        delay = random.uniform(5, 12)
        logger.info(f'Processing "{name}". Waiting {delay:.1f}s')
        time.sleep(delay)

        try:
            logger.info(f'Requesting URL: {url}')
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
        except RequestException as e:
            send_error(f'Network error or Bad Status: {e}')
            return

        try:
            count = parse_vacancies_count(response.text)
            results[name] = count
            logger.info(f'Parsed successfully: {count} vacancies')
        except ValueError as e:
            send_error(f'Parsing failed: {e}')
            return

    try:
        save_results(worksheet, results, Config.DATE_COLUMN_NAME, sheet_headers)
        logger.info('Data saved to Google Sheets')
    except ValueError as e:
        send_error(f'Saving failed: {e}')

    try:
        date = datetime.now().strftime('%d.%m.%Y')
        msg_lines = [f'📊 Daily Report | {date}']
        for name, count in results.items():
            msg_lines.append(f'{name}: {count}')

        send_message(Config.BOT_TOKEN, Config.CHAT_ID, '\n'.join(msg_lines))
        logger.info('Success message sent to Telegram')
    except Exception as e:
        logger.error(f'Failed to send final report: {e}')

    logger.info('Script finished successfully')

if __name__ == '__main__':
    main()
