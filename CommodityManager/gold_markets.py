# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

# Built in modules


# Third party modules


# Custom modules


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

START = 1
STABLE_MARKET = 2
VOLATILE_MARKET = 3
FINISHED = 4


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes

class Market():

    def __init__(self, location, currency):

        self.location = location
        self.currency = currency
        #self.raw_df = None
        self.stats_df = None

        self.buy_limit_mean = None
        self.buy_limit_mode = None
        self.buy_limit_std = None

        self.buy_quantity_mean = None
        self.buy_quantity_mode = None
        self.buy_quantity_std = None

        self.sell_limit_mean = None
        self.sell_limit_mode = None
        self.sell_limit_std = None

        self.sell_quantity_mean = None
        self.sell_quantity_mode = None
        self.sell_quantity_std = None

    def mask(self, a_df):
        _mask = (a_df['location'] == self.location) & (a_df['currency'] == self.currency)
        a_df = a_df.loc[_mask]

        return a_df

    def add_stats(self, a_df):
        a_df = self.mask(a_df)

        self.buy_limit_mean = a_df['buy_limit'].mean()
        self.buy_limit_mode = a_df['buy_limit'].mode()[0]
        self.buy_limit_std = a_df['buy_limit'].std()

        self.buy_quantity_mean = a_df['buy_quantity'].mean()
        self.buy_quantity_mode = a_df['buy_quantity'].mode()[0]
        self.buy_quantity_std = a_df['buy_quantity'].std()

        self.sell_limit_mean = a_df['sell_limit'].mean()
        self.sell_limit_mode = a_df['sell_limit'].mode()[0]
        self.sell_limit_std = a_df['sell_limit'].std()

        self.sell_quantity_mean = a_df['sell_quantity'].mean()
        self.sell_quantity_mode = a_df['sell_quantity'].mode()[0]
        self.sell_quantity_std = a_df['sell_quantity'].std()

    def __str__(self):
        return "Loc: {}, Cur: {}, Buy: ['Price': {:.1f}, 'Quantity: {:.1f}], Sell:  ['Price': {:.1f}, 'Quantity: {:.1f}]".format(
            self.location, self.currency,
            self.buy_limit_mean, self.buy_quantity_mean,
            self.sell_limit_mean, self.sell_quantity_mean)


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions

def calc_bollinger_bands(a_market):
    start_index = 0
    bollinger_high = a_market.raw_df['buy_limit'][0]
    bollinger_low = a_market.raw_df['buy_limit'][0]

    inside_bolinger = False
    state = START

    for index, row in a_market.raw_df.iterrows():

        if state == START:
            std = a_market.raw_df['buy_limit'].iloc[start_index:index].std()
            mean = a_market.raw_df['buy_limit'].iloc[start_index:index].mean()

            bollinger_high = mean + (std * 4)
            bollinger_low = mean - (std * 4)

            if index > start_index + 100:
                state = STABLE_MARKET

        elif state == STABLE_MARKET:
            if row['buy_limit'] > bollinger_high or row['buy_limit'] < bollinger_low:

                #print(index, "Boll high", row['buy_limit'], bollinger_high, std)
                start_index = index
                state = VOLATILE_MARKET

            else:
                # print("Boll high", row['buy_limit'], bollinger_high, std, index)

                std = a_market.raw_df['buy_limit'].iloc[start_index:index].std()
                mean = a_market.raw_df['buy_limit'].iloc[start_index:index].mean()

                bollinger_high = mean + (std * 4)
                bollinger_low = mean - (std * 4)

        elif state == VOLATILE_MARKET:
            if index > start_index + 5:
                vol_std = a_market.raw_df['buy_limit'].iloc[start_index:index].std()

                if vol_std < std:
                    #print(index, "vol std", vol_std, "std", std)
                    start_index = index
                    state = STABLE_MARKET


        elif state == FINISHED:
            pass

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main

