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

import gspread # Python API used to interact with Google Spreadsheets
from gspread_dataframe import set_with_dataframe
from apiclient.discovery import build

from oauth2client.client import GoogleCredentials
# to authorize with the Google Drive API using OAuth 2.0
from oauth2client.service_account import ServiceAccountCredentials 
from google.oauth2 import service_account
from google.cloud import language_v1

import urllib.request  # the lib that handles the url stuff

class Google_API_Agent(object):
    
    def __init__(self):
        
        self.lock = Lock()

        self.positive_percent = 0
        self.neural_percent = 0
        self.negative_percent = 0
        
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
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(self.service_account_info_google_spreadsheet, scope)
        
        self.drive_service = build("drive", "v3", credentials=self.creds) # define API service
        self.gc = gspread.authorize(self.creds) # authorize the gspread client sheet

        # Credentials for Google Cloud Natural Language API
        self.service_account_info_FinTechLab = FinTechLab_KC_json_res
        self.creds_FinTechLab = service_account.Credentials.from_service_account_info(self.service_account_info_FinTechLab)
        self.language_client = language_v1.LanguageServiceClient(credentials=self.creds_FinTechLab,) # creating the language service client object

    # For more information: https://medium.com/@CROSP/manage-google-spreadsheets-with-python-and-gspread-6530cc9f15d1
    # create (C) a new Google Sheets
    def create_google_sheets(self, gs_name):
        sh = self.gc.create(gs_name)
        worksheet = sh.worksheet('Sheet1')
        print('The Google Sheets has been created!')

    # read (R) a Google Sheets into DataFrame
    def read_google_sheets(self, gs_name):
        sh = self.gc.open(gs_name)
        worksheet = sh.worksheet('Sheet1')
        data = worksheet.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        print('The DataFrame has been read!')
        return df

    # write (W) a Google Sheets
    def write_google_sheets(self, gs_name, df_input):
        try:
            sh_agent = self.gc.open(gs_name)
            worksheet = sh_agent.worksheet('Sheet1')
            set_with_dataframe(worksheet, df_input)
            file_id_agent = sh_agent.id
            permission_agent = {
                'type': 'anyone',
                'role': 'writer',
            }
            res_agent = (self.drive_service.permissions().create(fileId=file_id_agent, body=permission_agent).execute())
            sharable_url_agent = "https://drive.google.com/file/d/" + file_id_agent + "/edit"
            print(sharable_url_agent)
        except:
            print('An error occurred')

    # append (U) to a Google Sheets
    def append_google_sheets(self, gs_name, new_row):
        try:
            sh_agent = self.gc.open(gs_name)
            worksheet = sh_agent.sheet1
            
            file_id_agent = sh_agent.id
            permission_agent = {
                'type': 'anyone',
                'role': 'writer',
            }
            res_agent = (self.drive_service.permissions().create(fileId=file_id_agent, body=permission_agent).execute())
            sharable_url_agent = "https://drive.google.com/file/d/" + file_id_agent + "/edit"
            try:          
                new_row[-1] = new_row[-1].to_pydatetime().strftime("%d-%m-%Y %H:%M:%S")
                print('ohA')
            except:       
                new_row[-2] = new_row[-2].to_pydatetime().strftime("%d-%m-%Y %H:%M:%S")
                print('ohB')
                
            worksheet.append_row(new_row)
            print(sharable_url_agent)
        except:
            print('An error occurred')
            
    def perform_google_sentiment_analysis(self):

        self.lock.acquire()
        print('The google lock is acquired\n')
        
        tweets_dataset = pd.read_csv('./local_db/tweet_data/bitcoin_tweets.csv')
        tweets_dataset['Sentiment Score'], tweets_dataset['Sentiment Magnitude'], tweets_dataset['Google Analyzer Label'] = zip(*tweets_dataset['Preproccessed Tweet Text'].apply(self.google_sentiment_analysis))

        positive = tweets_dataset[tweets_dataset['Google Analyzer Label'] == 'positive']
        self.positive_percent = positive.shape[0]/(tweets_dataset.shape[0])
        print(self.positive_percent)

        neutral = tweets_dataset[tweets_dataset['Google Analyzer Label'] == 'neutral']
        self.neural_percent = neutral.shape[0]/(tweets_dataset.shape[0])
        print(self.neural_percent)
        
        negative = tweets_dataset[tweets_dataset['Google Analyzer Label'] == 'negative']
        self.negative_percent = negative.shape[0]/(tweets_dataset.shape[0])
        print(self.negative_percent)

        tweets_dataset.to_csv('./local_db/tweet_data/bitcoin_tweets.csv', index = False)

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
    #gs_name = 'G7'
    #google_api_object = Google_API_Agent()
    #google_api_object.perform_google_sentiment_analysis()
    #tweet_df_processed = pd.read_csv('./local_db/bitcoin_tweets.csv')
    #print(tweet_df_processed.head())

