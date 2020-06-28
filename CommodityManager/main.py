#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:31:15 2018

@author: davesmith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
from datetime import datetime, timedelta
import logging
import time
# from threading import Timer,Thread,Event

# Third party modules
import pandas as pd
import requests

from xml.etree import ElementTree

# Custom modules
import database_handler as db
import chart_drawing as cd


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

LOGGER = logging.getLogger(' GWR Engine')

# Directory locations
CHART_DIR = "/home/davesmith/Documents/Personal/Python/CommodityManager/charts/"

# Web connection consts
LOGIN_REQUEST = "https://www.bullionvault.com/secure/login.do"
LOGIN_REPLY = 'https://www.bullionvault.com/secure/j_security_check?'
USERNAME_AND_PASSWORD = {'j_username': 'DAVESMITH',
                         'j_password': 'W3G0tS0w3ll'}
VIEW_MARKET = 'https://www.bullionvault.com/secure/api/v2/view_market_xml.do'

# Markets
GOLD_LOCATIONS = ('AUXZU', 'AUXLN', 'AUXNY', 'AUXTR', 'AUXSG')
CURRENCIES = ('USD', 'GBP', 'EUR', 'YEN')

START = 1
STABLE_MARKET = 2
VOLATILE_MARKET = 3
FINISHED = 4


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes


class Market():

    def __init__(self, location, currency):

        self.location = location
        self.currency = currency
        self.raw_df = None
        self.stats_df = None

    def add_stats(self):
        self.buy_limit_mean = self.raw_df['buy_limit'].mean()
        self.buy_limit_mode = self.raw_df['buy_limit'].mode()[0]
        self.buy_limit_std = self.raw_df['buy_limit'].std()

        self.buy_quantity_mean = self.raw_df['buy_quantity'].mean()
        self.buy_quantity_mode = self.raw_df['buy_quantity'].mode()[0]
        self.buy_quantity_std = self.raw_df['buy_quantity'].std()

        self.sell_limit_mean = self.raw_df['sell_limit'].mean()
        self.sell_limit_mode = self.raw_df['sell_limit'].mode()[0]
        self.sell_limit_std = self.raw_df['sell_limit'].std()

        self.sell_quantity_mean = self.raw_df['sell_quantity'].mean()
        self.sell_quantity_mode = self.raw_df['sell_quantity'].mode()[0]
        self.sell_quantity_std = self.raw_df['sell_quantity'].std()
        pass


class Event():

    def __init__():

        pass



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


def get_market_prices(session):
    time_start = time.time()
    response = session.get(VIEW_MARKET)
    time_response = time.time()

    root = ElementTree.fromstring(response.content)

    markets = []
    timestamp = datetime.now()

    # parse_xml_response
    for name in root.iter():
        if (name.attrib != {}):
            # print(name.attrib)

            commodity = name.attrib.get("securityClassNarrative", None)
            location = name.attrib.get("securityId", None)
            currency = name.attrib.get("considerationCurrency", None)

            if commodity == 'GOLD':
                markets.append(db.GoldMarket())
                markets[-1].update_info(timestamp, location, currency)

            direction = name.attrib.get("actionIndicator", None)
            quantity = float(name.attrib.get("quantity", 0.0))
            limit = int(name.attrib.get("limit", 0))

            if direction == 'B':
                markets[-1].update_buy(quantity, limit)

            elif direction == 'S':
                markets[-1].update_sell(quantity, limit)


    for market in markets:
        db.insert(market)

    time_save_to_db = time.time()
    rows = db.info(db.GoldMarket)

    print("Database size:" + str(rows),
          "Time total = %.1f ms" % ((time_save_to_db - time_start) * 1000),
          "response = %.1f ms" % ((time_response - time_start) * 1000),
          "ET = %.1f ms" % ((time_save_to_db - time_response) * 1000))


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

