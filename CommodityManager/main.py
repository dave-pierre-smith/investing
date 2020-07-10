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
    'background': '#070814', #  101129
    'h1_text': '#fff7b3',
    'h2_text': '#fff7b3',
    'button': '#242424',
    'button_text': '#ffffff'
}
H1_STYLE = {'textAlign': 'left', 'font-family': 'Courier', 'color': CSS_COLOURS['h1_text'], 'backgroundColor': '#050505', 'hover' :{
  'backgroundColor': '#ffffff', #; /* Green */
  'color': 'white'
}}
BUTTON_TIER1_INNER_STYLE = {'textAlign': 'center', 'color': '#fff7b3', 'background-color': '#050505',
                            'width': '17%', 'font-size': 25, 'border': '0px solid #ffffff',
                            'hover' :{
                              'backgroundColor': '#ffffff', #; /* Green */
                              'color': 'white'
                            }}
BUTTON_TIER1_OUTER_STYLE = {'textAlign': 'center', 'color': '#fff7b3', 'background-color': '#050505', 'width': '16%', 'font-size': 25, 'border': '0px solid #ffffff'}
BUTTON_TIER2_STYLE = {'textAlign': 'center', 'color': '#fff7b3', 'background-color': '#050505', 'width': '96%', 'height': '10pc', 'font-size': 20, 'float': 'centre',
                      'position': 'relative', 'left': '2%', 'top': '0px'}


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Style Sheet


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs

# Define the GUI elements
_h1 = html.H1(children='Daveonomics', style=H1_STYLE)
_h2 = html.H2(children='A portal to analyse markets.', style=H1_STYLE)

_button_bullion = dcc.Link(html.Button('Bullion', id='bullion-val', n_clicks=0,style=BUTTON_TIER1_OUTER_STYLE), href='bullion')
_button_currencies = dcc.Link(html.Button('currencies', id='currencies-val', n_clicks=0, style=BUTTON_TIER1_INNER_STYLE), href='currencies')
_button_markets = dcc.Link(html.Button('Markets', id='markets-val', n_clicks=0, style=BUTTON_TIER1_INNER_STYLE), href='markets')
_button_bonds = dcc.Link(html.Button('Bonds', id='bonds-val', n_clicks=0, style=BUTTON_TIER1_INNER_STYLE), href='bonds')
_button_govt = dcc.Link(html.Button('Govt', id='govt-val', n_clicks=0, style=BUTTON_TIER1_INNER_STYLE), href='govt')
_button_boe = dcc.Link(html.Button('BoE', id='boe-val', n_clicks=0, style=BUTTON_TIER1_OUTER_STYLE), href='boe')
_hr = html.Hr(style={'color': '#050505', 'backgroundColor': '#fff7b3', 'width': '100%'})

# Grouped together widgets used across multiple pages
CONTROL_BAR = {'bullion-val': _button_bullion, 'currencies-val':  _button_currencies,
               'markets-val': _button_markets, 'bonds-val': _button_bonds, 'govt-val': _button_govt, 'boe-val': _button_boe}
print(CONTROL_BAR.values())

