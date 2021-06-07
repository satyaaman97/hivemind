# tickers.csv obtained from a github repo:
# https://github.com/shilewenuw/get_all_tickers/tree/master/get_all_tickers

import reticker


class TickerExtractor:
    def __init__(self, csv_filename):
        self.csv_filename = csv_filename
        self.stocks = {}
        self.extractor = reticker.TickerExtractor()
        self.read()

    def read(self):
        with open(self.csv_filename) as f:
            for line in f:
                ticker, name = line.split(',')
                self.stocks[ticker] = name

    def get_tickers(self, text):
        return [ticker for ticker in self.extractor.extract(text) if ticker in self.stocks]

    def get_name(self, ticker):
        if ticker in self.stocks:
            return self.stocks[ticker]
        else:
            return None
