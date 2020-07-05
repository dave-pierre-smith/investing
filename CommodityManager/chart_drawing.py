# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:34:52 2018

@author: dave.smith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
from datetime import datetime
import logging
import re

# Third party modules
import numpy as np
from _plotly_future_ import v4_subplots
import plotly
import plotly.graph_objs as go
import plotly.subplots as sp
import plotly.express as px


# Custom modules
import main


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


def plotly_line(a_df, a_title, a_columns=[]):
    ACCEPTED_COLUMN_TYPES = [np.float64, np.int64, float]

    data = []
    _col_count = len(a_df.columns)
    _cols_loaded = 0
    _data_points = 0

    for x in range(_col_count):
        _column = a_df.columns[x]

        # Only plot the columns passed in as a list
        if _column not in a_columns:
            logger.info("plotly_scatter, Skipping {}".format(_column))
            continue

        # Reject datatypes which will cause issues plotting
        if a_df[_column].dtype not in ACCEPTED_COLUMN_TYPES:
            logger.info("Column dtype {} for {} not valid for plotting.".format(a_df[_column].dtype, _column))
            continue

        if a_df[_column].max() > 20 or a_df[_column].min() < -20:
            data.append(px.line(x=a_df.index, y=a_df[_column], name=_column, yaxis='y2'))
        else:
            data.append(px.line(x=a_df.index, y=a_df[_column], name=_column))

        # cols_loaded += 1
        _data_points += len(a_df[_column])

        layout = go.Layout(title=a_title, yaxis=dict(title='Various'), xaxis=dict(title='Quantity'),
                           yaxis2=dict(title='Price', titlefont=dict(color='rgb(148, 103, 189)'),
                                       tickfont=dict(color='rgb(148, 103, 189)'), overlaying='y', side='right'))

        # else:
        # print("reject dtype for ", _column, a_df[_column].dtype)
        # continue

        logger.info("Added column {} to chart. {:.1f}% complete.".format(_column, (x / _col_count) * 100))

    logger.info("{} data points ready to plot across {} columns and {} rows.".format(_data_points, _cols_loaded,
                                                                                     len(a_df.index)))

    fig = {'data': data, 'layout': layout}

    plotly.offline.plot(fig, auto_open=True)

def plotly_scatter_fig(a_df, a_title, a_yaxis):
    """:arg
    """
    print("plotly_scatter, args {} {} ".format(a_df["timestamp"].iloc[0], len(a_df)))

    #_df = a_df.copy()

    ACCEPTED_COLUMN_TYPES = [np.float64, np.int64, float]

    _col_count = len(a_df.columns)
    _cols_loaded = 0
    _data_points = 0

    _axes = {"y1_min": 0, "y1_max": 0, "y2_min": 0, "y2_max": 0}

    # Create traces
    # fig = go.Figure()
    #fig = sp.make_subplots(rows=2, cols=1)
    print("plotly_scatter, initialise figure with 2 subplots. Parse over {} columns, {}".format(_col_count, a_df.columns))

    fig = px.line(a_df, x="timestamp", y=a_yaxis, color="location")

    #fig.update_layout({'color': main.CSS_COLOURS["background"]})

    return fig

def plotly_scatter(a_df, a_title, a_columns=None):
    """:arg
    The figure data type for plotly is a root like structure with the 3 core elements in the first tier.
    - 'data': A list of the traces to add to the chart
    - 'layout': A plotly layout object with info on what to draw
    - 'frame':
    """
    # Create the plot
    #chart = TraceList()

    #chart.columnOrder = a_df.columns
    #chart.create_traces_from_list(a_df.columns)
    print("plotly_scatter")

    ACCEPTED_COLUMN_TYPES = [np.float64, np.int64, float]

    _col_count = len(a_df.columns)
    _cols_loaded = 0
    _data_points = 0

    _axes = {"y1_min": 0, "y1_max": 0, "y2_min": 0, "y2_max": 0}

    # Create traces
    #fig = go.Figure()
    fig = sp.make_subplots(rows=2, cols=1)
    print("plotly_scatter, initialise figure with 2 subplots. Parse over {} columns".format(_col_count))

    # Begin plotting
    for x in range(_col_count):
        _column = a_df.columns[x]

        if a_columns is not None and _column not in a_columns:
            print("plotly_scatter, Skipping {}".format(_column))
            continue

        if a_df[_column].dtype not in ACCEPTED_COLUMN_TYPES:
            print("Column dtype {} for {} not valid for plotting.".format(a_df[_column].dtype, _column))
            continue

        # Check the datatype of the column is valid
        # if a_df[_column].dtype == np.float64 or a_df[_column].dtype == np.int64 or a_df[_column].dtype is float:

        if a_df[_column].max() > 20000:
            print("plotly_scatter, add trace {} to subplot 1".format(_column))
            _trace = go.scatter(x=a_df.index, y=a_df[_column], mode='lines', name=_column)
            fig.add_trace(_trace, row=1, col=1)
            # data.append(go.Scatter(x=a_df.index, y=a_df[_column], name=_column, yaxis='y2', mode='lines'))

            if a_df[_column].min() < _axes['y1_min']:
                _axes['y1_min'] = a_df[_column].min()

            if a_df[_column].max() < _axes['y1_max']:
                _axes['y1_max'] = a_df[_column].max()

        else:
            print("plotly_scatter, add trace {} to subplot 2".format(_column))
            _trace = go.scatter(x=a_df.index, y=a_df[_column], mode='lines', name=_column)
            fig.append_trace(_trace, row=2, col=1)
            # data.append(go.Scatter(x=a_df.index, y=a_df[_column], name=_column, mode='lines'))

            if a_df[_column].min() < _axes['y2_min']:
                _axes['y2_min'] = a_df[_column].min()

            if a_df[_column].max() < _axes['y2_max']:
                _axes['y2_max'] = a_df[_column].max()

        _cols_loaded += 1
        _data_points += len(a_df[_column])

        #layout = go.Layout(title=a_title, yaxis=dict(title='Various'), xaxis=dict(title='Quantity'),
        #                   yaxis2=dict(title='Price', titlefont=dict(color='rgb(148, 103, 189)'),
        #                   tickfont=dict(color='rgb(148, 103, 189)'), overlaying='y', side='right'))

        #else:
            #print("reject dtype for ", _column, a_df[_column].dtype)
            #continue

        # logger.info("Added column {} to chart. {:.1f}% complete.".format(_column, (x/_col_count)*100))

    print("{} data points ready to plot across {} columns and {} rows.".format(_data_points, _cols_loaded, len(a_df.index)))

    #fig = {'data': data, 'layout': layout, 'frame': None}

    return fig

    # Edit the layout
    #fig.update_layout(title=a_title, yaxis=dict(title='Quantity'), xaxis=dict(title='time'), yaxis2=dict(title='Price'))

    #fig.update_yaxes(range=[_axes['y1_min'], _axes['y1_max']], row=1, col=1)
    #fig.update_yaxes(range=[_axes['y2_min'], _axes['y2_max']], row=2, col=1)

    #fig.show()

    # plotly.offline.plot(fig, auto_open=True)

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main



