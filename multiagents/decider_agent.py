from app.constants.constants import *
##from constants import tick_time
##from constants import case_threshold
##from constants import profit_threshold_percentage
##from constants import default_trade_amount
##from constants import trading_symbol
##from constants import action_threshold
##from constants import timeframe
##from constants import risk_reward_ratio
from threading import Thread
from multiagents.broker_agent import BrokerAgent
import time
import logging
log = logging.getLogger('decider_agent')


class deciderAgent():

    def __init__(self, knowledgeDatabase, agents, ceo):
        self.knowledgeDatabase = knowledgeDatabase
        self.agents = agents
        self.ceo = ceo
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.tick()
            time.sleep(tick_time)


    def tick(self):
        # compute weight to determine buy/sell
        log.info('decider agent tick')
        total_weight = 0
        agent_signals={}
        trade_entry = {}
        trade_entry['symbol'] = trading_symbol
        for agent in self.agents:
            signal = agent.peek()
            total_weight += signal * self.knowledgeDatabase.get_weight(agent.__str__(),signal)
            agent_signals[agent.__str__()] = signal
            trade_entry[agent.__str__()] = signal
        if debug:
            log.info('total weight:%s',total_weight)
        if total_weight > action_threshold:
            action = 1
        elif total_weight < -action_threshold:
            action = -1
        else:
            action = 0
        trade_entry['action'] = action

        # case based reasoning to determine quantity
        trade_quantity = default_trade_amount
        log.info('case based reasoning:')
        matched_case = self.knowledgeDatabase.get_case(agent_signals)
        log.info('matched case: %s',matched_case)

        if len(matched_case) > case_threshold:
            log.info(matched_case['profit/loss'])
            profit = matched_case['profit/loss'].dropna().sum()/len(matched_case)
            log.info('average profitability:%s',profit)
            if profit > profit_threshold_percentage:
                trade_quantity = 2 * default_trade_amount
        trade_entry['quantity'] = trade_quantity

        # call CEO agent to validate trade
        trade_entry['stoploss'] = self.get_std_20()
        trade_entry['takeprofit'] = self.get_std_20() * risk_reward_ratio
        trade_entry['open_price'] = self.get_market_price()

        self.ceo.review(trade_entry)

    def get_std_20(self):
        df = BrokerAgent.get_ohlcv_data(trading_symbol, timeframe)
        df['std_20'] = df['close'].rolling(window=20).std()
        return df.iloc[-1]['std_20']

    def get_market_price(self):
        return BrokerAgent.get_ticker_price(trading_symbol)


