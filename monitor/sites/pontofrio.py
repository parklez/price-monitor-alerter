from typing import Union
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import requests


SESSION = requests.Session()
SESSION.headers.update({'Connection': 'keep-alive',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'})
SESSION.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))


def convert_price(price: str) -> float:
    return float(price.replace('.', '').replace(',', '.'))


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

    price_start = r.text.find('id="product-price">R$ ')
    price_end = r.text.find('</p>', price_start)

    if price_start == -1 or price_end == -1:
        return None

    return convert_price(r.text[price_start+22:price_end])
