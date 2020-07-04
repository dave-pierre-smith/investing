#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:31:15 2018

@author: davesmith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import argparse
from datetime import datetime, timedelta
import logging
import time
# from threading import Timer,Thread,Event
import threading
import os

# Third party modules
import pandas as pd
import requests

from xml.etree import ElementTree

# Custom modules
import database_handler as db
import chart_drawing as cd
import bullion_vault as bv
import gold_markets as gm


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

# LOGGER = logging.getLogger()
logger = logging.getLogger(__name__)

# Directory locations
CHART_DIR = "/home/davesmith/Documents/Personal/Python/CommodityManager/charts/"


# Markets
GOLD_LOCATIONS = ('AUXZU', 'AUXLN', 'AUXNY', 'AUXTR', 'AUXSG')
CURRENCIES = ('USD', 'GBP', 'EUR', 'YEN')

_master_df = pd.DataFrame()


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes


class Event():

    def __init__(self):

        pass



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def setup_logging():
    '''
    Setup the logging to file
    '''
    # Check we don't have any other handles attached

    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(ch)
        # the_log.addHandler(ch)

    logger.setLevel(logging.DEBUG)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

def main(args):
    '''

    '''

    setup_logging()
    markets = []

    # Populate the market objects into a list with params set to None
    for gold_loc in GOLD_LOCATIONS:
        for currency in CURRENCIES:
            if gold_loc != 'AUXTR' and currency != 'YEN':
                markets.append(gm.Market(gold_loc, currency))

    # Create the database
    db.create_database()
    logger.info("Created the database.")

    # Find the time frame we have data for
    time_in_db = db.first_row(db.GoldMarket)
    logger.info("Timestamp of the first row in GoldMarket table: {}".format(time_in_db))

    _master_df = db.to_pandas(db.GoldMarket, time_in_db, datetime.now())

    _plotly_df = pd.DataFrame()

    _columns = ["timestamp"]

    for market in markets:
        market.add_stats(_master_df)
        logger.info(market)

        # Clean up the data ready to be plotted
        _temp_df = market.mask(_master_df)
        _temp_df = _temp_df.rename(columns={"buy_quantity": "{}_{}_buy_quantity".format(market.currency, market.location),
                                            "buy_limit": "{}_{}_buy_limit".format(market.currency, market.location),
                                            "sell_quantity": "{}_{}_sell_quantity".format(market.currency, market.location),
                                            "sell_limit": "{}_{}_sell_limit".format(market.currency, market.location)})
        _temp_df = _temp_df.drop(columns=["id", "location", "currency"])
        _temp_df = _temp_df.set_index("timestamp")

        _plotly_df = pd.concat([_plotly_df, _temp_df], axis=1, sort=True)#, axis="columns", ignore_index=True)

        # Control the amount of data we plot
        if market.currency == "GBP" and market.location == "AUXLN":
            _columns.extend(list(_temp_df.columns))

        """
        Bollinger Bands are a type of statistical chart characterizing the prices and volatility over time of a 
        financial instrument or commodity, using a formulaic method propounded by John Bollinger in the 1980s.
        """
        # gm.calc_bollinger_bands(market) #TODO - Get this working properly!!! DS - 28-06-2020
        # logger.info("Market {}".format(market))

    #_columns = list(dict.fromkeys(_columns))
    logger.info(_columns)

    #_plotly_df = _plotly_df.resample('5T')

    if args.draw_chart:
        _mask = (_plotly_df.index > datetime.now() - timedelta(days=7))
        l
        _plotly_df = _plotly_df.loc[_mask]

        logger.info("We have {} rows of data across {} columns ready to draw.".format(len(_plotly_df), len(_plotly_df.columns)))
        #_plotly_df.to_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/plotly.csv")
        cd.plotly_scatter(_plotly_df, "Dave is a legend", _columns)

    if args.gather_data:
        # Create a web session to request gold market data every 5 seconds
        _thread_web_session = threading.Thread(target=bv.main)
        _thread_web_session.start()
        logger.info("Started the web socket thread.")

    while True:
        pass



if __name__ == "__main__":
    '''

    '''
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--gather_data", help="Run the thread to gather market data from bullion vault.", action="store_true")
    parser.add_argument("--draw_chart", help="Draw the market data we have in the database.", action="store_true")
    args = parser.parse_args()

    main(args)

    """
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
                    print("Exception Occured", e)

                    # fetch the login page and send back the login details
                    session.get(LOGIN_REQUEST)
                    r = session.post(LOGIN_REPLY, data=USERNAME_AND_PASSWORD)
                    """
