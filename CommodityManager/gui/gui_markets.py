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

# GUI Modules


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants


# Dash GUI dataframes - These are loaded as a part of main() to initialise the data.

CSS_COLOURS = {
    'background': '#070814', # 101129
    'h1_text': '#fff7b3',
    'h2_text': '#fff7b3',
    'button': '#242424', # 5553ad
    'button_text': '#ffffff'
}

STOCK_TICKER = [
                 {'label': 'Tesla', 'value': 'TSLA'},
                 {'label': 'Microsoft', 'value': 'MSFT'},
                 {'label': 'Apple', 'value': 'AAPL'}
             ]

H3_STYLE = {'textAlign': 'left', 'font-family': 'Courier', 'color': CSS_COLOURS['h1_text']}


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs

# Define the GUI elements
_dropdown = dcc.Dropdown(id='dropdown-stock', options=STOCK_TICKER, value=STOCK_TICKER[0]['value'], style={'width': '100%', 'float': 'left'})


_df = yf.get_stock(STOCK_TICKER[0]['value']).copy()
_df = _df.reset_index()

print("update_stock_graph, df.len: {}, df.columns {}".format(len(_df), _df.columns))

#_fig = cd.plotly_scatter_fig(_df, "Dave is a legend", a_xaxis="index", a_yaxis="Open")
_fig = cd.plotly_candlestick(_df)

_graph = dcc.Graph(id='stock-graphic', figure=_fig, style={'width': '100%', 'float': 'right', 'backgroundColor': CSS_COLOURS['background']})

# Grouped together widgets used across multiple pages

# Build the layout
LAYOUT = \
    html.Div([
        html.Div(["Input 1"], style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
        html.Div(["Input 2"], style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
        html.Div(["Input 3"], style={'width': '33%', 'float': 'left', 'display': 'inline-block'}),
        html.Div([_dropdown], style={'width': '15%', 'float': 'left', 'display': 'inline-block'}),
        html.Div([_graph], style={'width': '83%', 'backgroundColor': CSS_COLOURS['background'], 'display': 'inline-block'}),
    ],
    style={'backgroundColor': CSS_COLOURS['background']})


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def register_update_stock_graph_callbacks(app):

    @app.callback(Output('stock-graphic', 'figure'),
                  [Input('dropdown-stock', 'value')])
    def update_stock_graph(a_stock):
        print("update_stock_graph({})".format(a_stock))

        _df = yf.get_stock(a_stock).copy()
        _df = _df.reset_index()

        print("update_stock_graph, df.len: {}, df.columns {}".format(len(_df), _df.columns))

        _fig = cd.plotly_candlestick(_df)
        #_fig = cd.plotly_scatter_fig(_df, "Dave is a legend",  a_xaxis="index", a_yaxis="open")

        return _fig