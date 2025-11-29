from bs4 import BeautifulSoup

def parse_vacancies_count(html: str) -> int:
    soup = BeautifulSoup(html, 'html.parser')

    element = soup.find('span', class_='fs-1 fw-bold text-muted')

    if not element:
        raise ValueError('Could not find an element with the number of vacancies on the page')

    text_value = element.get_text(strip=True).replace(' ', '').replace('\xa0', '')

    if not text_value.isdigit():
        raise ValueError(f'The text found is not a number: {text_value}')

    return int(text_value)
