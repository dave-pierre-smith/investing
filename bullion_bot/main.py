

#%% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

import time
import requests
import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd
import datetime
import time
import os
import plotly
from collections import defaultdict


#%% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

URL_LOGIN = "https://www.bullionvault.com/secure/login.do"
URL_MARKETS = "https://www.bullionvault.com/secure/api/v2/view_market_xml.do"
URL_MARKETS_OLD = "https://www.bullionvault.com/view_market_xml.do"


#%% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

class Connection:

    def __init__(self):
        pass


class Market:

    def __init__(self, a_market_info):
        #self.time = datetime.datetime.utcnow()
        self.time = round(time.time(), 1)
        self.metal = a_market_info['securityClassNarrative']
        self.currency = a_market_info['considerationCurrency']
        self.location = a_market_info['securityId']

        self.buy_price = None
        self.buy_quantity = None
        self.sell_price = None
        self.sell_quantity = None

    def __str__(self):
        return "Time: {}, Market: {}, Currency: {}, Buy Price: {}, Sell Price: {}".format(self.time, self.location, self.currency, self.buy_price, self.sell_price)

    def add_price(self, a_price_info):

        if a_price_info['actionIndicator'] == "B":
            self.buy_price = a_price_info['limit']
            self.buy_quantity = a_price_info['quantity']

        elif a_price_info['actionIndicator'] == "S":
            self.sell_price = a_price_info['limit']
            self.sell_quantity = a_price_info['quantity']

    def to_dict(self):
        _return = {}

        _return['unixtime'] = self.time
        _return['location'] = self.location
        _return['currency'] = self.currency
        _return['buy_price'] = self.buy_price
        _return['buy_quantity'] = self.buy_quantity
        _return['sell_price'] = self.sell_price
        _return['sell_quantity'] = self.sell_quantity

        return _return

class Position:

    def __init__(self):
        pass

#%% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


def etree_to_dict(t):

    d = {t.tag: {} if t.attrib else None}

    children = list(t)

    if children:
        dd = defaultdict(list)

        for dc in map(etree_to_dict, children):

            for k, v in dc.items():
                dd[k].append(v)

        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}

    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())

    if t.text:
        text = t.text.strip()

        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text

        else:
            d[t.tag] = text
            
    return d


def make_url_request(a_url):
    # sending get request and saving the response as response object
    r = requests.get(url=URL_MARKETS_OLD)
    root = etree.fromstring(r.text)


    _return = etree_to_dict(root)
    print(_return)

    return root

#%% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

if __name__ == "__main__":

    # If we have market data then load it in
    if os.path.isfile("market_data.csv"):
        _master_df = pd.read_csv("market_data.csv")

    else:
        _master_df = pd.DataFrame()


    while True:
        _markets = []

        _reply = make_url_request(URL_MARKETS_OLD)



        # sending get request and saving the response as response object
        #r = requests.get(url=URL_MARKETS_OLD)
        #root = etree.fromstring(r.text)

        # Parse over the data in the reply
        for child in root.iter():

            if child.tag == "pitch":
                _markets.append(Market(child.attrib))

            if child.tag == "price":
                _markets[-1].add_price(child.attrib)

        _list = []

        for _market in _markets:
            _list.append(_market.to_dict())
            #print(_market)

        _df = pd.DataFrame(_list)
        _df = _df.set_index("unixtime")

        _master_df = pd.concat([_master_df, _df], sort=True)
        _master_df.to_csv("market_data.csv")

        time.sleep(5)


