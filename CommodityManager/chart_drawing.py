# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:34:52 2018

@author: dave.smith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import logging

# Third party modules
import numpy as np
from _plotly_future_ import v4_subplots
import plotly
import plotly.graph_objs as go
import plotly.subplots as sp
#import plotly.express as px


# Custom modules


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes

class Trace():
    def __init__(self):
        self.name = ""
        self.dataPoints = []

    def get_max(self):
        if len(self.dataPoints) == 0:
            return 0
        return max(self.dataPoints)


class TraceList():
    def __init__(self):
        self.time = []
        self.traces = {}
        self.columnOrder = []

    def new_trace(self, name):
        t = Trace()
        t.name = name
        self.traces[name] = t

    def create_traces_from_list(self, names):
        for n in names:
            self.new_trace(n)

    def add_new_line(self, data, timestamp):

        for k, v in data.items():
            # find trace
            t = self.traces[k]
            t.dataPoints.append(float(v))

        self.time.append(timestamp)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def singleAxesLineChart(title,
                        x_label, y_label,
                        save_location,
                        time_scale,
                        *args):


    # x, y, line1_color, x2, y2, line2_color, x3, y3, line3_color):

    if (time_scale == 'Hour'):
        datetime_diff_major = mdates.HourLocator(interval=3)  # every 5 day
        datetime_diff_minor = mdates.HourLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%H:%M')
    elif (time_scale == 'Day'):
        datetime_diff_major = mdates.DayLocator(interval=5)  # every 5 day
        datetime_diff_minor = mdates.DayLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%d/%m/%Y')
    elif (time_scale == 'Month'):
        datetime_diff_major = mdates.MonthLocator(interval=1)  # every 5 day
        datetime_diff_minor = mdates.DayLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%d/%m/%Y')

    fig, ax = plt.subplots()

    plt.title(title)

    ax.plot(*args)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # format the ticks
    ax.xaxis.set_major_locator(datetime_diff_major)
    ax.xaxis.set_major_formatter(datetimeFmt)
    ax.xaxis.set_minor_locator(datetime_diff_minor)

    x_axis_min = args[0][0]
    x_axis_max = args[0][len(args[0]) - 1]

    ax.set_xlim(x_axis_min, x_axis_max)

    ax.tick_params('y')
    ax.grid(True)

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.show()
    plt.pause(10)
    plt.savefig(save_location)
    plt.close()

def duelAxesLineChart(title, x, y, y2, x_label, y_label, y2_label, line1_color, line2_color, save_location):
    # years = mdates.YearLocator()   # every year
    # months = mdates.MonthLocator()  # every month
    five_days = mdates.DayLocator(interval=5)  # every 5 day
    days = mdates.DayLocator(interval=1)  # every day
    dateFmt = mdates.DateFormatter('%d/%m/%Y')

    print(five_days)

    fig, ax1 = plt.subplots()

    plt.title(title)

    ax1.plot(x, y, line1_color)
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label, color=line1_color)
    ax1.tick_params('y', colors=line1_color)

    ax2 = ax1.twinx()
    ax2.plot(x, y2, line2_color)
    ax2.set_ylabel(y2_label, color=line2_color)
    ax2.tick_params('y', colors=line2_color)

    # format the ticks
    ax1.xaxis.set_major_locator(five_days)
    ax1.xaxis.set_major_formatter(dateFmt)
    ax1.xaxis.set_minor_locator(days)

    x_axis_min = x[0]
    x_axis_max = x[len(x) - 1]
    ax1.set_xlim(x_axis_min, x_axis_max)
    ax1.grid(True)

    fig.autofmt_xdate()

    fig.tight_layout()
    plt.show()
    plt.pause(30)
    plt.savefig(save_location)
    plt.close()


