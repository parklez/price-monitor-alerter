import datetime
import time
from urllib.parse import urlparse
import pandas as pd

from monitor.sites.goimports import fetch_price as goimports_fetch_price
from monitor.sites.pontofrio import fetch_price as pontofrio_fetch_price
from monitor.sites.angeloni import fetch_price as angeloni_fetch_price
from monitor.sites.lg import fetch_price as lg_fetch_price
from monitor.utils.safe_writer import SafeWriter
from monitor.utils.telegram_notifier import telegram_send_message


CURRENT_TIME = time.strftime("%Y-%m-%d %H:%M:%S")

HISTORICAL_DATA_FILE = './prices.csv'
HISTORICAL_DF = pd.read_csv('./prices.csv', parse_dates=['time'])
HISTORICAL_PIVOT = HISTORICAL_DF.pivot(index='time', columns='product', values='price')

STRATEGY = {
    'www.goimports.com.br': goimports_fetch_price,
    'www.lg.com': lg_fetch_price,
    'www.angeloni.com.br': angeloni_fetch_price,
    'www.pontofrio.com.br': pontofrio_fetch_price
}


def write_price_to_csv(product: str, price: float, stream: SafeWriter) -> None:
    stream.write(f'{product},{CURRENT_TIME},{price}\n')


def scrape(product: dict, stream: SafeWriter) -> None:
    strategy = STRATEGY.get(urlparse(product['url']).hostname, None)
    if strategy is None:
        print(f'[INFO] Could not find strategy for {product["url"]}')
        return
    price = strategy(product['url'])
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
    diff = loc(round((previous_price/price - 1) * 100, 2))

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
