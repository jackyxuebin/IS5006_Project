# IS5006 Final Group Project

## Signal Generation Agent (Run every 5 minutes)
Input: Price
Output: BUY (1), HOLD (0), SELL(-1)

### [1. Bollinger Band Agent](https://www.investopedia.com/trading/using-bollinger-bands-to-gauge-trends/)
Bollinger Bands(BBand) are usually used to gauge market’s overbought/oversold conditions. It relies on the concept of mean reversion of the price. Mean reversion assumes that if a price deviates substantially from its average, it will eventually move back to its mean. This agent generates a sell signal when the price falls below the lower band and a buy signal when the price rises above the high band. Otherwise, it generates a neutral signal. Below formula is used to compute BBand.

lower = mean(20) – 2*std(20))
upper = mean(20) + 2*std(20)

### [2. Bollinger Band Agent](https://www.investopedia.com/ask/answers/121014/what-are-best-indicators-use-conjunction-bollinger-bands.asp#:~:text=Using%20the%20%25b%20Indicator,the%20upper%20and%20lower%20bands.&text=This%20is%20helpful%20for%20traders,determine%20divergences%20and%20trend%20changes)
The Bollinger Band Trend(BBTrend) indicator is usually used in conjunction with the Bollinger Band indicator. It can signal both strength and direction of price, offering a different perspective. This agent generates a buy signal when the BBTrend is above 0, a sell signal when BBTrend is below 0. Below formula is used to compute BBTrend
 
lower = abs(lowerBB(20) – lowerBB(50))
upper = abs(upperBB(20) – upperBB(50))
BBTrend = (lower - upper) ÷ middleBB(20)

### 3. Fuzzy Logic Agent
The Fuzzy Logic agent will work with 2 other agents (Google API agent and Tweepy agent) to perform fuzzy logic for generating ‘recommendation score’ based on sentiment score and sentiment magnitude obtained from Google API agent. The generated recommendation score and the percentages of the labels (positive, negative and neutral) will be used to generate signal -1 (sell signal), 0 (no action) or 1(buy signal) based on the predefined thresholds. The thresholds were fixed based on the results from our simulation.

### 4. Deep Evolution Agent
We can look to gradient-free approaches to reinforcement learning for help. Using genetic algorithms one can find the parameters that best defines a good performing agent. You start with a certain number of predefined agents (i.e. potential trading strategies) with randomly initialised parameters. Some of them by chance will outperform others. Here is where the evolution comes to play and resurrects the concept of the ‘survival of the fittest’. The algorithm selects the top performing decile of agents and add a bit of Gaussian noise to the parameters so that in the next iteration the agent gets to explore the neighbouring space to identify even better performing strategies. It is down to the core a very simple concept. One can further improve these results by changing some of the input parameters to the genetic algorithm for example the hyperparameters like the window size, population size, variance, and learning rate.

### 5. Double Duel Recurrent Q Learning Agent
It is an online action-value function learning with an exploration policy, e.g., epsilon-greedy7. You take an action, observe, maximise, adjust policy and do it all again.

## Decider Agent (Run every 5 minutes)
There are two main tasks performed by the decider agent - decision on direction and quantity to trade. Action is computed based on the sum of the product of each agent’s signal and their corresponding weight. If the sum exceeds a certain threshold, a buy decision is made; If the sum falls below a certain threshold, a sell decision is made; Otherwise no action is triggered. Quantity is computed using case based reasoning. It works with below logic. Every time a sequence of signals are retrieved, the agent queries the knowledge database for all historical trade with the same signal sequence. Average profitability is computed based on those historical trades. If the average profitability exceeds a predefined threshold, we double the quantity to trade, otherwise we use a predefined default quantity
Attributes:<br/>

## Knowledge database
The knowledge database stores two sets of information - agent weights and pertinent past cases.

**Attributes:**
1. bollinger_band_agent signal
2. bollinger_band_trend_agent signal
3. fuzzy_logic_agent signal
4. Q_learning_double_duel_recurrent_agent signal 
5. deep_evolution_agent signal

**Logic:**
1. Init - restores knowledge database locally and on cloud e.g. csv file and google sheet
8. Create - creates an entry in the knowledge database
9. Update - update the knowledge database with profit/loss
10. Store - saves the knowledge database to google sheet

## PNL Agent(Run every minutes)
The profit/loss agent polls the tradebook frequently to check if any take profit/stop loss level is violated. If so, it simply closes the trade to secure profit/reduce loss:
1. Runs every minute to check any stoploss triggered for trades in our order book(risk control)
2. Close trade if risk control kicks in and update order book
3. Update knowledge database with profit/loss

## Learning Agent (Run every hour)
The learning agent runs only after each trading cycle. The cycle period can be configured. At the end of each cycle, it closes all open trades and computes the long profitability and short profitability of each agent. The weight is computed as (long profitability/short profitability)-1. If the weight is below 0. It’ll be adjusted to 0:
1. Check and close if any open trade from order book
2. Update order book with profit/loss
3. Update the knowldge database with profit/loss
4. Update the weight of each signal agent based on historical profit/loss data
5. Save order book, knowledge database, weight into google sheet

## CEO
The CEO agent checks the balance of the account. If there is sufficient balance, it places the trade, otherwise it aborts the trade. For every trade, it also computes the take profit and stop loss level. Lastly, it records the trade into the trade book in the knowledge database once it’s placed:
1. Validate against priori rules of trade (Volume/Balance)
2. Place order through broker agent
3. Record order in order book

## Broker
The broker agent integrates with the exchange and exposes below 5 methods.
1.  Get_ohlcv_data
2.  Get_balance
3.  Get_ticker_price
4.  Place_market_buy_order
5.  Place_market_sell_order

