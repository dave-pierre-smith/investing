# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import argparse
from datetime import datetime, timedelta
import logging
import time
# from threading import Timer,Thread,Event
import threading
import os
import re

# Third party modules
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import requests

from xml.etree import ElementTree

# Custom modules
import database_handler as db
import chart_drawing as cd
import bullion_vault as bv
import gold_markets as gm
import yahoo_finance as yf


app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.config.suppress_callback_exceptions = True



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

# The logger
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

# Directory locations
CHART_DIR = "/home/davesmith/Documents/Personal/Python/CommodityManager/charts/"

# Markets
GOLD_LOCATIONS = ('AUXZU', 'AUXLN', 'AUXNY', 'AUXTR', 'AUXSG')
CURRENCIES = ('USD', 'GBP', 'EUR', 'YEN')

_master_df = pd.DataFrame()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True

# Dash GUI dataframes - These are loaded as a part of main() to initialise the data.
_plotly_df = pd.read_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/master.csv")
_plotly_df['timestamp'] = pd.to_datetime(_plotly_df['timestamp'], format="%Y-%m-%d %H:%M:%S.%f")

CSS_COLOURS = {
    'background': '#101129',
    'h1_text': '#fff7b3',
    'h2_text': '#fff7b3',
    'button': '#5553ad',
    'button_text': '#ffffff'
}
H1_STYLE = {'textAlign': 'left', 'font-family': 'Courier', 'color': CSS_COLOURS['h1_text']}
BUTTON_STYLE = {'textAlign': 'center', 'color': '#fff7b3', 'background-color': '#070814', 'width': '16%', 'font-size': 25}


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs

# Define the GUI elements
_h1 = html.H1(children='Daveonomics', style=H1_STYLE)
_h2 = html.H2(children='A portal to analyse markets.', style=H1_STYLE)

_button_bullion = dcc.Link(html.Button('Bullion', id='bullion-val', n_clicks=0,style=BUTTON_STYLE), href='bullion')
_button_currencies = dcc.Link(html.Button('currencies', id='currencies-val', n_clicks=0, style=BUTTON_STYLE), href='currencies')
_button_markets = dcc.Link(html.Button('Markets', id='markets-val', n_clicks=0, style=BUTTON_STYLE), href='markets')
_button_bonds = dcc.Link(html.Button('Bonds', id='bonds-val', n_clicks=0, style=BUTTON_STYLE), href='bonds')
_button_govt = dcc.Link(html.Button('Govt', id='govt-val', n_clicks=0, style=BUTTON_STYLE), href='govt')
_button_boe = dcc.Link(html.Button('BoE', id='boe-val', n_clicks=0, style=BUTTON_STYLE), href='boe')

# Grouped together widgets used across multiple pages
CONTROL_BAR = [_h1, _button_bullion, _button_currencies, _button_markets, _button_bonds, _button_govt, _button_boe]

# Group the elements into DIVS
LAYOUT = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(CONTROL_BAR),
    html.Div(id='page-content'),

    ], style={'backgroundColor': CSS_COLOURS['background']})

# Group the elements into DIVS
app.layout = LAYOUT

# Once the main page elements are built, build the other GUI Pages which require elements from them
import gui.gui_main as gui_main
import gui.gui_bullion as gui_bullion
import gui.gui_markets as gui_markets
import gui.gui_currencies as gui_currencies
import gui.gui_bonds as gui_bonds

# Register the callbacks for all the pages
gui_bullion.register_update_graph_callbacks(app)
gui_markets.register_update_stock_graph_callbacks(app)

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

last_pathname = ""

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    global last_pathname
    print("display_page({}), last_pathname: {},".format(pathname, last_pathname))

    # Add some debug code to catch repeated callbacks
    if last_pathname == pathname:
        last_pathname = pathname
        print("last_pathname: {}, pathname: {}".format(last_pathname, pathname))
        return

    last_pathname = pathname

    if pathname == '/bullion':
        return gui_bullion.LAYOUT

    elif pathname == '/currencies':
        return gui_currencies.LAYOUT

    elif pathname == '/markets':
        return gui_markets.LAYOUT

    elif pathname == '/bonds':
        return gui_bonds.LAYOUT


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main


def main(args):
    '''

    '''

    #setup_logging()
    markets = []

    global _plotly_df

    # Populate the market objects into a list with params set to None
    for gold_loc in GOLD_LOCATIONS:
        for currency in CURRENCIES:
            if gold_loc != 'AUXTR' and currency != 'YEN':
                markets.append(gm.Market(gold_loc, currency))

    # Create the database
    db.create_database()
    print("Created the database.")

    # Find the time frame we have data for
    time_in_db = db.first_row(db.GoldMarket)
    print("Timestamp of the first row in GoldMarket table: {}".format(time_in_db))

    _master_df = db.to_pandas(db.GoldMarket, time_in_db, datetime.now())
    _master_df.to_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/master.csv")

    _columns = ["timestamp"]

    for market in markets:
        market.add_stats(_master_df)
        print(market)

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
    print(_columns)

    #_plotly_df = _plotly_df.resample('5T')

    if args.draw_chart:
        _mask = (_plotly_df.index > datetime.now() - timedelta(days=7))
        _plotly_df = _plotly_df.loc[_mask]

        print("We have {} rows of data across {} columns ready to draw.".format(len(_plotly_df), len(_plotly_df.columns)))
        #_plotly_df.to_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/plotly.csv")
        cd.plotly_scatter(_plotly_df, "Dave is a legend", _columns)

    if args.gather_data:
        # Create a web session to request gold market data every 5 seconds
        _thread_web_session = threading.Thread(target=bv.main)
        _thread_web_session.start()
        print("Started the web socket thread.")



if __name__ == "__main__":
    '''

    '''
    # setup_logging()

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--gather_data", help="Run the thread to gather market data from bullion vault.", action="store_true")
    parser.add_argument("--draw_chart", help="Draw the market data we have in the database.", action="store_true")
    args = parser.parse_args()



    # main(args)

    print("DASH VERSION: {}".format(dcc.__version__))
    app.run_server(debug=True)

    print("Running code after the app is initialised.")
