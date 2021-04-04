import datetime
import pandas as pd
from constants import api_key
from constants import secret
from threading import Lock, Thread
from multiprocessing import Process, Queue
from tweepy_agent import *
import controller 

class Personal_Assistant_Agent():
    def __init__(self):
        self.name = 'Group 7 Personal Assistant Agent'
        self.call_personal_assistant_controller()
        print('activated')

    def call_personal_assistant_controller(self):
        print("PA is activated")
        pa_controller = controller.Controller()
        

