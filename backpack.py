import requests
import time
import base64
import json
from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
import logging
import math

load_dotenv()

# Constants - adjust as needed
MARKET = 'WEN_USDC' #Pair
BID_SPREAD = 0.01  # Spread for bid orders, adjust as needed
ASK_SPREAD = 0.01  # Spread for ask orders, adjust as needed
ORDER_REFRESH_TIME = 30  # Time in seconds to refresh orders
POSITION_SIZE = 30000 #In First Currency




#Backpack.exchange URL
API_URL = 'https://api.backpack.exchange'

# Your API keys and ED25519 keys
API_KEY = os.getenv("API_KEY")

# Assuming your_base64_private_key is the base64 encoded ED25519 private key
encoded_private_key = os.getenv("API_SECRET")
# Decode the base64 encoded private key to get the raw bytes
private_key_bytes = base64.b64decode(encoded_private_key)

# Load the private key from the raw bytes
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)

# Setup logging
logging.basicConfig(filename='market_maker.log', level=logging.INFO, format='%(asctime)s %(message)s')

def log_to_console_and_file(message):
    print(message)
    logging.info(message)

def generate_signature(instruction, params, timestamp, window=5000):
    params_with_instruction = {'instruction': instruction, **params}
    ordered_params = urlencode(sorted(params_with_instruction.items()))
    signing_string = f"{ordered_params}&timestamp={timestamp}&window={window}"
    signature = private_key.sign(signing_string.encode())
    return base64.b64encode(signature).decode()

def get_headers(instruction, params, timestamp, window=5000):
    signature = generate_signature(instruction, params, timestamp, window)
    return {
        'X-API-Key': API_KEY,
        'X-Timestamp': str(timestamp),
        'X-Window': str(window),
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }
def get_market_price():
    endpoint = f'{API_URL}/api/v1/ticker?symbol={MARKET}'
    response = requests.get(endpoint)
    data = response.json()

    # Ensure the necessary keys are present in the response
    if 'lastPrice' in data:
        # Using 'lastPrice' as the market price
        return float(data['lastPrice'])
    elif 'high' in data and 'low' in data:
        # Alternatively, calculate the mid-price as the average of 'high' and 'low'
        high_price = float(data['high'])
        low_price = float(data['low'])
        return (high_price + low_price) / 2
    else:
        print("Unexpected response structure:", data)
        return None  # Or handle as appropriate
    
def place_order(side, price, size):
    timestamp = int(time.time() * 1000)
    instruction = 'orderExecute'

    # Load JSON data from the file
    with open('market.json', 'r') as f:
        market_data = json.load(f)

    # Get the market info for the current MARKET symbol
    market_info = next((market for market in market_data if market['symbol'] == MARKET), None)
    if market_info is None:
        log_to_console_and_file(f"Error: {MARKET} not found in the market data.")
        return None

    # Get the tick size and step size from the market info
    tick_size = market_info['filters']['price']['tickSize']
    step_size = market_info['filters']['quantity']['stepSize']

   # Round the price and quantity based on the tick size and step size
    rounded_price = round(float(price), int(-1 * math.log10(float(tick_size))))
    rounded_quantity = round(float(size), int(-1 * math.log10(float(step_size))))

    order_data = {
        'symbol': MARKET,
        'orderType': 'Limit',  # Ensure this is correct as per the API
        'side': side,  # Typically 'Bid' or 'Ask'
        'price': str(rounded_price),  # Ensure the API accepts the format (string or number)
        'quantity': str(rounded_quantity),  # Ensure the API accepts the format (string or number)
    }
    headers = get_headers(instruction, order_data, timestamp)
    response = requests.post(f'{API_URL}/api/v1/order', headers=headers, json=order_data)

    if response.status_code not in [200, 201, 202]:
        print(f"Error placing order, status code: {response.status_code}, response: {response.text}")
        return None

    try:
        return response.json()
    except ValueError:  # Includes JSONDecodeError
        print(f"No JSON content returned in response to place_order, status code: {response.status_code}")
        return None


def cancel_all_orders(market_symbol):
    timestamp = int(time.time() * 1000)
    instruction = 'orderCancelAll'
    # Include the market symbol in the payload
    payload = {'symbol': market_symbol}
    signature = generate_signature(instruction, payload, timestamp)
    headers = {
        'X-API-Key': API_KEY,
        'X-Timestamp': str(timestamp),
        'X-Window': str(5000),
        'X-Signature': signature,
        'Content-Type': 'application/json'
    }
    response = requests.delete(f'{API_URL}/api/v1/orders', headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:  # Includes JSONDecodeError
            print(f"No JSON content returned in response to cancel_all_orders, status code: {response.status_code}")
            return None
    else:
        print(f"Error cancelling orders, status code: {response.status_code}, response: {response.text}")
        return None

def market_maker_cycle():
    mid_price = get_market_price()
    bid_price = mid_price * (1 - BID_SPREAD)
    ask_price = mid_price * (1 + ASK_SPREAD)

    print(f"Placing new orders. Mid price: {mid_price}, Bid price: {bid_price}, Ask price: {ask_price}")
    
    # Cancel all existing orders before placing new ones
    cancel_all_orders(MARKET)
    # Load JSON data from the file
    with open('market.json', 'r') as f:
        market_data = json.load(f)

    # Check if the MARKET symbol exists in the JSON data
    market_info = next((market for market in market_data if market['symbol'] == MARKET), None)
    if market_info is None:
        log_to_console_and_file(f"Error: {MARKET} not found in the market data.")
        return

    # Check if the POSITION_SIZE meets the minimum quantity requirement
    min_quantity = market_info['filters']['quantity']['minQuantity']
    if POSITION_SIZE < float(min_quantity):
        log_to_console_and_file(f"Error: POSITION_SIZE {POSITION_SIZE} is less than the minimum quantity {min_quantity} for {MARKET}.")
        return

    try:
        bid_order = place_order('Bid', bid_price, POSITION_SIZE)
    except Exception as e:
        log_to_console_and_file(f"Error placing bid order: {str(e)}")

    try:
        ask_order = place_order('Ask', ask_price, POSITION_SIZE)
    except Exception as e:
        log_to_console_and_file(f"Error placing ask order: {str(e)}")

    print(f"Placed orders: {bid_order} {ask_order}")


    # Assume size is 1 for demonstration purposes, adjust as needed
    # try:
    #     bid_order = place_order('Bid', bid_price, POSITION_SIZE)
    # except:
    #     pass
    # try:
    #     ask_order = place_order('Ask', ask_price, POSITION_SIZE)
    # except:
    #     pass
    # print(f"Placed orders: {bid_order} {ask_order}")

def run_market_maker():
    while True:
        market_maker_cycle()
        time.sleep(ORDER_REFRESH_TIME)

if __name__ == '__main__':
    run_market_maker()
