import threading
import requests
import time
import json
import os

import pandas as pd

from dateutil import parser
from helpers import helpers
from queue import Queue

DATA_DIR = 'data'               # Folder to store the markets.csv and daily crypto prices csvs, could be an issue when a coin is called markets..
MARKETS_FILE = 'markets.csv'    # File which contains crypto names on coinmarketcap,


###########
# Markets #
###########

def get_and_save_markets_data():
    """ Downloads the market pairs available on coinmarketscap and save the result a csv in DATA_DIR/MARKETS_FILE

    """

    try:
        response = requests.get("https://api.coinmarketcap.com/v1/ticker/")
    except:
        return

    content = response.content
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    result = json.loads(content)
    df = pd.DataFrame.from_dict(result)
    df = df[['id', 'name']]
    df = df.sort_values(by='name')
    df = df.rename(index=str, columns={"id": "value", "name": "label"})
    df.to_csv(os.path.join(DATA_DIR, MARKETS_FILE), sep=',', index=False)


###########
# Cryptos #
###########

q = Queue()

def worker():
    while True:
        crypto = q.get()
        prepare_crypto_parsing(crypto)
        q.task_done()


def get_and_save_crypto_price_data():
    # Create the queue and thread pool.
    markets = helpers.get_markets_file()
    for market in markets:
        q.put(market['value'])

    for i in range(10):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()


def prepare_crypto_parsing(crypto):
    """ Get daily historical prices for a crypto over a specified time range

    :param crypto: name of crypto to get data from
    :return: dataframe [Date, Open, High, Low, Close, Volume, Market Cap]
    :return:
    """

    fileout = os.path.join(DATA_DIR, '{}.csv'.format(crypto))
    parse_start_time = time.time()

    # when crypto file does not exist download it
    if not os.path.isfile(fileout):
        get_and_save_crypto_data(crypto, fileout)

    # when old crypto file download it
    if not helpers.is_modified_today(fileout):
        get_and_save_crypto_data(crypto, fileout)

    print('Got {} it took {:0.2f} seconds'.format(crypto, (time.time() - parse_start_time)))


def get_and_save_crypto_data(crypto, fileout):
    start = '20010101'
    end = pd.Timestamp("today").strftime("%Y%m%d")
    api_url = "https://coinmarketcap.com/currencies/{}/historical-data/?start={}&end={}".format(crypto, start, end)
    df = pd.read_html(api_url)[0]
    df['Date'] = [parser.parse(x) for x in df['Date']]

    df.to_csv(fileout, sep=',', index=False)


