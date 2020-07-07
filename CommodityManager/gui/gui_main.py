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



# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet

CSS_COLOURS = {
    'background': '#101129',
    'h1_text': '#fff7b3',
    'h2_text': '#fff7b3',
    'button': '#5553ad',
    'button_text': '#ffffff'
}
H1_STYLE = {'textAlign': 'center', 'font-family': 'Courier', 'color': CSS_COLOURS['h1_text']}
BUTTON_STYLE = {'textAlign': 'center', 'color': '#fff7b3', 'background-color': '#070814', 'width': '25%', 'font-size': 25}


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs

# Define the GUI elements
_h1 = html.H1(children='Daveonomics', style=H1_STYLE)
_h2 = html.H2(children='A portal to analyse markets.', style=H1_STYLE)
_button_commodities = html.Button('Bullion', id='bullion-val', n_clicks=0,style=BUTTON_STYLE);
_button_currencies = html.Button('currencies', id='currencies-val', n_clicks=0, style=BUTTON_STYLE);
_button_markets = html.Button('Markets', id='markets-val', n_clicks=0, style=BUTTON_STYLE)
_button_bonds = html.Button('Bonds', id='bonds-val', n_clicks=0, style=BUTTON_STYLE)

# Grouped together widgets used across multiple pages
CONTROL_BAR = [_h1, _button_commodities, _button_currencies, _button_markets, _button_bonds]

# Group the elements into DIVS
main_layout = html.Div([html.Div(CONTROL_BAR)], style={'backgroundColor': CSS_COLOURS['background']})


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

