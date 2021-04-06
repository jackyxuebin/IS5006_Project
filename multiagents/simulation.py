from multiagents.pa_agent import *

class Simulation:
    def __init__(self):
        self.pa = Personal_Assistant_Agent()

    def __del__(self):
        print("I'm being automatically shutdown. Goodbye!")
        
