from constants import debug
from constants import tick_time
from threading import Thread
import time

class deciderAgent():

    def __init__(self, knowledgeDatabase, agents):
        self.knowledgeDatabase = knowledgeDatabase
        self.agents = agents
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        for i in range(60):
            self.tick()
            time.sleep(tick_time)


    def tick(self):
        # compute weight to determine buy/sell
        total_weight = 0
        for agent in self.agents:
            signal = agent.peek()
            total_weight += signal * self.knowledgeDatabase.get_weight(agent.__str__())

        if debug:
            print('total weight:',total_weight)

        # case based reasoning to determine quantity

        # call CEO agent to validate trade


