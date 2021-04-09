from threading import Thread,Lock
from multiagents.broker_agent import BrokerAgent
from app.constants.constants import *
from collections import deque
import random
import numpy as np
import time
import logging
import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)


log = logging.getLogger('Q_learning_double_duel_recurrent_agent')
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
tf.compat.v1.disable_eager_execution()
should_load_model = True
# Model trained with
#     600 sets 1min data, iterations = 200
#     POPULATION_SIZE = 15, GAMMA = 0.99, LEARNING_RATE = 0.003
#     window_size = 30, batch_size = 32, , LAYER_SIZE = 256, ,MEMORY_SIZE = 300

class Model:
    def __init__(self, input_size, output_size, layer_size, learning_rate, name):
        with tf.variable_scope(name):
            self.X = tf.placeholder(tf.float32, (None, None, input_size))
            self.Y = tf.placeholder(tf.float32, (None, output_size))
            cell = tf.nn.rnn_cell.LSTMCell(layer_size, state_is_tuple = False)
            self.hidden_layer = tf.placeholder(tf.float32, (None, 2 * layer_size))
            self.rnn,self.last_state = tf.nn.dynamic_rnn(inputs=self.X,cell=cell,
                                                    dtype=tf.float32,
                                                    initial_state=self.hidden_layer)
            tensor_action, tensor_validation = tf.split(self.rnn[:,-1],2,1)
            feed_action = tf.layers.dense(tensor_action, output_size)
            feed_validation = tf.layers.dense(tensor_validation, 1)
            self.logits = feed_validation + tf.subtract(feed_action,tf.reduce_mean(feed_action,axis=1,keep_dims=True))
            self.cost = tf.reduce_sum(tf.square(self.Y - self.logits))
            self.optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate).minimize(self.cost)


