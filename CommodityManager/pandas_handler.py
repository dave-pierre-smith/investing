# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules
import logging
from datetime import timedelta
import time

# Third party modules
import pandas as pd

# Custom modules


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Markets
GOLD_LOCATIONS = ('AUXZU', 'AUXLN', 'AUXNY', 'AUXTR', 'AUXSG')
CURRENCIES = ('USD', 'GBP', 'EUR', 'YEN')


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Dash Layout
# %% Must be called before the callback functions as the decorators need the layout to determine the inputs


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes




# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def resample_bullion_dataframe(a_df):
    """:arg
    [Unnamed: 0	id	timestamp	location	currency	buy_quantity	buy_limit	sell_quantity	sell_limit]

    Dataframe has the above columns. Needs sorting into individual locations & currencies before resampling and concat
    back together with a sort to finish it off.
    """
    _master_df = a_df.copy()
    _dfs = []

    for _location in GOLD_LOCATIONS:

        for _currency in CURRENCIES:

            _temp_df = _master_df.loc[(_master_df['location'] == _location) & (_master_df['currency'] == _currency)]
            _temp_df = _temp_df.resample(timedelta(days=1), on="timestamp").mean()
            #_series = pd.series([_location for x in range(len(_temp_df))])
            _temp_df['location'] = _location
            _temp_df['currency'] = _currency
            _temp_df = _temp_df.reset_index()
            #print("_temp_df len: {} after resampling".format(len(_temp_df)))
            #print("_temp_df len: {}".format(len(_temp_df)))

            _dfs.append(_temp_df)

            #time.sleep(100)

    _return_df = pd.concat(_dfs, sort=False)
    _return_df.to_csv("csv/dave2.csv")

    _cols = _return_df.columns

    for _col in _cols:

        if _col not in ['buy_limit', 'buy_quantity', 'currency', 'location', 'sell_limit', 'sell_quantity', 'timestamp']:
            print("Dropping: {}".format(_col))
            _return_df = _return_df.drop(columns=[_col])

    return _return_df


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

