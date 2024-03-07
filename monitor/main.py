import json
import os
import threading
from monitor.utils.safe_writer import SafeWriter
from monitor.scraper import scrape


PRODUCTS = json.loads(os.environ.get('PRODUCTS', '[]'))


if __name__ == '__main__':
    if not os.path.isfile('./prices.csv'):
        with open('./prices.csv', 'w') as f:
            f.write('product,time,price\n')

    WRITER = SafeWriter('./prices.csv', 'a')
    threads = []
    for p in PRODUCTS:
        threads.append(threading.Thread(target=scrape,
                                        args=(p, WRITER)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    WRITER.close()
