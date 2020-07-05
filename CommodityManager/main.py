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


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

# LOGGER = logging.getLogger()
logger = logging.getLogger(__name__)

# Directory locations
CHART_DIR = "/home/davesmith/Documents/Personal/Python/CommodityManager/charts/"


# Markets
GOLD_LOCATIONS = ('AUXZU', 'AUXLN', 'AUXNY', 'AUXTR', 'AUXSG')
CURRENCIES = ('USD', 'GBP', 'EUR', 'YEN')

_master_df = pd.DataFrame()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Dash GUI dataframes
_plotly_df = pd.DataFrame()

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




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


df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

available_indicators = df['Indicator Name'].unique()

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Fertility rate, total (births per woman)'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Life expectancy at birth, total (years)'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        id='year--slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    )
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-type', 'value'),
     Input('year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')

    return fig



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

def main(args):
    '''

    '''

    setup_logging()
    markets = []

    global _plotly_df

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
        _plotly_df = _plotly_df.loc[_mask]

        logger.info("We have {} rows of data across {} columns ready to draw.".format(len(_plotly_df), len(_plotly_df.columns)))
        #_plotly_df.to_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/plotly.csv")
        cd.plotly_scatter(_plotly_df, "Dave is a legend", _columns)

    if args.gather_data:
        # Create a web session to request gold market data every 5 seconds
        _thread_web_session = threading.Thread(target=bv.main)
        _thread_web_session.start()
        logger.info("Started the web socket thread.")



if __name__ == "__main__":
    '''

    '''
    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--gather_data", help="Run the thread to gather market data from bullion vault.", action="store_true")
    parser.add_argument("--draw_chart", help="Draw the market data we have in the database.", action="store_true")
    args = parser.parse_args()

    main(args)

    print("DASH VERSION: {}".format(dcc.__version__))
    app.run_server(debug=True)
