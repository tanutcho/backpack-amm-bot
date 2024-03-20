# Automate Market Maker (for backpack.exchange)

This Python code implements a simple Automate Market Maker (AMM) strategy for backpack.exchange. The strategy involves opening both Bid and Ask orders from the mid price to facilitate trading.

## Strategy Overview
The AMM strategy follows these steps:

1. Calculate the mid price by averaging the Bid and Ask prices.
2. Determine the spread percentage (e.g., 1% or 2%) to set the Bid and Ask prices.
3. Open Bid orders slightly below the mid price and Ask orders slightly above the mid price.
4. Refresh order in every specific seconds (e.g., 15 seconds).


## Use this script
Please create .env file including API_KEY and API_SECRET from backpack.exchange, Then install dependency and start the script.

```
pip install python-dotenv
python backpack.py
```


Warning: Experimental Use Only