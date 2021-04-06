from threading import Thread,Lock
from multiagents.broker_agent import BrokerAgent
from app.constants.constants import *
import numpy as np
import time
import logging
log = logging.getLogger('deep_evolution_agent')
should_load_model = True


class Deep_Evolution_Strategy:
    inputs = None

    def __init__(
            self, weights, reward_function, population_size, sigma, learning_rate
    ):
        self.weights = weights
        self.reward_function = reward_function
        self.population_size = population_size
        self.sigma = sigma
        self.learning_rate = learning_rate

    def _get_weight_from_population(self, weights, population):
        weights_population = []
        for index, i in enumerate(population):
            jittered = self.sigma * i
            weights_population.append(weights[index] + jittered)
        return weights_population

    def get_weights(self):
        return self.weights

    def train(self, epoch=100, print_every=1):
        lasttime = time.time()
        for i in range(epoch):
            population = []
            rewards = np.zeros(self.population_size)
            for k in range(self.population_size):
                x = []
                for w in self.weights:
                    x.append(np.random.randn(*w.shape))
                population.append(x)
            for k in range(self.population_size):
                weights_population = self._get_weight_from_population(
                    self.weights, population[k]
                )
                rewards[k] = self.reward_function(weights_population)
            rewards = (rewards - np.mean(rewards)) / (np.std(rewards) + 1e-7)
            for index, w in enumerate(self.weights):
                A = np.array([p[index] for p in population])
                self.weights[index] = (
                        w
                        + self.learning_rate
                        / (self.population_size * self.sigma)
                        * np.dot(A.T, rewards).T
                )
            if (i + 1) % print_every == 0:
                print(
                    'iter %d. reward: %f'
                    % (i + 1, self.reward_function(self.weights))
                )
        print('time taken to train:', time.time() - lasttime, 'seconds')
        np.save('./Models/Deep_Evolution_Model', self.weights)
        # print(self.weights)


class Model:
    def __init__(self, input_size, layer_size, output_size, load_model):
        if load_model:
            self.weights = np.load('./model/Deep_Evolution_Model.npy', allow_pickle=True)
        else:
            self.weights = [
                np.random.randn(input_size, layer_size),
                np.random.randn(layer_size, output_size),
                np.random.randn(1, layer_size),
            ]

    def predict(self, inputs):
        feed = np.dot(inputs, self.weights[0]) + self.weights[-1]
        decision = np.dot(feed, self.weights[1])
        return decision

    def get_weights(self):
        return self.weights

    def set_weights(self, weights):
        self.weights = weights


class Agent:
    POPULATION_SIZE = 15
    SIGMA = 0.1
    LEARNING_RATE = 0.03

    def __init__(self, model, window_size, trend, skip, initial_money):
        self.model = model
        self.window_size = window_size
        self.half_window = window_size // 2
        self.trend = trend
        self.close = trend
        self.skip = skip
        self.initial_money = initial_money
        self.es = Deep_Evolution_Strategy(
            self.model.get_weights(),
            self.get_reward,
            self.POPULATION_SIZE,
            self.SIGMA,
            self.LEARNING_RATE,
        )

    def act(self, sequence):
        decision = self.model.predict(np.array(sequence))
        return np.argmax(decision[0])

    def get_state(self, t):
        window_size = self.window_size + 1
        d = t - window_size + 1
        block = self.trend[d: t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0: t + 1]
        res = []
        for i in range(window_size - 1):
            res.append(block[i + 1] - block[i])
        return np.array([res])

    def get_reward(self, weights):
        initial_money = self.initial_money
        starting_money = initial_money
        self.model.weights = weights
        state = self.get_state(0)
        inventory = []
        quantity = 0
        for t in range(0, len(self.trend) - 1, self.skip):
            action = self.act(state)
            next_state = self.get_state(t + 1)

            if action == 1 and starting_money >= self.trend[t]:
                inventory.append(self.trend[t])
                starting_money -= self.close[t]

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                starting_money += self.trend[t]

            state = next_state
        return ((starting_money - initial_money) / initial_money) * 100

    def fit(self, iterations, checkpoint):
        self.es.train(iterations, print_every=checkpoint)

    def buy(self):
        initial_money = self.initial_money
        state = self.get_state(0)
        starting_money = initial_money
        states_sell = []
        states_buy = []
        inventory = []
        last_action = [0, 0, 0]
        for t in range(0, len(self.trend) - 1, self.skip):
            action = self.act(state)
            next_state = self.get_state(t + 1)

            if action == 1 and initial_money >= self.trend[t]:
                inventory.append(self.trend[t])
                initial_money -= self.trend[t]
                states_buy.append(t)
                # print('T %d: buy 1 unit at price %f, total balance %f'% (t, self.trend[t], initial_money))
                last_action = [1, t, self.trend[t]]

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                initial_money += self.trend[t]
                states_sell.append(t)
                try:
                    invest = ((self.close[t] - bought_price) / bought_price) * 100
                except:
                    invest = 0
                last_action = [-1, t, self.trend[t]]
                # print('T %d, sell 1 unit at price %f, investment %f %%, total balance %f,'% (t, self.close[t], invest, initial_money))
            else:
                last_action = [0, t, self.trend[t]]
            state = next_state

        invest = ((initial_money - starting_money) / starting_money) * 100
        total_gains = initial_money - starting_money
        return states_buy, states_sell, total_gains, invest, last_action

class DeepEvolutionAgent():

    def __init__(self):
        # Lock to prevent other agents from reading signals when tick is in progress
        self.lock = Lock()
        self.signals = []
        self.thread = Thread(name=self.__str__(),target=self.loop)
        self.thread.start()

    def loop(self):
        while True:
            self.tick()
            time.sleep(tick_time)


    def tick(self):
        self.lock.acquire()
        df = BrokerAgent.get_ohlcv_data(trading_symbol,timeframe,limit=1000)
        close = df.close.values.tolist()
        window_size = 100
        skip = 1
        initial_money = 2000 / default_trade_amount

        model = Model(input_size=window_size, layer_size=500, output_size=3, load_model=should_load_model)
        agent = Agent(model=model,
                      window_size=window_size,
                      trend=close,
                      skip=skip,
                      initial_money=initial_money)
        if not should_load_model:
            agent.fit(iterations=1000, checkpoint=10)

        states_buy, states_sell, total_gains, invest, last_action = agent.buy()
        # print(last_action[0], df.date[last_action[1]], last_action[2])

        # import matplotlib.pyplot as plt
        # fig = plt.figure(figsize=(15, 5))
        # plt.plot(close, color='r', lw=2.)
        # plt.plot(close, '^', markersize=10, color='m', label='buying signal', markevery=states_buy)
        # plt.plot(close, 'v', markersize=10, color='k', label='selling signal', markevery=states_sell)
        # plt.title('total gains %f, total investment %f%%' % (total_gains, invest))
        # plt.legend()
        # plt.savefig('Evolution_Strategy_agent.png')
        # plt.show()

        if last_action[0] == 1:
            self.signals.append(1)
        elif last_action[0] == -1:
            self.signals.append(-1)
        else:
            self.signals.append(0)
        log.info('signals %s',self.signals)
        self.lock.release()


    def peek(self):
        self.lock.acquire()
        signal = 0
        if len(self.signals)>0:
            signal = self.signals[-1]
        self.lock.release()
        # print("signal")
        return signal

    def __str__(self):
        return 'deep_evolution_agent'
