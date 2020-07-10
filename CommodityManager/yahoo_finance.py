# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import logging
import time

# Third party modules
from datetime import datetime, timezone, timedelta
import pandas as pd
import os
import yfinance

# Custom modules


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes

_business_info = ['timestamp', 'zip', 'sector', 'fullTimeEmployees', 'longBusinessSummary', 'city', 'phone', 'state', 'country', 'companyOfficers', 'website', 'maxAge', 'address1', 'industry', 'previousClose', 'regularMarketOpen', 'twoHundredDayAverage', 'trailingAnnualDividendYield', 'payoutRatio', 'volume24Hr', 'regularMarketDayHigh', 'navPrice', 'averageDailyVolume10Day', 'totalAssets', 'regularMarketPreviousClose', 'fiftyDayAverage', 'trailingAnnualDividendRate', 'open', 'toCurrency', 'averageVolume10days', 'expireDate', 'yield', 'algorithm', 'dividendRate', 'exDividendDate', 'beta', 'circulatingSupply', 'startDate', 'regularMarketDayLow', 'priceHint', 'currency', 'regularMarketVolume', 'lastMarket', 'maxSupply', 'openInterest', 'marketCap', 'volumeAllCurrencies', 'strikePrice', 'averageVolume', 'priceToSalesTrailing12Months', 'dayLow', 'ask', 'ytdReturn', 'askSize', 'volume', 'fiftyTwoWeekHigh', 'forwardPE', 'fromCurrency', 'fiveYearAvgDividendYield', 'fiftyTwoWeekLow', 'bid', 'tradeable', 'dividendYield', 'bidSize', 'dayHigh', 'exchange', 'shortName', 'longName', 'exchangeTimezoneName', 'exchangeTimezoneShortName', 'isEsgPopulated', 'gmtOffSetMilliseconds', 'quoteType', 'symbol', 'messageBoardId', 'market', 'annualHoldingsTurnover', 'enterpriseToRevenue', 'beta3Year', 'profitMargins', 'enterpriseToEbitda', '52WeekChange', 'morningStarRiskRating', 'forwardEps', 'revenueQuarterlyGrowth', 'sharesOutstanding', 'fundInceptionDate', 'annualReportExpenseRatio', 'bookValue', 'sharesShort', 'sharesPercentSharesOut', 'fundFamily', 'lastFiscalYearEnd', 'heldPercentInstitutions', 'netIncomeToCommon', 'trailingEps', 'lastDividendValue', 'SandP52WeekChange', 'priceToBook', 'heldPercentInsiders', 'nextFiscalYearEnd', 'mostRecentQuarter', 'shortRatio', 'sharesShortPreviousMonthDate', 'floatShares', 'enterpriseValue', 'threeYearAverageReturn', 'lastSplitDate', 'lastSplitFactor', 'legalType', 'morningStarOverallRating', 'earningsQuarterlyGrowth', 'dateShortInterest', 'pegRatio', 'lastCapGain', 'shortPercentOfFloat', 'sharesShortPriorMonth', 'category', 'fiveYearAverageReturn', 'regularMarketPrice', 'logo_url']
SHARE_PRICE_COLUMNS = ['Date', 'Open', 'High', 'Low',  'Close' 'Volume' 'Dividends', 'Stock Splits']


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

market_info_df = None
share_price_df = None

def get_stock(a_stock):
    global market_info_df
    global share_price_df



    # Update the data with the current time
    dt = datetime.now()
    utc_time = dt#.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    def check_dataframe_exists(a_filepath, a_df, a_columns, a_index):
        # Save the stock information

        print("check_dataframe_exists({}, {}, {}, {})".format(a_filepath, a_df, a_columns, a_index))
        if a_df is None:
            if os.path.isfile(a_filepath):
                a_df = pd.read_csv(a_filepath, index_col=a_index, parse_dates=True)

            else:
                a_df = pd.DataFrame(columns=a_columns)
                a_df = a_df.set_index(a_index)

        return a_df

    def check_for_day_in_df( a_df):

        # Check if we need to add the record to the database
        _day_start = utc_time.replace(hour=0, minute=0, second=0, microsecond=0)
        _day_end = _day_start + timedelta(hours=24)

        print("_day_start: {}, _day_end: {}, _symbol: {}".format(_day_start, _day_end, msft.info['symbol']))

        _mask = (a_df.index >= _day_start) & (a_df.index < _day_end)
        _temp_df = a_df.loc[_mask]

        return _temp_df

    # Check we have a dataframe already in RAM, and if not check we have database file to load, otherwise create a new one
    market_info_df = check_dataframe_exists("csv/market_info.csv", market_info_df, _business_info, "timestamp")
    _market_info_df = market_info_df.copy()

    # Load the ticker
    msft = yfinance.Ticker(a_stock)

    # Add a timestamp to the ticker load
    msft.info['timestamp'] = utc_time.date()

    # Get only the data for the company selected
    _mask = (_market_info_df['symbol'] == msft.info['symbol'])
    _company_df = _market_info_df.loc[_mask]

    # Check if we have any company info stored for today
    _company_df = check_for_day_in_df(_company_df)

    # Update the dataframe
    if len(_company_df) == 0:
        print("We have no entry for {} stock for {}. Add to the database.".format(msft.info['symbol'], utc_time.date()))
        _market_info_df = _market_info_df.append(msft.info, ignore_index=True)
        _market_info_df.to_csv("csv/market_info.csv")

    else:
        print("We found {} entries.".format(len(_company_df)))

    #
    # Now we have the company info loaded and saved, lets get the share price
    #
    # Check we have a dataframe already in RAM, and if not check we have database file to load, otherwise create a new one
    #check_dataframe_exists("csv/share_prices/{}.csv".format(), share_price_df, SHARE_PRICE_COLUMNS, "Date")
    #_share_price_df = share_price_df.copy()

    # get historical market data
    hist = msft.history(period="1mo")
    #print(hist)

    # Safety mechanism to prevent accidental spamming of yfinance
    time.sleep(1)

    return hist

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

