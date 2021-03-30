import random
import time
from threading import Lock

import os
import re
import tweepy as tw
import pandas as pd
import json
from datetime import datetime
from time import strptime
from threading import Lock
import threading

from oauth2client.client import GoogleCredentials

# to authorize with the Google Drive API using OAuth 2.0
from oauth2client.service_account import ServiceAccountCredentials 
from google.oauth2 import service_account

from google.cloud import language_v1

import urllib.request  # the lib that handles the url stuff

class Google_API_Agent(object):
    def __init__(self):
        
        self.lock = Lock()
        print('Google lock has been setup')
        
        # credential for Google Drive and Google Sheets API
        self.google_json = 'https://drive.google.com/uc?export=view&id=1J2jcEdRJY1qprkBckoOG9-vYCGKvciGG'

        # credential for Google Cloud Natural Language API
        self.FinTechLab_json = 'https://drive.google.com/uc?export=view&id=1V6hI5PhXSQa29GlGZBt2ycIGyerSFuuV'

        self.Google_Spreadsheet_json = ""
        self.FinTechLab_KC_json = ""

        for line in urllib.request.urlopen(self.google_json):
            self.Google_Spreadsheet_json += line.decode('utf-8')

        for line in urllib.request.urlopen(self.FinTechLab_json):
            self.FinTechLab_KC_json += line.decode('utf-8')

        Google_Spreadsheet_json_res = json.loads(self.Google_Spreadsheet_json)
        FinTechLab_KC_json_res = json.loads(self.FinTechLab_KC_json) 

        # define the scope
        scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

        # Alternative: add credentials to the account, use Credential_for_Google_Spreadsheet.json content
        self.service_account_info_google_spreadsheet = Google_Spreadsheet_json_res
        self.service_account_info_FinTechLab = FinTechLab_KC_json_res

        credentials = service_account.Credentials.from_service_account_info(self.service_account_info_FinTechLab)

        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(self.service_account_info_google_spreadsheet, scope)
        self.language_client = language_v1.LanguageServiceClient(credentials=credentials,) # creating the language service client object

    def perform_google_sentiment_analysis(self):

        print(threading.currentThread().getName() + " --- ")
        self.lock.acquire()
        print('The google lock is acquired')
        
        tweets_dataset = pd.read_csv('bitcoin_tweets.csv')
        tweets_dataset['Sentiment Score'], tweets_dataset['Sentiment Magnitude'], tweets_dataset['Google Analyzer Label'] = zip(*tweets_dataset['Preproccessed Tweet Text'].apply(self.google_sentiment_analysis))
        tweets_dataset.to_csv('bitcoin_tweets.csv', index = False)

        self.lock.release()
        print('The google lock is released')        
        
    # this function used to send a tweet text to google api to get the score and magnitude
    def google_sentiment_analysis(self, content):
             
        document = language_v1.Document(content=content, type_=language_v1.Document.Type.PLAIN_TEXT)
        response = self.language_client.analyze_sentiment(document=document)

        # classify, based on the score, whether a text has a positive, neutral or negative sentiment (from lecture note)
        if response.document_sentiment.score >= 0.25 and response.document_sentiment.score <= 1:
            predicted_label = "positive"
            sentiment_score = response.document_sentiment.score
            sentiment_magnitude = response.document_sentiment.magnitude


        elif response.document_sentiment.score >= -0.25 and response.document_sentiment.score < 0.25:
            predicted_label = "neutral"
            sentiment_score = response.document_sentiment.score
            sentiment_magnitude = response.document_sentiment.magnitude

        else:
            predicted_label = "negative"
            sentiment_score = response.document_sentiment.score
            sentiment_magnitude = response.document_sentiment.magnitude

        return sentiment_score, sentiment_magnitude, predicted_label
       
## uncomment the following lines of code to test the agent
#if __name__ == '__main__':
#    google_api_object = Google_API_Agent()
