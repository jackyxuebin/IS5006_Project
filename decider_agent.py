from constants import debug
from constants import tick_time
from constants import case_threshold
from constants import profit_threshold_percentage
from constants import default_trade_amount
from constants import trading_symbol
from constants import action_threshold
from threading import Thread
from ceo import ceo
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
        action = 0
        total_weight = 0
        agent_signals={}
        for agent in self.agents:
            signal = agent.peek()
            total_weight += signal * self.knowledgeDatabase.get_weight(agent.__str__(),signal)
            agent_signals[agent.__str__()] = signal
        if debug:
            print('total weight:',total_weight)
        if total_weight > action_threshold:
            action = 1
        elif total_weight < -action_threshold:
            action = -1
        else:
            action = 0

        # case based reasoning to determine quantity
        trade_quantity = default_trade_amount
        if debug:
            print('case based reasoning:')
        matched_case = self.knowledgeDatabase.get_case(agent_signals)
        if debug:
            print('matched case:',matched_case)

        if len(matched_case) > case_threshold:
            profit = matched_case['profit/loss'].sum()/len(matched_case)
            if debug:
                print('average profitability:',profit)
            if profit > profit_threshold_percentage:
                trade_quantity = 2 * default_trade_amount

        # call CEO agent to validate trade
        ceo.review(trading_symbol, action, trade_quantity)

