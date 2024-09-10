import pandas as pd
import gymnasium as gym
from gym_anytrading.envs import TradingEnv, Actions, Positions, StocksEnv
from trader_bot.utils.logger import logging
from enum import Enum
import numpy as np


def add_signals(env):
    start = env.frame_bound[0]-env.window_size
    end = env.frame_bound[1]
    prices = env.df.loc[:,'low'].to_numpy()[start:end]
    # signal_features = env.df.loc[:,['low','volume','SMA','RSI','OBV']].to_numpy()[start:end]


    patterns = ['macd', 'boll', 'rsi','low','volume']
    # Combine patterns into a single regular expression
    regex_pattern = '|'.join(patterns)
    # Filter columns based on the combined pattern
    regex_pattern = '^(' + '|'.join(patterns) + ')'
    # Filter columns based on the combined pattern
    selected_columns = env.df.filter(regex=regex_pattern)
    logging.info(f"Load data with selected features: {selected_columns.columns}")
    

    # ['Close','volume','close_14_sma',	'close_30_sma',	'close_7_sma','rsi_30'	]
    signal_features = selected_columns.to_numpy()[start:end]
    return prices,signal_features

def custom_update_profit(env, action):
    trade = False
    if (
        (action == Actions.Buy.value and env._position == Positions.Short) or
        (action == Actions.Sell.value and env._position == Positions.Long)
    ):
        trade = True

    if trade or env._truncated:
        current_price = env.prices[env._current_tick]
        last_trade_price = env.prices[env._last_trade_tick]


        if env._position == Positions.Long:
            shares = (env._total_profit * (1 - env.trade_fee_ask_percent)) / last_trade_price
            env._total_profit = (shares * (1 - env.trade_fee_bid_percent)) * current_price


class StockEnvironment(TradingEnv):

    def __init__(self, df, window_size, frame_bound, render_mode=None):
        assert len(frame_bound) == 2

        self.frame_bound = frame_bound
        super().__init__(df, window_size, render_mode)

        self.trade_fee_bid_percent = 0.0  # unit
        self.trade_fee_ask_percent = 0.0  # unit

    def _process_data(self):
        start = self.frame_bound[0]-self.window_size
        end = self.frame_bound[1]
        prices = self.df.loc[:,'low'].to_numpy()[start:end]
        # signal_features = env.df.loc[:,['low','volume','SMA','RSI','OBV']].to_numpy()[start:end]


        patterns = ['macd', 'boll', 'rsi','low','volume']
        # Combine patterns into a single regular expression
        regex_pattern = '|'.join(patterns)
        # Filter columns based on the combined pattern
        regex_pattern = '^(' + '|'.join(patterns) + ')'
        # Filter columns based on the combined pattern
        selected_columns = self.df.filter(regex=regex_pattern)
        logging.info(f"Load data with selected features: {selected_columns.columns}")
        

        # ['Close','volume','close_14_sma',	'close_30_sma',	'close_7_sma','rsi_30'	]
        signal_features = selected_columns.to_numpy()[start:end]
        return prices,signal_features

    def _calculate_reward(self, action):
        step_reward = 0

        trade = False
        if (
            (action == Actions.Buy.value and self._position == Positions.Short) or
            (action == Actions.Sell.value and self._position == Positions.Long)
        ):
            trade = True

        if trade or self._truncated:
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]
            price_diff = current_price - last_trade_price

            if self._position == Positions.Long:
                step_reward += price_diff
        
        # if self._truncated:
        #     current_price = self.prices[self._current_tick]
        #     setp_reward += (self._total_profit-1) * current_price

        return step_reward

    def _update_profit(self, action):
        trade = False
        if (
            (action == Actions.Buy.value and self._position == Positions.Short) or
            (action == Actions.Sell.value and self._position == Positions.Long)
        ):
            trade = True

        if trade or self._truncated:
            current_price = self.prices[self._current_tick]
            last_trade_price = self.prices[self._last_trade_tick]

            if self._position == Positions.Long:
                shares = (self._total_profit * (1 - self.trade_fee_ask_percent)) / last_trade_price
                self._total_profit = (shares * (1 - self.trade_fee_bid_percent)) * current_price

    def max_possible_profit(self):
        current_tick = self._start_tick
        last_trade_tick = current_tick - 1
        profit = 1.

        while current_tick <= self._end_tick:
            position = None
            if self.prices[current_tick] < self.prices[current_tick - 1]:
                while (current_tick <= self._end_tick and
                       self.prices[current_tick] < self.prices[current_tick - 1]):
                    current_tick += 1
                position = Positions.Short
            else:
                while (current_tick <= self._end_tick and
                       self.prices[current_tick] >= self.prices[current_tick - 1]):
                    current_tick += 1
                position = Positions.Long

            if position == Positions.Long:
                current_price = self.prices[current_tick - 1]
                last_trade_price = self.prices[last_trade_tick]
                shares = profit / last_trade_price
                profit = shares * current_price
            last_trade_tick = current_tick - 1

        return profit

class StockEnvironment1(StocksEnv):
    _process_data = add_signals
    # _update_profit= custom_update_profit
        