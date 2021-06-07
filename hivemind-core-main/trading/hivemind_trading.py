# https://pythonrepo.com/repo/kirkthaker-investopedia-trading-api-python-third-party-apis-wrappers
from investopedia_simulator_api.investopedia_api import *
import os


class Investopedia:
    def __init__(self):
        self.username = os.environ.get("username")
        self.password = os.environ.get("password")
        self.credentials = {
            "username": self.username,
            "password": self.password
        }
        self.client = InvestopediaApi(self.credentials)

    def get_portfolio(self):
        print("Portfolio Infomation:")
        print("---------------------")
        # Read your portfolio
        long_positions  = self.client.portfolio.stock_portfolio
        short_positions = self.client.portfolio.short_portfolio
        my_options      = self.client.portfolio.option_portfolio
        account_balance = self.client.portfolio.account_value
        print("Long Position: {}\nShort Position: {}\nMy Options: {}\nAccount Balance: {}".format(
                                                                    long_positions,
                                                                    short_positions,
                                                                    my_options,
                                                                    account_balance))
        return self.client.portfolio

    def get_stock_info(self, stock_name):
        stock_info = self.client.get_stock_quote(stock_name).__dict__
        print("Stock Information:\n", stock_info)
        return stock_info

    def place_order(self,order_info):
        trade = self.client.StockTrade(
            order_info["stock_name"],
            order_info["quantity"],
            order_info["order_type"],
            order_type=OrderType.MARKET()
        )
        trade_info = trade.validate()
        if trade.validated:
            print("Trade Successful")
            print(trade_info)
            trade.execute()
            return trade_info
        return None

    def open_trade(self):
        open_trade = self.client.open_orders
        return open_trade
