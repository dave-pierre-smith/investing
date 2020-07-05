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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Dash GUI dataframes - These are loaded as a part of main() to initialise the data.
_plotly_df = pd.read_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/master.csv")
_plotly_df['timestamp'] = pd.to_datetime(_plotly_df['timestamp'], format="%Y-%m-%d %H:%M:%S.%f")


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet

CSS_COLOURS = {
    'background': '#d7e0e0',
    'h1_text': '#1b1c1c',
    'h2_text': '#353738'
}

SLIDER_DATES = [datetime(2017,1,1) + timedelta(weeks=(x*3)) for x in range(16)]

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs

# Define the GUI elements
_h1 = html.H1(children='Daveonomics', style={'textAlign': 'center','color': CSS_COLOURS['h1_text']})
_h2 = html.H2(children='A portal to analyse markets.', style={'textAlign': 'center','color': CSS_COLOURS['h1_text']})

_dt_picker = dcc.DatePickerRange(id='my-date-picker-range',
            min_date_allowed=_plotly_df['timestamp'].min(), max_date_allowed=_plotly_df['timestamp'].max(),
            initial_visible_month=_plotly_df['timestamp'].max().date(), end_date=_plotly_df['timestamp'].max().date())

_dropdown = dcc.Dropdown(id='dropdown-currency',
        options=[
            {'label': 'Great British Pounds', 'value': 'GBP'},
            {'label': 'US Dollar', 'value': 'USD'},
            {'label': 'Euro', 'value': 'EUR'}
        ],
        value='GBP'
    )

_graph = dcc.Graph(id='indicator-graphic', style={'width': '100%'})
_graph_sell_limit = dcc.Graph(id='graph_sell_limit', style={'width': '100%'})
_graph_buy_quantity = dcc.Graph(id='graph_buy_quantity', style={'width': '100%'})
_graph_sell_quantity = dcc.Graph(id='graph_sell_quantity', style={'width': '100%'})

# Group the elements into DIVS
app.layout = \
    html.Div([
        html.Div([_h1, _h2, _dt_picker, _dropdown]),
        html.Div([_graph], style={'width': '48%', 'float': 'left', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_sell_limit], style={'width': '48%', 'float': 'right', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_buy_quantity], style={'width': '48%', 'float': 'left', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_sell_quantity], style={'width': '48%', 'float': 'right', 'backgroundColor': CSS_COLOURS['background']}),

    ],
    style={'backgroundColor': CSS_COLOURS['background']})


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

@app.callback([Output('indicator-graphic', 'figure'),
               Output('graph_sell_limit', 'figure'),
               Output('graph_buy_quantity', 'figure'),
               Output('graph_sell_quantity', 'figure')],
              [Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('dropdown-currency', 'value')])
def update_graph(start_date, end_date, currency):

    global _plotly_df

    print("update_graph, df.len: {}, df.columns {}".format(len(_plotly_df), _plotly_df.columns))

    # Mask out the currency
    _temp_df = _plotly_df.copy()
    _temp_df = _temp_df.loc[_plotly_df['currency'] == currency]

    # We have some dates to mask the data on
    if start_date is not None and end_date is not None:
        a_start_date = datetime.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        a_end_date = datetime.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')

        _temp_df = _temp_df.loc[(_temp_df["timestamp"] >= a_start_date) & (_temp_df["timestamp"] <= a_end_date)]
        print("len(_df): {}", len(_temp_df))

    _fig = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_yaxis="buy_limit")
    _fig_2 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_yaxis="sell_limit")
    _fig_3 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_yaxis="buy_quantity")
    _fig_4 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_yaxis="sell_quantity")

    return _fig, _fig_2, _fig_3, _fig_4



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
