from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk import tokenize
import regex
import json


class SentimentAnalyzer:
    def __init__(self):
        with open('../../data/added_words.json', 'r') as f:
            words_dict = json.loads(f.read())
        self.analyzer = SentimentIntensityAnalyzer()
        self.analyzer.lexicon.update(words_dict)
        self.put_regex = r'(\b\d{1,4}(\.\d{0,2})?[ ]?[p]\b)'
        self.call_regex = r'(\b\d{1,4}(\.\d{0,2})?[ ]?[c]\b)'

    def post_sentiment(self, post_text):
        sentences = tokenize.sent_tokenize(post_text)
        l = len(sentences)
        scores = {'pos': 0.0, 'neg': 0.0, 'neu': 0.0}
        for sentence in sentences:
            # replacing words such as 300c or 412p with call or put
            # which the model has known weight for
            sentence = regex.sub(self.call_regex, 'call', sentence)
            sentence = regex.sub(self.put_regex, 'put', sentence)
            polarity_score = self.analyzer.polarity_scores(sentence)
            # averaging out sentiment for all sentences in text
            scores = {key: val+(polarity_score[key]/l)
                      for key, val in scores.items()}
        return scores
