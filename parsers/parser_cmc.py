import pandas as pd
import numpy as np
import requests
import json

from dateutil import parser
from helpers import helpers


def get_markets():
    response = requests.get("https://api.coinmarketcap.com/v1/ticker/")
    content = response.content
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    result = json.loads(content)
    df = pd.DataFrame.from_dict(result)
    df = df[['id', 'name']]
    df = df.sort_values(by='name')
    df = df.rename(index=str, columns={"id": "value", "name": "label"})
    df = df.to_dict('records')
    return df


class Historical(object):
    def __init__(self,
                 crypto='bitcoin',
                 start='20170101',
                 end=pd.Timestamp("today").strftime("%Y%m%d"),
                 rate="High",
                 is_test_data=False,
                 accent_color='blue'):
        self.crypto = crypto
        self.start = start
        self.end = end
        self.rate = rate  # Open / High / Low / Close
        self.is_test_data = is_test_data
        self.accent_color = accent_color

    ###########
    # Private #
    ###########

    def _get_historial_price_data(self):
        """ Get daily historical prices for a crypto over a specified time range

        :param crypto: name of crypto to get data from
        :param start: start date
        :param end: end date
        :return: dataframe [Date, Open, High, Low, Close, Volume, Market Cap]
        :return:
        """
        api_url = "https://coinmarketcap.com/currencies/{}/historical-data/?start={}&end={}".format(self.crypto,
                                                                                                    self.start,
                                                                                                    self.end)
        df = pd.read_html(api_url)[0]
        df['Date'] = [parser.parse(x) for x in df['Date']]

        return df

    def _get_historial_price_test_data(self):
        """ Get a dataframe with fake data, for testing purposes

        :return:
        df      : dataframe
        """
        date_range = {'Date': pd.date_range(start=self.start, end=self.end)}
        df = pd.DataFrame(date_range)
        df[self.rate] = np.random.randint(3, 20000, len(df))
        return df

    def _calculate_pct_change(self, df):
        """ Calculate the crypto's percentage change with years start

        :param df: dataframe

        :return:
        df      : dataframe
        """
        col_pct = helpers.get_price_value_pct(self.crypto)
        df[col_pct] = df.groupby(['year'])[self.rate].transform(lambda x: (x / x[len(x) - 1]))
        return df

    ###########
    # Public #
    ###########

    def get_cmc_historical_data(self):
        """ Get a workable dataframe containing the crypto date, price and percentage change values.

        :return:
        cmc_prices      : dataframe
        """
        cmc_prices = self._get_historial_price_test_data() if self.is_test_data else self._get_historial_price_data();
        cmc_prices = helpers.add_day_week_year_to_df(cmc_prices)
        cmc_prices = helpers.calculate_pct_change(cmc_prices, self.crypto, self.rate)
        return cmc_prices
