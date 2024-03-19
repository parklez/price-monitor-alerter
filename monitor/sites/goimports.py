from typing import Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


SESSION = requests.Session()
SESSION.headers.update({'Connection': 'keep-alive'})
SESSION.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))


def fetch_price(url: str) -> Union[float, None]:
    print('[INFO] Fetching price from: ' + url)
    try:
        r = SESSION.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    if r.status_code != 200:
        print(f"Request failed with status code {r.status_code}")
        return None

    for line in r.text.splitlines():
        line = line.strip()
        if line.startswith('<h2 class="price">R$ '):
            return convert_price(line.split()[2])
    return None


def convert_price(price: str) -> float:
    return float(price.replace('.', '').replace(',', '.'))
