import gspread

from gspread import Worksheet
from datetime import datetime
from typing import List, Dict

def get_worksheet(creds_path: str, sheet_name: str) -> Worksheet:
    gc = gspread.service_account(filename=creds_path)
    sh = gc.open(sheet_name)
    return sh.sheet1

def get_headers(worksheet: Worksheet) -> list[str]:
    return worksheet.row_values(1)

def validate_columns(worksheet: Worksheet, config_data: List[Dict], date_col_name: str, sheet_headers: list[str]) -> None:
    expected_headers = [date_col_name] + [item['name'] for item in config_data]

    sheet_headers_set = set(sheet_headers)
    expected_headers_set = set(expected_headers)

    missing = expected_headers_set - sheet_headers_set
    if missing:
        raise ValueError(f'Spreadsheet is missing columns required by config: {missing}')

    extra = sheet_headers_set - expected_headers_set
    if extra:
        raise ValueError(f'Spreadsheet has extra columns not defined in config: {extra}')

def save_results(worksheet: Worksheet, results: Dict[str, int], date_col_name: str, headers: list[str]) -> None:
    row = [''] * len(headers)

    if date_col_name in headers:
        date_index = headers.index(date_col_name)
        row[date_index] = datetime.now().strftime('%d.%m.%Y')
    else:
        raise ValueError(f'Date column "{date_col_name}" not found during save.')

    for name, count in results.items():
        if name in headers:
            index = headers.index(name)
            row[index] = count

    worksheet.append_row(row)
