import random
import time
from threading import Thread,Lock
import threading
from datetime import datetime, timedelta

import os
import re
import tweepy as tw
import pandas as pd
import json
from datetime import datetime
from time import strptime
import threading
from oauth2client.client import GoogleCredentials

# to authorize with the Google Drive API using OAuth 2.0
from oauth2client.service_account import ServiceAccountCredentials 
from google.oauth2 import service_account

from google.cloud import language_v1
from constants import tick_time, tweeter_time

import urllib.request  # the lib that handles the url stuff

# TextBlob - Python library for processing textual data
from textblob import TextBlob

# WordCloud - Python linrary for creating image wordclouds
from wordcloud import WordCloud

# Matplotlib - plotting library to create graphs and charts
import matplotlib.pyplot as plt

# Settings for Matplotlib graphs and charts
from pylab import rcParams
rcParams['figure.figsize'] = 12, 8

class Tweepy_Agent(object):
    
    def __init__(self):
        self.lock = Lock()
        self.consumer_key = 'lk0gKzRSdUw5WkxnylvcPKFE2'
        self.consumer_secret = 'lSkwjt4HMKzOCP4qIvQHFa0Ea91p1kmlLN6VXhFpuQdTyfPUFu'
        self.access_token = '1375962232270381057-lcxpR8AGSHkrTfPbvTnqZdKVuPegCB'
        self.access_token_secret = 'i5eZt2UPFARPwcKlqacVuDy7fgCxpCoObWL6YDP1U33le'

        # Authenticate to Twitter / authorize twitter, initialize tweepy
        # Create API object that we are going to use it to fetch the tweets
        self.auth = tw.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tw.API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.get_all_tweets_search()
            time.sleep(tweeter_time)
            
    # https://gist.github.com/yanofsky/5436496
    def get_all_tweets_account_name(self):
        
        self.lock.acquire()
        alltweets = [] # initialize a list to hold all the tweepy Tweets
        screen_name = 'whale_alert'
   
        #make initial request for most recent tweets (200 is the maximum allowed count)
        # new_tweets = self.api.user_timeline(screen_name = screen_name ,count=200)
        all_tweets = tw.Cursor(self.api.user_timeline, 
                                screen_name=screen_name, 
                                count=None,
                                since_id=None,
                                max_id=None,
                                #trim_user=True,
                                exclude_replies=True,
                                contributor_details=False,
                                include_entities=False
                                ).items(200);

        df_list = []
        for tweet in all_tweets:
            created_at = tweet.created_at; tweet_id = tweet.id_str; text = tweet.text
            fullname = tweet.user.name; screenname = tweet.user.screen_name; favorite_count = tweet.favorite_count
            retweet_count = tweet.retweet_count; follower_count = tweet.user.followers_count; follow_count = tweet.user.friends_count
            verified = tweet.user.verified; location = tweet.user.location; bio = tweet.user.description; user_since = tweet.user.created_at
            
            df_list.append({'Date': created_at, 'Tweet ID': tweet_id, 'Tweet Text': str(text),'Full Name': str(fullname),
                                 'Screen Name': '@' + str(screenname),'favorite_count': int(favorite_count),'Retweets': int(retweet_count),
                                 'Followers': int(follower_count),'Follows': int(follow_count),'Verified' : str(verified),
                                 'User Since': user_since,'Location': location,'bio': bio
                                 })
                       
        #save the id of the oldest tweet less one
        oldest = int(df_list[-1]['Tweet ID']) - 1
        
        #keep grabbing tweets until there are no tweets left to grab
        while (len(df_list) < 200):
            print(f"getting tweets before {oldest}")
            #all subsiquent requests use the max_id param to prevent duplicates
            all_tweets = tw.Cursor(self.api.user_timeline, 
                                    screen_name=screen_name, 
                                    count=None,
                                    since_id=None,
                                    max_id=oldest,
                                    #trim_user=True,
                                    exclude_replies=True,
                                    contributor_details=False,
                                    include_entities=False
                                    ).items(200);            
            for tweet in all_tweets:
                created_at = tweet.created_at; tweet_id = tweet.id_str; text = tweet.text
                fullname = tweet.user.name; screenname = tweet.user.screen_name; favorite_count = tweet.favorite_count
                retweet_count = tweet.retweet_count; follower_count = tweet.user.followers_count; follow_count = tweet.user.friends_count
                verified = tweet.user.verified; location = tweet.user.location; bio = tweet.user.description; user_since = tweet.user.created_at
                
                #'created_day': created_day,'created_dd': created_dd,'created_mmm': created_mmm,
                #'created_yyyy': created_yyyy,'created_time': created_time,
                df_list.append({'Date': created_at, 'Tweet ID': tweet_id, 'Tweet Text': str(text),'Full Name': str(fullname),
                                     'Screen Name': '@' + str(screenname),'Favorite_count': int(favorite_count),'Retweets': int(retweet_count),
                                     'Followers': int(follower_count),'Follows': int(follow_count),'Verified' : str(verified),
                                     'User Since': user_since,'Location': location,'Bio': bio
                                     })
                           
            oldest = int(df_list[-1]['Tweet ID']) - 1
            print(f"...{len(df_list)} tweets downloaded so far")



            
        # 'created_day', 'created_dd', 'created_mmm', 'created_yyyy','created_time',    
        tweet_df = pd.DataFrame(df_list, columns = ['Date','Tweet ID', 'Tweet Text', 'Full Name', 'Screen Name',
                                                          'Favorite_count', 'Retweets', 'Followers','Follows', 'Verified',
                                                           'User Since', 'Location', 'Bio']) 

        # sentiment analysis
        tweet_df['Preproccessed Tweet Text'] = tweet_df['Tweet Text'].apply(self.clean_up_tweet)
        tweet_df['Subjectivity'] = tweet_df['Preproccessed Tweet Text'].apply(self.get_text_subjectivity)
        tweet_df['Polarity'] = tweet_df['Preproccessed Tweet Text'].apply(self.get_text_polarity)
        tweet_df = tweet_df.drop(tweet_df[tweet_df['Preproccessed Tweet Text'] == ''].index)
        tweet_df['Label'] = tweet_df['Polarity'].apply(self.get_text_analysis)
        
        # self.get_word_cloud_analysis(tweet_df)
        
        tweet_df.to_csv(f'./local_db/tweet_data/{screen_name}_tweets.csv', index = False)
        
        self.lock.release()
        
        
    def get_all_tweets_search(self):
        
        self.lock.acquire()
        print('The tweepy lock has been acquired')
        
        search_words = 'bitcoin OR cryptocurrency OR #bitcoin OR #cryptocurrency' # Define the search term and the date_since date as variables
        date_since = datetime.now() 
        #date_until = datetime.now() - timedelta(1)

        date_since = datetime.strftime(date_since, '%Y-%m-%d')
        #date_until = datetime.strftime(date_until, '%Y-%m-%d')
        
        # Collect tweets
        all_tweets = tw.Cursor(self.api.search,
                      q=search_words,
                      result_type='recent',
                      lang="en", since=date_since).items(200)
        
        df_list = []
        for tweet in all_tweets:
            created_at = tweet.created_at; tweet_id = tweet.id_str
            text = tweet.text; fullname = tweet.user.name; screenname = tweet.user.screen_name
            favorite_count = tweet.favorite_count; retweet_count = tweet.retweet_count
            follower_count = tweet.user.followers_count; follow_count = tweet.user.friends_count
            verified = tweet.user.verified; location = tweet.user.location
            bio = tweet.user.description; user_since = tweet.user.created_at
            
            df_list.append({'Date': created_at, 'Tweet ID': str(tweet_id), 'Tweet Text': str(text),'Full Name': str(fullname),
                                 'Screen Name': '@' + str(screenname),'Favorite_count': int(favorite_count),'Retweets': int(retweet_count),
                                 'Followers': int(follower_count),'Follows': int(follow_count),'Verified' : str(verified),
                                 'User Since': user_since,'Location': location,'Bio': bio
                                 })
            
        #save the id of the oldest tweet less one
        oldest = int(df_list[-1]['Tweet ID']) - 1

        #keep grabbing tweets until there are no tweets left to grab
        while (len(df_list) < 200):
            print(f"getting tweets before {oldest}")
            # Collect tweets
            all_tweets = tw.Cursor(self.api.search,
                          q=search_words,
                          lang="en",
                          since=date_since).items(200)
            
            for tweet in all_tweets:
                created_at = tweet.created_at; tweet_id = tweet.id_str
                text = tweet.text; fullname = tweet.user.name; screenname = tweet.user.screen_name
                favorite_count = tweet.favorite_count; retweet_count = tweet.retweet_count
                follower_count = tweet.user.followers_count; follow_count = tweet.user.friends_count
                verified = tweet.user.verified; location = tweet.user.location
                bio = tweet.user.description; user_since = tweet.user.created_at
                
                df_list.append({'Date': created_at, 'Tweet ID': str(tweet_id), 'Tweet Text': str(text),'Full Name': str(fullname),
                                     'Screen Name': '@' + str(screenname),'Favorite_count': int(favorite_count),'Retweets': int(retweet_count),
                                     'Followers': int(follower_count),'Follows': int(follow_count),'Verified' : str(verified),
                                     'User Since': user_since,'Location': location,'Bio': bio
                                     })
                
            oldest = int(df_list[-1]['Tweet ID']) - 1
            print(oldest)
            print(f"...{len(df_list)} tweets downloaded so far")
            
        tweet_df = pd.DataFrame(df_list, columns = ['Date','Tweet ID', 'Tweet Text', 'Full Name', 'Screen Name',
                                                          'Favorite_count', 'Retweets', 'Followers','Follows', 'Verified',
                                                           'User Since', 'Location', 'Bio'])

        tweet_df['Preproccessed Tweet Text'] = tweet_df['Tweet Text'].apply(self.clean_up_tweet)
        tweet_df['Subjectivity'] = tweet_df['Preproccessed Tweet Text'].apply(self.get_text_subjectivity)
        tweet_df['Polarity'] = tweet_df['Preproccessed Tweet Text'].apply(self.get_text_polarity)
        tweet_df = tweet_df.drop(tweet_df[tweet_df['Preproccessed Tweet Text'] == ''].index)
        tweet_df['Label'] = tweet_df['Polarity'].apply(self.get_text_analysis)
        
        # self.get_word_cloud_analysis(tweet_df)
        
        tweet_df.to_csv(f'./local_db/tweet_data/bitcoin_tweets.csv', index=False)

        self.lock.release()
        print('The tweepy lock has been released')
                    
    # Cleaning the tweets
    # https://github.com/pjwebdev/Basic-Data-Science-Projects/blob/master/8-Twitter-Sentiment-Analysis/Tweeter%20Sentiment%20Analysis.ipynb
    def clean_up_tweet(self, txt):
        # Remove mentions
        txt = re.sub(r'@[A-Za-z0-9_]+', '', txt)
        # Remove hashtags
        txt = re.sub(r'#', '', txt)
        # Remove retweets:
        txt = re.sub(r'RT : ', '', txt)
        # Remove urls
        txt = re.sub(r'https?:\/\/[A-Za-z0-9\.\/]+', '', txt)
        return txt

    def get_text_subjectivity(self, txt):
        return TextBlob(txt).sentiment.subjectivity

    def get_text_polarity(self, txt):
        return TextBlob(txt).sentiment.polarity

    # categorize our tweets as Negative, Neutral and Positive.
    def get_text_analysis(self, polarity):
        if (polarity < 0 and polarity > -0.5):
            return "Negative"
        elif polarity <= -0.5:
            return "Highly Negative"
        elif polarity == 0:
            return "Neutral"
        elif (polarity > 0 and polarity < 0.5):
            return "Positive"
        else:
            return "Highly Positive"

    # categorize our tweets as Negative, Neutral and Positive.
    def get_word_cloud_analysis(self, tweet_df):
        # Creating a word cloud
        words = ' '.join([tweet for tweet in tweet_df['Preproccessed Tweet Text']])
        wordCloud = WordCloud(width=600, height=400).generate(words)

        plt.imshow(wordCloud)
        plt.show()

    def __str__(self):
        return 'tweepy_agent'
    
if __name__ == '__main__':
    tweepy_object = Tweepy_Agent()
