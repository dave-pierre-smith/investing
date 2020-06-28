#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 19 11:57:26 2018

@author: davesmith
"""

# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Imports

from datetime import datetime, timedelta
import time

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import pandas as pd


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Constants

Base = declarative_base()

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
ENGINE = create_engine('sqlite:///databases/metal.db')


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Classes

class GoldMarket(Base):
    '''

    '''
    __tablename__ = 'gold_market'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    location = Column(String(5))
    currency = Column(String(3))
    buy_quantity = Column(Float(precision=5, asdecimal=True))
    buy_limit = Column(Integer)
    sell_quantity = Column(Float(precision=5, asdecimal=True))
    sell_limit = Column(Integer)

    def update_info(self, timestamp, location, currency):
        self.timestamp = timestamp
        self.location = location
        self.currency = currency

    def update_buy(self, quantity, limit):
        self.buy_quantity = quantity
        self.buy_limit = limit

    def update_sell(self, quantity, limit):
        self.sell_quantity = quantity
        self.sell_limit = limit


class GoldFeaturesDaily(Base):
    '''

    '''
    __tablename__ = 'gold_features_daily'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    location = Column(String(5))
    currency = Column(String(3))

    buy_limit_mean = Column(Float(precision=2, asdecimal=True))
    buy_limit_mode = Column(Integer)
    buy_limit_std = Column(Float(precision=2, asdecimal=True))

    buy_quantity_mean = Column(Float(precision=2, asdecimal=True))
    buy_quantity_mode = Column(Integer)
    buy_quantity_std = Column(Float(precision=2, asdecimal=True))

    sell_limit_mean = Column(Float(precision=2, asdecimal=True))
    sell_limit_mode = Column(Integer)
    sell_limit_std = Column(Float(precision=2, asdecimal=True))

    sell_quantity_mean = Column(Float(precision=2, asdecimal=True))
    sell_quantity_mode = Column(Integer)
    sell_quantity_std = Column(Float(precision=2, asdecimal=True))

    def __init__(self, timestamp, location, currency, dataframe):
        self.timestamp = timestamp
        self.location = location
        self.currency = currency

        self.buy_limit_mean = dataframe['buy_limit'].mean()
        self.buy_limit_mode = dataframe['buy_limit'].mode()[0]
        self.buy_limit_std = dataframe['buy_limit'].std()

        self.buy_quantity_mean = dataframe['buy_quantity'].mean()
        self.buy_quantity_mode = dataframe['buy_quantity'].mode()[0]
        self.buy_quantity_std = dataframe['buy_quantity'].std()

        self.sell_limit_mean = dataframe['sell_limit'].mean()
        self.sell_limit_mode = dataframe['sell_limit'].mode()[0]
        self.sell_limit_std = dataframe['sell_limit'].std()

        self.sell_quantity_mean = dataframe['sell_quantity'].mean()
        self.sell_quantity_mode = dataframe['sell_quantity'].mode()[0]
        self.sell_quantity_std = dataframe['sell_quantity'].std()


# %% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Functions


def create_database():
    '''
    Create all tables in the engine. This is equivalent to "Create Table"
    statements in raw SQL.
    '''
    Base.metadata.create_all(ENGINE)


def insert(table):
    '''
    Add an entry to the database
    '''
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    DBSession = sessionmaker(bind=ENGINE)

    # A DBSession() instance establishes all conversations with the database
    # and represents a "staging zone" for all the objects loaded into the
    # database session object. Any change made against the objects in the
    # session won't be persisted into the database until you call
    # session.commit(). If you're not happy about the changes, you can
    # revert all of them back to the last commit by calling
    # session.rollback()
    session = DBSession()
    session.add(table)
    session.commit()


def delete(table):
    DBSession = sessionmaker(bind=ENGINE)
    session = DBSession()

    session.query(table).delete()

    session.commit()


def info(table, ts=None, location=None, currency=None):
    '''
    Return the number of rows in the table
    '''
    DBSession = sessionmaker(bind=ENGINE)
    session = DBSession()

    if ts and location is None and currency is None:
        return session.query(table).filter(table.timestamp == ts).count()

    elif location is not None and currency is not None:
        return (session.query(table).filter(table.timestamp == ts)
                .filter(table.location == location)
                .filter(table.currency == currency).count())

    else:
        return session.query(table).count()


def first_row(table):
    '''
    Get the first row in the database
    '''
    DBSession = sessionmaker(bind=ENGINE)
    session = DBSession()

    # Return the first Person from all Persons in the database
    first_time = session.query(table).first()

    return first_time.timestamp


def to_pandas(table, start_time, end_time,
                       location=None, currency=None):
    '''
    Get the data from the tables and return a dataframe
    '''
    DBSession = sessionmaker(bind=ENGINE)
    session = DBSession()

    # Build the query
    if location is None and currency is None:
        query = session.query(table)   \
            .filter(table.timestamp >= start_time) \
            .filter(table.timestamp <= end_time).statement

    elif location is None:
        query = session.query(table)   \
            .filter(table.timestamp >= start_time) \
            .filter(table.timestamp <= end_time)   \
            .filter(table.currency == currency).statement

    elif currency is None:
        query = session.query(table)   \
            .filter(table.timestamp >= start_time) \
            .filter(table.timestamp <= end_time)   \
            .filter(table.location == location).statement

    else:
        query = session.query(table)   \
            .filter(table.timestamp >= start_time) \
            .filter(table.timestamp <= end_time)   \
            .filter(table.currency == currency)    \
            .filter(table.location == location).statement

    df = pd.read_sql(query, session.bind)

    return df

