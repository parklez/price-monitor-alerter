import datetime
import time
from typing import Union
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from monitor.utils.safe_writer import SafeWriter
from monitor.utils.telegram_notifier import telegram_send_message


SESSION = requests.Session()
SESSION.headers.update({'Connection': 'keep-alive'})
SESSION.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))


CURRENT_TIME = time.strftime("%Y-%m-%d %H:%M:%S")

HISTORICAL_DATA_FILE = './prices.csv'
HISTORICAL_DF = pd.read_csv('./prices.csv', parse_dates=['time'])
HISTORICAL_PIVOT = HISTORICAL_DF.pivot(index='time', columns='product', values='price')


def fetch_price(url: str) -> Union[float, None]:
    """
    Fetches the price from the given URL.

    Parameters:
        url (str): The URL to fetch the price from.

    Returns:
        Union[float, None]: The fetched price as a float, or None if the request fails or the price is not found.
    """
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
    """
    Convert the price from a string to a float.

    Args:
        price (str): The price as a string.

    Returns:
        float: The price as a float.
    """
    return float(price.replace('.', '').replace(',', '.'))


def write_price_to_csv(product: str, price: float, stream: SafeWriter) -> None:
    stream.write(f'{product},{CURRENT_TIME},{price}\n')


def scrape(product: dict, stream: SafeWriter) -> None:
    price = fetch_price(product['url'])
    name = product['product_name']

    if not price:
        print(f'[INFO] Could not fetch price for {name}!')
        return
    if name not in HISTORICAL_PIVOT.columns:
        print(f'[INFO] First entry for {name} -\t R$: {price}')
    elif price == HISTORICAL_PIVOT[name].dropna().iloc[-1]:
        print(f'[INFO] Price unchanged: {name} -\t R$: {price}')
        return

    send_alerts(product, price)
    print(f'[INFO] Writing price to CSV: {name} -\t R$: {price}')
    write_price_to_csv(name, price, stream)


def localize_price(price: float) -> str:
    # Github Actions does not have this locale installed
    # locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')
    # return locale.currency(price, symbol=False, grouping=True)
    return f'{price:,.2f}'


def send_alerts(product: dict, price: float) -> None:
    name = product['product_name']
    if name not in HISTORICAL_PIVOT.columns:
        return
    previous_price = HISTORICAL_PIVOT[name].dropna().iloc[-1]
    if price > previous_price:
        print(f'[INFO] Price increased: {name} -\t R$: {price}')
        return

    median_price = HISTORICAL_PIVOT[name].median()
    lowest_recorded_price = HISTORICAL_PIVOT[name].min()
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=40)
    lowest_price_in_40_days = HISTORICAL_PIVOT[name].loc[start_date:now].min()
    if lowest_price_in_40_days == float('nan'):
        lowest_price_in_40_days = HISTORICAL_PIVOT[name].min()

    loc = localize_price
    diff = loc(round((previous_price/now - 1) * 100, 2))

    text = ""
    text = f'💸 {name} is now R$: {loc(price)}! 💸'
    text += f'\n📉 Discount: -{loc(previous_price-price)} BRL ({diff}%)'
    text += '\n\n```'
    text += '\n-----------------------------------'
    text += f'\nPrevious price: R$: {loc(previous_price)}'
    text += f'\nCheapest record: R$: {loc(lowest_recorded_price)}'
    text += f'\nLowest in 40 days: R$: {loc(lowest_price_in_40_days)}'
    text += f'\nMedian: R$: {loc(median_price)}'
    text += '\n-----------------------------------```'
    text += f'\n{product["url"]}'

    for person in product['alerts']['telegram']:
        print(f'[INFO] Sending Telegram message to {person}')
        telegram_send_message(text, person)
