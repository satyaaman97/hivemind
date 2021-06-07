import numpy as np
import math
from datetime import date, datetime
from sentiment import SentimentAnalyzer
# from ticker_extractor import TickerExtractor
from db_utils import Mongo
import time
from pymongo import results
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler


class Preprocessor:
    def __init__(self, submission):
        self.submission = submission
        self.comments = submission['comments']
        self.comment_dict = {}
        self.analyzer = SentimentAnalyzer()
        self.ticker_extractor = None  # TickerExtractor('tickers.csv')

    def vectorize(self, post):
        numerical_keys = ['score', 'num_comments', 'upvote_ratio',
                          'ups', 'total_awards_received', 'downs',
                          'gilded', 'pos', 'neg', 'neu', 'title_pos', 'title_neg', 'title_neu']
        categorical_keys = ['distinguished', 'stickied']
        vector = [post[key] if key in post else 0 for key in numerical_keys]
        for key in categorical_keys:
            if key in post and post[key]:
                vector.append(1)
            else:
                vector.append(0)
        created_date = date.fromtimestamp(float(post['created_utc']))
        vector += [created_date.month, created_date.day, created_date.year]
        scaler = MinMaxScaler()

        return scaler.fit_transform(vector)

    def get_parent(self, parent_id):
        if parent_id in self.comment_dict:
            return self.comment_dict[parent_id]
        elif parent_id[:2] == 't3':
            return self.submission
        else:
            for comment in self.comments:
                if comment['id'] == parent_id:
                    self.comment_dict[parent_id] = comment
                    return comment
        return None

    def get_tickers(self, post):
        if 'tickers' in post:
            return post['tickers']
        tickers = []
        if 'body' in post:
            tickers += self.ticker_extractor.get_tickers(post['body'])
        if 'title' in post:
            tickers += self.ticker_extractor.get_tickers(post['title'])
        if tickers:
            post.update({'tickers': tickers})
            return tickers
        else:
            if post is self.submission:
                post.update({'tickers': []})
                return []
            else:
                parent_id = post['parent_id'][3:]
                parent = self.get_parent(parent_id)
                if parent:
                    tickers = self.get_tickers(parent)
                post.update({'tickers': tickers})
                return tickers

    def get_sentiment_score(self, post):
        scores = self.analyzer.post_sentiment(
            post['body'] if 'body' in post else '')
        is_comment = 'parent_id' in post
        if not is_comment:
            title_scores = self.analyzer.post_sentiment(
                post['title'] if 'title' in post else '')
            title_scores = {f'title_{k}': v for k, v in title_scores.items()}
            scores.update(title_scores)
        post.update(scores)

    def process_submission(self, l, stock_data, not_found):
        # self.get_tickers(self.submission)
        # self.get_sentiment_score(self.submission)
        if self.submission['tickers']:
            l.append({'vector': self.vectorize(self.submission),
                     'fitness': self.submission['fitness']})
        for comment in self.comments:
            # self.get_tickers(comment)
            # self.get_sentiment_score(comment)
            if comment['fitness'] != 0:
                l.append({'vector': self.vectorize(comment),
                         'fitness': comment['fitness']})

    def finalize(self, post, stock_data, not_found):
        add = {}

        add['fitness'] = self.get_fitness_value(post, stock_data, not_found)
        add['tickers'] = post['tickers']
        add['vector'] = self.vectorize(post)
        return add

    def sigmoid(self, n):
        try:
            return 2*(1/(1+math.exp(-0.1*n)))-1
        except OverflowError:
            if n < 1:
                return -1
            else:
                return 1

    def get_fitness_value(self, post, stock_data, not_found):
        tickers = post['tickers']
        if len(tickers) == 0:
            post.update({'fitness': 0})
            return 0
        timestamp = post['created_utc']
        start_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        end_date = datetime.fromtimestamp(
            int(timestamp) + (86400*5)).strftime("%Y-%m-%d")
        fit = 0
        for ticker in tickers:
            if ticker in stock_data:
                history = stock_data[ticker]
            else:
                if ticker not in not_found:
                    try:
                        t = yf.Ticker(ticker)
                        history = t.history(period='max')
                        stock_data[ticker] = history
                    except:
                        not_found.add(ticker)
                        continue
                else:
                    continue
            try:
                start_price = history.loc[start_date]["High"]
                end_price = history.loc[end_date]["High"]
                time_range = history.loc[start_date:end_date]
                fit += (time_range["High"].sum()-(len(time_range["High"])
                        * start_price))/(len(time_range["High"])-1)*100
            except KeyError:
                fit += 0
        fit = self.sigmoid(fit/len(tickers))
        post.update({'fitness': fit})
        return fit


if __name__ == '__main__':
    mc = Mongo()
    idx = 0
    all_submissions = list(mc['WSB']['vectors'].find(
        {'fitness': {'$ne': 0}}))
    l = []
    not_found = set([])
    stock_data = {}
    try:
        for submission in all_submissions:
            p = Preprocessor(submission)
            p.process_submission(l, stock_data, not_found)
            idx += 1
            print(idx)
            if idx % 1000 == 0:
                not_found.clear()
                stock_data.clear()

                with open('logfile', 'a') as f:
                    f.write(
                        f'vectorizing idx: {idx} Time: {time.strftime("%X %x")}\n')
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(
                f'Error Encountered: {str(e)} Time: {time.strftime("%X %x")}\n')

    coll = mc["WSB"]["inputs"]
    try:
        result = coll.insert_many(l)
        with open('logfile', 'a') as f:
            f.write(
                f'Wrote to vectors database: {len(result.inserted_ids)} entries Time: {time.strftime("%X %x")}\n')
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(
                f'Error Encountered: {str(e)} Time: {time.strftime("%X %x")}\n')
