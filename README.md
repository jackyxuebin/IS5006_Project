# IS5006_Project

# Signal Generation Agent(Run every 5 minutes)
Input: Price<br/>
Output: UP/DOWN<br/>

# Decider Agent<br/>(Run every 5 minutes)
Attributes:<br/>
1. Weight of each signal agent(initialize as 1)<br/>

Logic:<br/>
1. Take UP(+1)/DOWN(-1), compute a final decision using latest signals and weight<br/>
2. Match this case in knowledge database and compute amount of buy/sell<br/>
3. Place trade through CEO agent<br/>

# Knowledge database
Attributes:<br/>
Knowledge database<br/>
Signal1 | signal2 | signal3 | signal4 | sigal5 | signal6 | decision | profit/loss<br/>

Logic:<br/>
1. Init - restores knowledge database from google sheet<br/>
2. Create - creates an entry in the knowledge database<br/>
3. Update - update the knowledge database with profit/loss<br/>
4. Store - saves the knowledge database to google sheet<br/>

# PNL Agent(Run every minutes)
1. Runs every minute to check any stoploss triggered for trades in our order book(risk control)
2. Close trade if risk control kicks in and update order book
3. Update knowledge database with profit/loss

# Learning Agent (Run every hour)
Logic
1. Check and close if any open trade from order book<br/>
2. Update order book with profit/loss<br/>
3. Update the knowldge database with profit/loss<br/>
4. Update the weight of each signal agent based on historical profit/loss data<br/>
5. Save order book, knowledge database, weight into google sheet

# CEO(Run adhoc)
1. Validate against priori rules of trade (Volume/Balance)<br/>
2. Place order through broker agent<br/>
3. Record order in order book<br/>

# Order Book
Attributes:<br/>
1. Order book<br/>
OrderID | KnowldgeDBID | Symbol | Amount | Status | Profit/Loss<br/>

Logic:<br/>
1. Init - restores order book from google sheet<br/>
2. Create - creates an entry in the order book<br/>
3. Update - update the order book with profit/loss<br/>
4. Store - saves the order book to google sheet<br/>

# Broker(Run adhoc)
1. Check account balance
2. Place trade
3. Close trade


