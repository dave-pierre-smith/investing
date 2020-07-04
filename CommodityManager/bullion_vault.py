# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import time
from datetime import datetime, timedelta
import logging
import json

# Third party modules
from xml.etree import ElementTree
import requests
import pandas as pd

# Custom modules
import database_handler as db


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

VIEW_MARKET = 'https://www.bullionvault.com/secure/api/v2/view_market_xml.do'

# Web connection consts
LOGIN_REQUEST = "https://www.bullionvault.com/secure/login.do"
LOGIN_REPLY = 'https://www.bullionvault.com/secure/j_security_check?'
USER_DETAILS_FILEPATH = "login.json"




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


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

    logger.info("Database size: {}, Time total = {:.1f} ms, response = {:.1f}ms, ET = {:.1f}ms".format(
        str(rows), ((time_save_to_db - time_start) * 1000), ((time_response - time_start) * 1000), ((time_save_to_db - time_response) * 1000)))

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

def main():
    # Fill the database
    with requests.session() as session:

        with open(USER_DETAILS_FILEPATH) as f:
            _login_deets = json.load(f)

        # fetch the login page and send back the login details
        session.get(LOGIN_REQUEST)
        r = session.post(LOGIN_REPLY, data=_login_deets)
        _login_deets = None

        # Get the market info every 5 seconds and add to a database
        timer = time.time()

        while (True):
            if time.time() > (timer + 5):
                timer = time.time()

                # Try get the market info. If the connection is closed then
                # re-establish
                try:
                    get_market_prices(session)

                except Exception as e:
                    print(e)

                    with open(USER_DETAILS_FILEPATH) as f:
                        _login_deets = json.load(f)

                    # fetch the login page and send back the login details
                    session.get(LOGIN_REQUEST)
                    r = session.post(LOGIN_REPLY, data=_login_deets)
                    _login_deets = None