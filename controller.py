import datetime
from threading import Lock, Thread
import threading
from queue import Queue
from multiprocessing import Process, Queue
import tweeter_agent
import google_api_agent
import fuzzy_logic_agent
import time

class Controller(object):
    def __init__(self):
        
        self.q = Queue()
        self.tweepy_agent = tweeter_agent.Tweepy_Agent()
        self.google_agent = google_api_agent.Google_API_Agent()
        self.fuzzy_agent = fuzzy_logic_agent.Fuzzy_Logic_Agent()
        
        #self.tweepy_agent_process = Process(target = self.tweepy_agent.get_all_tweets_search(), args = (self.q, "test"))
        #self.tweepy_agent_process.start()
        #self.tweepy_agent_process.terminate()
        #self.tweepy_agent_process.join()
        #self.tweepy_agent_process = self.q.get()
        

        print("Multi-threading is started at: %s" % time.ctime())
        t1 = threading.Thread(name='tweet_thread',target=self.tweepy_agent.get_all_tweets_search())
        t1.setDaemon(True) #setting threads as "daemon" allows main program to exit eventually even if these dont finish correctly.
        t1.start()
        
        t2 = threading.Thread(name='google_thread',target=self.google_agent.perform_google_sentiment_analysis())
        t2.setDaemon(True) #setting threads as "daemon" allows main program to exit eventually even if these dont finish correctly.
        t2.start()
        
        t3 = threading.Thread(name='fuzzy_thread',target=self.fuzzy_agent.perform_fuzzy_logic())
        t3.setDaemon(True) #setting threads as "daemon" allows main program to exit eventually even if these dont finish correctly.
        t3.start()
