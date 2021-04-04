import random
import time
from threading import Thread,Lock
from constants import tick_time, fuzzy_time
import threading

import os
import re
import tweepy as tw
import pandas as pd
import numpy as np
import json
from datetime import datetime
from google_api_agent import *

# pip install scikit_Fuzzy
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class Fuzzy_Logic_Agent():
    
    def __init__(self):
        self.lock = Lock()
        self.signals = []
        self.positive_percent = 0
        self.neural_percent = 0
        self.negative_percent = 0
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.perform_fuzzy_logic()
            time.sleep(tick_time)
            
    def perform_fuzzy_logic(self):

        # perform sentiment analysis
        google_api_object = Google_API_Agent()
        google_api_object.perform_google_sentiment_analysis()
        
        self.positive_percent = google_api_object.positive_percent
        self.neural_percent = google_api_object.neural_percent
        self.negative_percent = google_api_object.negative_percent
        
        self.lock.acquire()
        print('The fuzzy logic lock has been acquired')

        tweets_sentiment = pd.read_csv('./local_db/tweet_data/bitcoin_tweets.csv')
        self.fuzzy_logic(tweets_sentiment)
        
        self.lock.release()
        print('The fuzzy logic lock has been released')
        
    # func: fuzzy logic for tweets data
    def fuzzy_logic(self, df_tweet_sentiment):
        
        total_tweets = len(df_tweet_sentiment)
        total_score = df_tweet_sentiment['Sentiment Score'].sum()
        total_magnitude = df_tweet_sentiment['Sentiment Magnitude'].sum()
        average_score = total_score / total_tweets
        average_magnitude = total_magnitude / total_tweets

        # The universe set for tweet length is between -1 to 1 with step 0.1, for the sentiment is between 0 to 1 with step 0.1
        score = ctrl.Antecedent(np.arange(-1, 2, 0.1), 'score')

        # The universe set for tweet length is between 0 to 10 with step 0.1, for the sentiment is between 0 to 1 with step 0.1
        magnitude = ctrl.Antecedent(np.arange(0, 11, 0.1), 'magnitude')

        # the usefulness is graded in anything between 0 to 100 with step 0.5
        recs = ctrl.Consequent(np.arange(0, 101, 0.5), 'recs')

        # Auto-membership function population is possible with .automf(3, 5, or 7) or list of the names of your Terms i.e. ['poor', 'average', 'good']
        score.automf(3)
        magnitude.automf(3)
        recs.automf(3)

        # antecedent: list of score, list of magnitude
        # consequent: buy, if sentiment is good and sell if sentiment is bad        
        # Create the rules that will maps between the antecendents (score and magnitude) and consequence (usefulness grade)
        rule1 = ctrl.Rule(antecedent=(score['poor']), consequent=recs['poor'], label='rule1')
        rule2 = ctrl.Rule(antecedent=(score['average'] & magnitude['poor']), consequent=recs['poor'], label='rule2')
        rule3 = ctrl.Rule(antecedent=(score['average'] & magnitude['average']), consequent=recs['average'], label='rule3')
        rule4 = ctrl.Rule(antecedent=(score['average'] & magnitude['good']), consequent=recs['average'], label='rule4')
        rule5 = ctrl.Rule(antecedent=(score['good'] & magnitude['poor']), consequent=recs['average'], label='rule5')
        rule6 = ctrl.Rule(antecedent=(score['good'] & magnitude['average']), consequent=recs['good'], label='rule6')
        rule7 = ctrl.Rule(antecedent=(score['good'] & magnitude['good']), consequent=recs['good'], label='rule7')

        sentiment_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
        sentiment = ctrl.ControlSystemSimulation(sentiment_ctrl)

        # # Assign the value of tweet into the input
        sentiment.input['score'] = average_score
        sentiment.input['magnitude'] = average_magnitude

        # Crunch the numbers
        sentiment.compute()

        recommendation = sentiment.output['recs']
        print('recommendation:', recommendation)

        # We make the cutoff for recommendation score as 30
        if (recommendation >= 30 and self.positive_percent >= 0.40):
            self.signals.append(1)
        elif (recommendation < 30 and self.negative_percent >= 0.40):
            self.signals.append(-1)
        else:
            self.signals.append(0)

    def peek(self):
        self.lock.acquire()
        signal = 0
        if len(self.signals)>0:
            signal = self.signals[-1]
        self.lock.release()
        return signal

    def __str__(self):
        return 'fuzzy_logic_agent'
    
#if __name__ == '__main__':
#    fuzzy_logic_object = Fuzzy_Logic_Agent()
#    fuzzy_logic_object.perform_fuzzy_logic()