class Agent:
    LEARNING_RATE = 0.003
    BATCH_SIZE = 32
    LAYER_SIZE = 256
    OUTPUT_SIZE = 3
    EPSILON = 0.5
    DECAY_RATE = 0.005
    MIN_EPSILON = 0.1
    GAMMA = 0.99
    MEMORIES = deque()
    COPY = 1000
    T_COPY = 0
    MEMORY_SIZE = 300

    def __init__(self, state_size, window_size, trend, skip):
        self.state_size = state_size
        self.window_size = window_size
        self.half_window = window_size // 2
        self.trend = trend
        self.skip = skip
        tf.reset_default_graph()
        self.INITIAL_FEATURES = np.zeros((4, self.state_size))
        self.model = Model(self.state_size, self.OUTPUT_SIZE, self.LAYER_SIZE, self.LEARNING_RATE,
                           'real_model')
        self.model_negative = Model(self.state_size, self.OUTPUT_SIZE, self.LAYER_SIZE, self.LEARNING_RATE,
                                    'negative_model')
        self.sess = tf.InteractiveSession()
        self.sess.run(tf.global_variables_initializer())
        self.trainable = tf.trainable_variables()

    def _assign(self, from_name, to_name):
        from_w = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=from_name)
        to_w = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=to_name)
        for i in range(len(from_w)):
            assign_op = to_w[i].assign(from_w[i])
            self.sess.run(assign_op)

    def _memorize(self, state, action, reward, new_state, dead, rnn_state):
        self.MEMORIES.append((state, action, reward, new_state, dead, rnn_state))
        if len(self.MEMORIES) > self.MEMORY_SIZE:
            self.MEMORIES.popleft()

    def _select_action(self, state):
        if np.random.rand() < self.EPSILON:
            action = np.random.randint(self.OUTPUT_SIZE)
        else:
            action = self.get_predicted_action([state])
        return action

    def _construct_memories(self, replay):
        states = np.array([a[0] for a in replay])
        new_states = np.array([a[3] for a in replay])
        init_values = np.array([a[-1] for a in replay])
        Q = self.sess.run(self.model.logits, feed_dict={self.model.X: states,
                                                        self.model.hidden_layer: init_values})
        Q_new = self.sess.run(self.model.logits, feed_dict={self.model.X: new_states,
                                                            self.model.hidden_layer: init_values})
        Q_new_negative = self.sess.run(self.model_negative.logits,
                                       feed_dict={self.model_negative.X: new_states,
                                                  self.model_negative.hidden_layer: init_values})
        replay_size = len(replay)
        X = np.empty((replay_size, 4, self.state_size))
        Y = np.empty((replay_size, self.OUTPUT_SIZE))
        INIT_VAL = np.empty((replay_size, 2 * self.LAYER_SIZE))
        for i in range(replay_size):
            state_r, action_r, reward_r, new_state_r, dead_r, rnn_memory = replay[i]
            target = Q[i]
            target[action_r] = reward_r
            if not dead_r:
                target[action_r] += self.GAMMA * Q_new_negative[i, np.argmax(Q_new[i])]
            X[i] = state_r
            Y[i] = target
            INIT_VAL[i] = rnn_memory
        return X, Y, INIT_VAL

    def get_state(self, t):
        window_size = self.window_size + 1
        d = t - window_size + 1
        block = self.trend[d: t + 1] if d >= 0 else -d * [self.trend[0]] + self.trend[0: t + 1]
        res = []
        for i in range(window_size - 1):
            res.append(block[i + 1] - block[i])
        return np.array(res)

    def buy(self, initial_money, load_model):
        if load_model:
            saver = tf.train.Saver()
            saver.restore(self.sess, "./model/Q_Learning_model.ckpt")
        starting_money = initial_money
        states_sell = []
        states_buy = []
        inventory = []
        last_action = [0, 0, 0]
        state = self.get_state(0)
        init_value = np.zeros((1, 2 * self.LAYER_SIZE))
        for k in range(self.INITIAL_FEATURES.shape[0]):
            self.INITIAL_FEATURES[k, :] = state
        for t in range(0, len(self.trend) - 1, self.skip):
            action, last_state = self.sess.run([self.model.logits, self.model.last_state],
                                               feed_dict={self.model.X: [self.INITIAL_FEATURES],
                                                          self.model.hidden_layer: init_value})
            action, init_value = np.argmax(action[0]), last_state
            next_state = self.get_state(t + 1)

            if action == 1 and initial_money >= self.trend[t]:
                inventory.append(self.trend[t])
                initial_money -= self.trend[t]
                states_buy.append(t)
                last_action = [1, t, self.trend[t]]
                # print('day %d: buy 1 unit at price %f, total balance %f'% (t, self.trend[t], initial_money))

            elif action == 2 and len(inventory):
                bought_price = inventory.pop(0)
                initial_money += self.trend[t]
                states_sell.append(t)
                try:
                    invest = ((close[t] - bought_price) / bought_price) * 100
                except:
                    invest = 0
                last_action = [-1, t, self.trend[t]]
                # print(
                #    'day %d, sell 1 unit at price %f, investment %f %%, total balance %f,'
                #    % (t, close[t], invest, initial_money)
                # )
            else:
                last_action = [0, t, self.trend[t]]

            new_state = np.append([self.get_state(t + 1)], self.INITIAL_FEATURES[:3, :], axis=0)
            self.INITIAL_FEATURES = new_state
        invest = ((initial_money - starting_money) / starting_money) * 100
        total_gains = initial_money - starting_money
        return states_buy, states_sell, total_gains, invest, last_action

    def train(self, iterations, checkpoint, initial_money):
        for i in range(iterations):
            total_profit = 0
            inventory = []
            state = self.get_state(0)
            starting_money = initial_money
            init_value = np.zeros((1, 2 * self.LAYER_SIZE))
            for k in range(self.INITIAL_FEATURES.shape[0]):
                self.INITIAL_FEATURES[k, :] = state
            for t in range(0, len(self.trend) - 1, self.skip):
                if (self.T_COPY + 1) % self.COPY == 0:
                    self._assign('real_model', 'negative_model')

                if np.random.rand() < self.EPSILON:
                    action = np.random.randint(self.OUTPUT_SIZE)
                else:
                    action, last_state = self.sess.run([self.model.logits,
                                                        self.model.last_state],
                                                       feed_dict={self.model.X: [self.INITIAL_FEATURES],
                                                                  self.model.hidden_layer: init_value})
                    action, init_value = np.argmax(action[0]), last_state

                next_state = self.get_state(t + 1)

                if action == 1 and starting_money >= self.trend[t]:
                    inventory.append(self.trend[t])
                    starting_money -= self.trend[t]

                elif action == 2 and len(inventory) > 0:
                    bought_price = inventory.pop(0)
                    total_profit += self.trend[t] - bought_price
                    starting_money += self.trend[t]

                invest = ((starting_money - initial_money) / initial_money)
                new_state = np.append([self.get_state(t + 1)], self.INITIAL_FEATURES[:3, :], axis=0)

                self._memorize(self.INITIAL_FEATURES, action, invest, new_state,
                               starting_money < initial_money, init_value[0])
                self.INITIAL_FEATURES = new_state
                batch_size = min(len(self.MEMORIES), self.BATCH_SIZE)
                replay = random.sample(self.MEMORIES, batch_size)
                X, Y, INIT_VAL = self._construct_memories(replay)

                cost, _ = self.sess.run([self.model.cost, self.model.optimizer],
                                        feed_dict={self.model.X: X, self.model.Y: Y,
                                                   self.model.hidden_layer: INIT_VAL})
                self.T_COPY += 1
                self.EPSILON = self.MIN_EPSILON + (1.0 - self.MIN_EPSILON) * np.exp(-self.DECAY_RATE * i)
            if (i + 1) % checkpoint == 0:
                print('epoch: %d, total rewards: %f.3, cost: %f, total money: %f' % (i + 1, total_profit, cost,
                                                                                     starting_money))
        saver = tf.train.Saver()
        save_path = saver.save(self.sess, "./model/Q_Learning_model.ckpt")

class QLearningDoubleDuelRecurrentAgent():

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
        window_size = 30
        skip = 1
        start_money = 2000 / default_trade_amount

        agent = Agent(state_size=window_size,
                      window_size=window_size,
                      trend=close,
                      skip=skip)

        if not should_load_model:
            agent.train(iterations=10, checkpoint=10, initial_money=start_money)

        states_buy, states_sell, total_gains, invest, last_action = agent.buy(initial_money=start_money, load_model=should_load_model)
        agent.sess.close()
        # print(last_action[0], df.date[last_action[1]], last_action[2])

        # import matplotlib.pyplot as plt
        # fig = plt.figure(figsize=(15, 5))
        # plt.plot(close, color='r', lw=2.)
        # plt.plot(close, '^', markersize=10, color='m', label='buying signal', markevery=states_buy)
        # plt.plot(close, 'v', markersize=10, color='k', label='selling signal', markevery=states_sell)
        # plt.title('total gains %f, total investment %f%%' % (total_gains, invest))
        # plt.legend()
        # plt.savefig('Q_learning_double_duel_recurrent_agent.png')
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
        return 'Q_learning_double_duel_recurrent_agent'