def duelAxesLineChartTrendlines(title, x, y, y2, x_label, y_label, y2_label, line1_color, line2_color, time_scale,
                                save_location):
    # years = mdates.YearLocator()   # every year
    # months = mdates.MonthLocator()  # every month

    if (time_scale == 'Hour'):
        datetime_diff_major = mdates.HourLocator(interval=3)  # every 5 day
        datetime_diff_minor = mdates.HourLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%h/%M')
    elif (time_scale == 'Day'):
        datetime_diff_major = mdates.DayLocator(interval=5)  # every 5 day
        datetime_diff_minor = mdates.DayLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%d/%m/%Y')
    elif (time_scale == 'Month'):
        datetime_diff_major = mdates.MonthLocator(interval=1)  # every 5 day
        datetime_diff_minor = mdates.DayLocator(interval=1)  # every day
        datetimeFmt = mdates.DateFormatter('%d/%m/%Y')

    # Calculate the trendline
    dates_list = [date for date in x]
    x_dates = mdates.date2num(dates_list)
    z = np.polyfit(x_dates, y, 1)
    p = np.poly1d(z)

    fig, ax1 = plt.subplots()

    plt.title(title)

    ax1.plot(x, y, line1_color,
             dates_list, p(x_dates), line1_color + '--')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label, color=line1_color)
    ax1.tick_params('y', colors=line1_color)

    # Calculate the trendline
    dates_list = [date for date in x]
    x_dates = mdates.date2num(dates_list)
    z = np.polyfit(x_dates, y2, 1)
    p = np.poly1d(z)

    ax2 = ax1.twinx()
    ax2.plot(x, y2, line2_color,
             dates_list, p(x_dates), line2_color + '--')
    ax2.set_ylabel(y2_label, color=line2_color)
    ax2.tick_params('y', colors=line2_color)

    # format the ticks
    ax1.xaxis.set_major_locator(datetime_diff_major)
    ax1.xaxis.set_minor_locator(datetime_diff_minor)
    ax1.xaxis.set_major_formatter(datetimeFmt)

    print(len(x))

    x_axis_min = x[0]
    x_axis_max = x[len(x) - 1]
    ax1.set_xlim(x_axis_min, x_axis_max)
    ax1.grid(True)

    fig.autofmt_xdate()

    fig.tight_layout()
    plt.show()
    plt.pause(3)
    plt.savefig(save_location)
    plt.close()

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


def plotly_scatter(a_df, a_title, a_columns=[]):
    # Create the plot
    #chart = TraceList()

    #chart.columnOrder = a_df.columns
    #chart.create_traces_from_list(a_df.columns)

    ACCEPTED_COLUMN_TYPES = [np.float64, np.int64, float]

    data = []
    _col_count = len(a_df.columns)
    _cols_loaded = 0
    _data_points = 0

    _axes = {"y1_min": 0, "y1_max": 0, "y2_min": 0, "y2_max": 0}

    # Create traces
    #fig = go.Figure()
    fig = sp.make_subplots(rows=2, cols=1)

    # Begin plotting
    for x in range(_col_count):
        _column = a_df.columns[x]

        if _column not in a_columns:
            logger.info("plotly_scatter, Skipping {}".format(_column))
            continue

        if a_df[_column].dtype not in ACCEPTED_COLUMN_TYPES:
            logger.info("Column dtype {} for {} not valid for plotting.".format(a_df[_column].dtype, _column))
            continue

        # Check the datatype of the column is valid
        # if a_df[_column].dtype == np.float64 or a_df[_column].dtype == np.int64 or a_df[_column].dtype is float:

        if a_df[_column].max() > 20000:
            fig.append_trace(go.Scatter(x=a_df.index, y=a_df[_column], mode='lines', name=_column), row=1, col=1)
            # data.append(go.Scatter(x=a_df.index, y=a_df[_column], name=_column, yaxis='y2', mode='lines'))

            if a_df[_column].min() < _axes['y1_min']:
                _axes['y1_min'] = a_df[_column].min()

            if a_df[_column].max() < _axes['y1_max']:
                _axes['y1_max'] = a_df[_column].max()

        else:
            fig.append_trace(go.Scatter(x=a_df.index, y=a_df[_column], mode='lines', name=_column), row=2, col=1)
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

        logger.info("Added column {} to chart. {:.1f}% complete.".format(_column, (x/_col_count)*100))

    logger.info("{} data points ready to plot across {} columns and {} rows.".format(_data_points, _cols_loaded, len(a_df.index)))

    #fig = {'data': data, 'layout': layout}

    # Edit the layout
    #fig.update_layout(title=a_title, yaxis=dict(title='Quantity'), xaxis=dict(title='time'), yaxis2=dict(title='Price'))

    #fig.update_yaxes(range=[_axes['y1_min'], _axes['y1_max']], row=1, col=1)
    #fig.update_yaxes(range=[_axes['y2_min'], _axes['y2_max']], row=2, col=1)

    #fig.show()

    plotly.offline.plot(fig, auto_open=True)

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main