def main():
    '''

    '''
    markets = []

    # Populate the market objects into a list
    for gold_loc in GOLD_LOCATIONS:
        for currency in CURRENCIES:
            if gold_loc != 'AUXTR' and currency != 'YEN':
                markets.append(Market(gold_loc, currency))

    db.create_database()

    # Find the time frame we have data for
    time_in_db = db.first_row(db.GoldMarket)

    for market in markets:

        # Otherwise we have raw data that need processing
        market.raw_df = db.to_pandas(db.GoldMarket, time_in_db,
                                     datetime.now(),
                                     market.location, market.currency)

        market.raw_df.to_csv("/home/davesmith/Documents/Personal/Python/CommodityManager/csv/market.csv")
        print(market.raw_df.info())

        start_index = 0
        bollinger_high = market.raw_df['buy_limit'][0]
        bollinger_low = market.raw_df['buy_limit'][0]

        inside_bolinger = False
        state = START

        for index, row in market.raw_df.iterrows():

            if state == START:
                std = market.raw_df['buy_limit'].iloc[start_index:index].std()
                mean = market.raw_df['buy_limit'].iloc[start_index:index].mean()

                bollinger_high = mean + (std * 4)
                bollinger_low = mean - (std * 4)

                if index > start_index + 100:
                    state = STABLE_MARKET

            elif state == STABLE_MARKET:
                if row['buy_limit'] > bollinger_high or row['buy_limit'] < bollinger_low:

                    print(index, "Boll high", row['buy_limit'], bollinger_high, std)
                    start_index = index
                    state = VOLATILE_MARKET

                else:
                    #print("Boll high", row['buy_limit'], bollinger_high, std, index)

                    std = market.raw_df['buy_limit'].iloc[start_index:index].std()
                    mean = market.raw_df['buy_limit'].iloc[start_index:index].mean()

                    bollinger_high = mean + (std * 4)
                    bollinger_low = mean - (std * 4)

            elif state == VOLATILE_MARKET:
                if index > start_index + 5:
                    vol_std = market.raw_df['buy_limit'].iloc[start_index:index].std()

                    if vol_std < std:
                        print(index, "vol std", vol_std, "std", std)
                        start_index = index
                        state = STABLE_MARKET


            elif state == FINISHED:
                pass







    # Fill the database
    with requests.session() as session:
        # fetch the login page and send back the login details
        session.get(LOGIN_REQUEST)
        r = session.post(LOGIN_REPLY, data=USERNAME_AND_PASSWORD)

        # Get the market info every 5 seconds and add to a database
        timer = time.time()

        while (True):
            if time.time() > (timer+5):
                timer = time.time()

                # Try get the market info. If the connection is closed then
                # re-establish
                try:
                    get_market_prices(session)

                except Exception as e:
                    print(e)

                    # fetch the login page and send back the login details
                    session.get(LOGIN_REQUEST)
                    r = session.post(LOGIN_REPLY, data=USERNAME_AND_PASSWORD)


if __name__ == "__main__":
    '''

    '''
    main()

    markets = []

    # Populate the market objects into a list
    for gold_loc in GOLD_LOCATIONS:
        for currency in CURRENCIES:
            if gold_loc != 'AUXTR' and currency != 'YEN':
                markets.append(Market(gold_loc, currency))

    db.create_database()

    # debug function
    # db.delete(db.GoldFeaturesDaily)

    # Find the time frame we have data for
    time_in_db = db.first_row(db.GoldMarket)
    time_in_db = time_in_db.replace(hour=0, minute=0, second=0, microsecond=0)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Cycle through all the raw data and process if needed
    while time_in_db < today:
        for market in markets:

            # We already have features for this day so move along to the nex step
            if db.info(db.GoldFeaturesDaily, ts=time_in_db,
                       location=market.location, currency=market.currency):
                print("Already have features for", time_in_db,
                      market.location, market.currency)
                time_in_db = time_in_db + timedelta(days=1)
                continue

            print("No features for", time_in_db, market.location, market.currency)

            # Otherwise we have raw data that need processing
            market.raw_df = db.to_pandas(db.GoldMarket, time_in_db,
                                           time_in_db + timedelta(days=1),
                                           market.location, market.currency)

            # If we have stuff in the dataframe, then save it to the database
            if len(market.raw_df) != 0:
                db.insert(db.GoldFeaturesDaily(time_in_db, market.location,
                                               market.currency, market.raw_df))
            else:
                print("Dataframe empty")

            market.raw_df = None
            # time.sleep(1)

        time_in_db = time_in_db + timedelta(days=1)

    for market in markets:
        # Load all the statistics into a dataframe and chart it
        market.stats_df = db.to_pandas(db.GoldFeaturesDaily,
                                       db.first_row(db.GoldFeaturesDaily),
                                       datetime.now().replace(
                                               hour=0, minute=0, second=0,
                                               microsecond=0),
                                       market.location, market.currency)

        #print(market.stats_df)
        '''
        cd.duelAxesLineChart(market.location + " " + market.currency,
                             market.stats_df['timestamp'],
                             market.stats_df['buy_limit_mean'],
                             market.stats_df['buy_limit_std'],
                             "Date", "Price", "Price",
                             'r','g',
                             CHART_DIR + market.location + "_" + market.currency +".png")

        cd.singleAxesLineChart(
                market.location + " " + market.currency, "Date", "Price",
                CHART_DIR + "LDN_GBP_price.png",
                "Day",
                market.stats_df['timestamp'],
                market.stats_df['buy_limit_mean'],
                "r",
                market.stats_df['timestamp'],
                market.stats_df['buy_limit_std'], "g")
        '''
            #stats_df['timestamp'], stats_df['buy_limit_std'], "b")

    # Fill the database
    with requests.session() as session:
        # fetch the login page and send back the login details
        session.get(LOGIN_REQUEST)
        r = session.post(LOGIN_REPLY, data=USERNAME_AND_PASSWORD)

        # Get the market info every 5 seconds and add to a database
        timer = time.time()

        while (True):
            if time.time() > (timer+5):
                timer = time.time()

                # Try get the market info. If the connection is closed then
                # re-establish
                try:
                    get_market_prices(session)

                except Exception as e:
                    print(e)

                    # fetch the login page and send back the login details
                    session.get(LOGIN_REQUEST)
                    r = session.post(LOGIN_REPLY, data=USERNAME_AND_PASSWORD)