_button_dimension1 = dcc.Link(html.Button('1D', id='dimension1-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension1')
_button_dimension2 = dcc.Link(html.Button('2D', id='dimension2-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension2')
_button_dimension3 = dcc.Link(html.Button('3D', id='dimension3-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension3')
_button_dimension4 = dcc.Link(html.Button('4D', id='dimension4-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension4')
_button_dimension5 = dcc.Link(html.Button('5D', id='dimension5-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension5')
_button_dimension6 = dcc.Link(html.Button('6D', id='dimension6-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='dimension6')

DIMENSION_BAR = [_button_dimension1, _button_dimension2, _button_dimension3, _button_dimension4, _button_dimension5, _button_dimension6]

_button_chart_scatter = dcc.Link(html.Button('Scatter', id='scatter-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='scatter')
_button_chart_line = dcc.Link(html.Button('Line', id='line-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='line')
_button_chart_bubble = dcc.Link(html.Button('Bubble', id='bubble-val', n_clicks=0, style=BUTTON_TIER2_STYLE), href='bubble')

CHART_BAR = [_button_chart_scatter, _button_chart_line, _button_chart_bubble]

# Group the elements into DIVS
LAYOUT = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(_h1, style={'backgroundColor': '#050505'}),
    html.Div(list(CONTROL_BAR.values()), style={'backgroundColor': '#050505'}),
    html.Div(_hr, style={'backgroundColor': '#050505'}),
    #html.Div([html.Hr()], style={'color': '#050505', 'backgroundColor': '#050505', 'width': '100%'}),
    html.Div([
        html.Div(DIMENSION_BAR, style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
        html.Div(CHART_BAR, style={'width': '70%', 'float': 'left', 'display': 'inline-block'})
        ], style={'width': '15%', 'float': 'left', 'display': 'inline-block', 'border-style': 'ridge', 'backgroundColor': '#050505', 'position': 'relative', 'top': '0px', 'left': '2%'} ),

    html.Div(id='page-content', style={'width': '81%', 'float': 'right', 'display': 'inline-block', 'backgroundColor': CSS_COLOURS['background'], 'position': 'relative', 'top': '0px', 'left': '0%'}),

    ], style={'width': '100%', 'float': 'center', 'height': '100pc', 'display': 'inline-block', 'backgroundColor': CSS_COLOURS['background']})

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

"""
# Update the index
@app.callback([Output('page-content', 'children'), Output("bullion-val", "style"), Output("currencies-val", "style"), Output("markets-val", "style"),
               Output("bonds-val", "style"), Output("govt-val", "style"), Output("boe-val", "style")],
              [Input("bullion-val", "n_clicks"), Input("currencies-val", "n_clicks"), Input("markets-val", "n_clicks"),
               Input("bonds-val", "n_clicks"), Input("govt-val", "n_clicks"), Input("boe-val", "n_clicks")])
def display_page(pathname, *args):
    global last_pathname
    print("display_page({}), last_pathname: {},".format(pathname, last_pathname))

    # Add some debug code to catch repeated callbacks
    if last_pathname == pathname:
        last_pathname = pathname
        print("last_pathname: {}, pathname: {}".format(last_pathname, pathname))
        return

    last_pathname = pathname

    # Update the button color and load the new layout
    _return = []

    for _id in list(CONTROL_BAR.keys()):
        _style = CONTROL_BAR[_id].children.style.copy()
        print(_style)

        _link_id = pathname[1:] + '-val'

        if _id == _link_id:
            _style['background-color'] = '#403f3f'
            _return.append(_style)

        else:
            _style['background-color'] = '#050505'
            _return.append(_style)


    if pathname == '/bullion':
        layout = gui_bullion.LAYOUT

    elif pathname == '/currencies':
        return gui_currencies.LAYOUT

    elif pathname == '/markets':
        return gui_markets.LAYOUT

    elif pathname == '/bonds':
        return gui_bonds.LAYOUT

    elif pathname == '/govt':
        return gui_bonds.LAYOUT

    elif pathname == '/boe':
        return gui_bonds.LAYOUT
        """

"""
# Update the shading on the tier 1 buttons.
"""
@app.callback(
    [Output("bullion-val", "style"), Output("currencies-val", "style"), Output("markets-val", "style"),
     Output("bonds-val", "style"), Output("govt-val", "style"), Output("boe-val", "style"), Output('page-content', 'children')],
    [Input("bullion-val", "n_clicks"), Input("currencies-val", "n_clicks"), Input("markets-val", "n_clicks"),
     Input("bonds-val", "n_clicks"), Input("govt-val", "n_clicks"), Input("boe-val", "n_clicks")]
)
def set_active(*args):
    print("set_active, market-val, {}".format(args))

    _return = []
    ctx = dash.callback_context

    if not ctx.triggered or not any(args):
        print("No clicks yet")
        return BUTTON_TIER1_OUTER_STYLE, BUTTON_TIER1_INNER_STYLE, BUTTON_TIER1_INNER_STYLE, BUTTON_TIER1_INNER_STYLE, BUTTON_TIER1_INNER_STYLE, BUTTON_TIER1_OUTER_STYLE, ""

    # get id of triggering button
    _trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print("ctx.triggered: {}".format(_trigger_id))

    for _id in list(CONTROL_BAR.keys()):
        # Update the button colour
        _style = CONTROL_BAR[_id].children.style.copy()
        print(_style)

        if _id == _trigger_id:
            _style['background-color'] = '#403f3f'
            _return.append(_style)

        else:
            _style['background-color'] = '#050505'
            _return.append(_style)
            #_return.append(BUTTON_TIER1_OUTER_STYLE)

    # Get the layout
    if _trigger_id == 'bullion-val':
        _return.append(gui_bullion.LAYOUT)

    elif _trigger_id == 'currencies-val':
        _return.append(gui_currencies.LAYOUT)

    elif _trigger_id == 'markets-val':
        _return.append(gui_markets.LAYOUT)

    elif _trigger_id == 'bonds-val':
        _return.append(gui_bonds.LAYOUT)

    elif _trigger_id == 'govt-val':
        _return.append(gui_bonds.LAYOUT)

    elif _trigger_id == 'boe-val':
        _return.append(gui_bonds.LAYOUT)

    else:
        _return.append("")

    print(_return)

    return _return

    #for _button in args:


    """
    ctx = dash.callback_context

    if not ctx.triggered or not any(args):
        return ["btn" for _ in range(1, 4)]

    # get id of triggering button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    return [
        "btn active" if button_id == f"btn-{i}" else "btn" for i in range(1, 4)
    ]
    """

    return {'textAlign': 'center', 'color': '#ffffff', 'background-color': '#403f3f',
                            'width': '17%', 'font-size': 25, 'border': '0px solid #ffffff'}


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
