import json
import os

from typing import List, Dict

def load_urls_config(path: str) -> List[Dict[str, str]]:
    if os.stat(path).st_size == 0:
        raise ValueError(f'Config file "{path}" is empty.')

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f'Config file "{path}" contains invalid JSON: {e}')

    if not isinstance(data, list):
        raise TypeError('Config must be a JSON list (array) of objects.')

    if not data:
        raise ValueError('Config list is empty. Please add at least one URL.')

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise TypeError(f'Item at index {index} is not a dictionary.')

        if 'name' not in item or 'url' not in item:
            raise KeyError(f'Item at index {index} is missing required fields "name" or "url".')

        if not item['name'] or not item['url']:
            raise ValueError(f'Item at index {index} has empty "name" or "url".')

    return data
