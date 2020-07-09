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
import pandas_handler as ph

# GUI Modules
import gui.gui_main as gui_main

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

# Dash GUI dataframes - These are loaded as a part of main() to initialise the data.
_plotly_df = pd.read_csv("/home/davesmith/Documents/Personal/GIThub/investing/CommodityManager/csv/master.csv")
_plotly_df['timestamp'] = pd.to_datetime(_plotly_df['timestamp'], format="%Y-%m-%d %H:%M:%S.%f")


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet

SLIDER_DATES = [datetime(2017,1,1) + timedelta(weeks=(x*3)) for x in range(16)]

CSS_COLOURS = {
    'background': '#101129',
    'h1_text': '#fff7b3',
    'h2_text': '#fff7b3',
    'button': '#5553ad',
    'button_text': '#ffffff'
}

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs





# Grouped together widgets used across multiple pages

# Build the layout

# Define the GUI elements
_dt_picker = dcc.DatePickerRange(id='my-date-picker-range',
                                 min_date_allowed=_plotly_df['timestamp'].min(),
                                 max_date_allowed=_plotly_df['timestamp'].max(),
                                 initial_visible_month=_plotly_df['timestamp'].max().date(),
                                 end_date=_plotly_df['timestamp'].max().date())

_dropdown = dcc.Dropdown(id='dropdown-currency',
                         options=[
                             {'label': 'Great British Pounds', 'value': 'GBP'},
                             {'label': 'US Dollar', 'value': 'USD'},
                             {'label': 'Euro', 'value': 'EUR'}
                         ],
                         value='GBP'
                         )

# Mask out the currency
_temp_df = _plotly_df.copy()
_temp_df = _temp_df.loc[_plotly_df['currency'] == "GBP"]

_temp_df = ph.resample_bullion_dataframe(_temp_df)

"""
# We have some dates to mask the data on
a_start_date = datetime.strptime(re.split('T| ', "2017-01-01")[0], '%Y-%m-%d')
a_end_date = datetime.strptime(re.split('T| ', "2020-07-30")[0], '%Y-%m-%d')

_temp_df = _temp_df.loc[(_temp_df["timestamp"] >= a_start_date) & (_temp_df["timestamp"] <= a_end_date)]
print("len(_df): {}", len(_temp_df))
"""

_fig = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="buy_limit", a_color="location")
_fig_2 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="sell_limit", a_color="location")
_fig_3 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="buy_quantity", a_color="location")
_fig_4 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="sell_quantity", a_color="location")

_graph = dcc.Graph(id='indicator-graphic', figure=_fig, style={'width': '100%'})
_graph_sell_limit = dcc.Graph(id='graph_sell_limit', figure=_fig_2, style={'width': '100%'})
_graph_buy_quantity = dcc.Graph(id='graph_buy_quantity', figure=_fig_3, style={'width': '100%'})
_graph_sell_quantity = dcc.Graph(id='graph_sell_quantity', figure=_fig_4, style={'width': '100%'})

LAYOUT = \
    html.Div([
        #html.Div(main.CONTROL_BAR),
        html.Div([_dt_picker, _dropdown]),
        html.Div([_graph], style={'width': '48%', 'float': 'left', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_sell_limit], style={'width': '48%', 'float': 'right', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_buy_quantity], style={'width': '48%', 'float': 'left', 'backgroundColor': CSS_COLOURS['background']}),
        html.Div([_graph_sell_quantity], style={'width': '48%', 'float': 'right', 'backgroundColor': CSS_COLOURS['background']}),

    ],
    style={'backgroundColor': CSS_COLOURS['background']})



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def register_update_graph_callbacks(app):

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

        _temp_df = ph.resample_bullion_dataframe(_temp_df)

        _fig = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="buy_limit", a_color="location")
        _fig_2 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="sell_limit", a_color="location")
        _fig_3 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="buy_quantity", a_color="location")
        _fig_4 = cd.plotly_scatter_fig(_temp_df, "Dave is a legend", a_xaxis="timestamp", a_yaxis="sell_quantity", a_color="location")

        return _fig, _fig_2, _fig_3, _fig_4
