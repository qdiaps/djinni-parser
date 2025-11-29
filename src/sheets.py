import gspread

from gspread import Worksheet
from datetime import datetime

def get_worksheet(creds_path: str, sheet_name: str) -> Worksheet:
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open(sheet_name)
    return sh.sheet1

def get_last_vacancies(worksheet: Worksheet) -> int:
    data = worksheet.get_all_values()

    if len(data) < 2:
        return 0

    try:
        last_value = data[-1][1]
        return int(str(last_value).replace(' ', ''))
    except (ValueError, IndexError):
        return 0

def add_vacancies(worksheet: Worksheet, vacancies: int) -> None:
    date = datetime.now().strftime('%d.%m.%Y')
    worksheet.append_row([date, vacancies])
