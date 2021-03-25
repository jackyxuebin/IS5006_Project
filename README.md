# IS5006_Project

# Signal Generation Agent(Run every 5 minutes)
Input: Price<br/>
Output: UP/DOWN<br/>

# Decider Agent<br/>(Run every 5 minutes)
Input: Signals(UP/DOWN)<br/>
Output: BUY/SELL AMOUNT<br/>
Attributes:<br/>
1. Weight of each signal agent(initialize as 1)<br/>
2. Knowledge database<br/>
Signal1 | signal2 | signal3 | signal4 | sigal5 | signal6 | decision | profit/loss<br/>
3. Order book<br/>
Symbol | BUY/SELL | AMOUNT | CEO Authorization

Logic:<br/>
1. Take UP(+1)/DOWN(-1), compute a final decision using latest signals and weight<br/>
2. Match this case in knowledge database and compute amount of buy/sell<br/>
3. Store this trade in order book<br/>

# PNL Agent (Run every hour)
1. Update the knowldge database with profit/loss<br/>
2. Update the weight of each signal agent based on last hour's profit/loss data

# CEO(Run every 5 minutes)
Polls the order book authorize the trade

# Broker Agent(Run every 5 minutes)
Place trades on order book

