# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 16:34:52 2018

@author: dave.smith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def singleAxesLineChart(title,
                        x_label, y_label,
                        save_location,
                        time_scale,
                        *args):
                        #x, y, line1_color, x2, y2, line2_color, x3, y3, line3_color):

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
    x_axis_max = args[0][len(args[0])-1]

    ax.set_xlim(x_axis_min, x_axis_max)

    ax.tick_params('y')
    ax.grid(True)

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.show()
    plt.pause(10)
    plt.savefig(save_location)
    plt.close()


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


def duelAxesLineChart(title, x, y, y2, x_label, y_label, y2_label, line1_color, line2_color, save_location):

    #years = mdates.YearLocator()   # every year
    #months = mdates.MonthLocator()  # every month
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
    x_axis_max = x[len(x)-1]
    ax1.set_xlim(x_axis_min, x_axis_max)
    ax1.grid(True)

    fig.autofmt_xdate()

    fig.tight_layout()
    plt.show()
    plt.pause(30)
    plt.savefig(save_location)
    plt.close()

def duelAxesLineChartTrendlines(title, x, y, y2, x_label, y_label, y2_label, line1_color, line2_color, time_scale, save_location):

    #years = mdates.YearLocator()   # every year
    #months = mdates.MonthLocator()  # every month

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
    z = numpy.polyfit(x_dates, y, 1)
    p = numpy.poly1d(z)

    fig, ax1 = plt.subplots()

    plt.title(title)

    ax1.plot(x, y, line1_color,
             dates_list, p(x_dates), line1_color +'--')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label, color=line1_color)
    ax1.tick_params('y', colors=line1_color)


    # Calculate the trendline
    dates_list = [date for date in x]
    x_dates = mdates.date2num(dates_list)
    z = numpy.polyfit(x_dates, y2, 1)
    p = numpy.poly1d(z)

    ax2 = ax1.twinx()
    ax2.plot(x, y2, line2_color,
             dates_list, p(x_dates), line2_color +'--')
    ax2.set_ylabel(y2_label, color=line2_color)
    ax2.tick_params('y', colors=line2_color)

    # format the ticks
    ax1.xaxis.set_major_locator(datetime_diff_major)
    ax1.xaxis.set_minor_locator(datetime_diff_minor)
    ax1.xaxis.set_major_formatter(datetimeFmt)

    print (len(x))

    x_axis_min = x[0]
    x_axis_max = x[len(x)-1]
    ax1.set_xlim(x_axis_min, x_axis_max)
    ax1.grid(True)

    fig.autofmt_xdate()

    fig.tight_layout()
    plt.show()
    plt.pause(3)
    plt.savefig(save_location)
    plt.close()

