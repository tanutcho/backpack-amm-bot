# Automate Market Maker (for backpack.exchange)

This Python code implements a simple Automate Market Maker (AMM) strategy for backpack.exchange. The strategy involves opening both Bid and Ask orders from the mid price to facilitate trading.

## Strategy Overview
The AMM strategy follows these steps:

1. Calculate the mid price by averaging the Bid and Ask prices.
2. Determine the spread percentage (e.g., 1% or 2%) to set the Bid and Ask prices.
3. Open Bid orders slightly below the mid price and Ask orders slightly above the mid price.
4. Refresh order in every specific seconds (e.g., 15 seconds).

# How to use
1. Open the account on backpack.exchange [Link to Backpack with Affiliate - little tip to dev](https://backpack.exchange/refer/f101340c-cd34-497f-b5a3-ee1ca8df1cda)
2. Create API Key from Settings page in backpack, Please note API_KEY and API_SECRET you may use in next section
3. Install Python 3 on your computer
4. Clone this repository ```git clone https://github.com/tanutcho/backpack-amm-bot.git ```
5. Edit `sample.env` file to your API_KEY and API_SECRET from (2)
6. Rename `sample.env` to `.env`
7. Install dependency and run backpack.py script
```
pip install python-dotenv
python backpack.py
```


<sub>Warning: Experimental Use Only</sub>


_Love this code? Buy me a coffee_

_ Solana Address:_ ```4pPe7iUZikn4C8miw8C3WLQvyy6YZ24qWnvw52U7nHYP```
