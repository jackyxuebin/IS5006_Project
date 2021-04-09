import datetime
import pandas as pd
from app.constants.constants import *
from threading import Lock, Thread
from multiagents.tweepy_agent import *
from multiagents.controller import *

class Personal_Assistant_Agent():
    def __init__(self):
        self.name = 'Group 7 Personal Assistant Agent'
        self.call_personal_assistant_controller()
        #print('activated')

    def call_personal_assistant_controller(self):
        #print("PA is activated")
        pa_controller = Controller()
        

