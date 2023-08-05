import time
import requests
import datetime
import sqlite3


BASE_URL = "https://testnet.binancefuture.com"
EXCHANGE_INFO_URL = f"{BASE_URL}/fapi/v1/exchangeInfo" 
ORDER_BOOK_URL = f"{BASE_URL}/fapi/v1/depth"

API_KEY = "hLflXSIwuxwGQefVOZDLz38rwWXJEHtLhXDToGyWWbvtWbzUhg3Q1roteEmFWhGk"
API_SECRET = "Z35YuyPPrElqI24svtsO2m7fpxJ9ha760dT9gfqWPqCBQJHY0YAZid8p3DchqZrq"

def are_symbols_valid(symbol1, symbol2):
    response = requests.get(EXCHANGE_INFO_URL)
    exchange_info = response.json()

    symbol1_found = any(symbol1 == s["symbol"] for s in exchange_info["symbols"])
    symbol2_found = any(symbol2 == s["symbol"] for s in exchange_info["symbols"])

    return symbol1_found and symbol2_found

def create_tables(cursor):
    create_orderbook_table_query = """
    CREATE TABLE IF NOT EXISTS orderbook_symbol (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        market TEXT,
        bid_price REAL,
        bid_volume REAL,
        ask_price REAL,
        ask_volume REAL
    )
    """
    cursor.execute(create_orderbook_table_query)

    create_imbalance_table_query = """
    CREATE TABLE IF NOT EXISTS imbalance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        market TEXT,
        order_imbalance_bid REAL,
        order_imbalance_ask REAL
    )
    """
    cursor.execute(create_imbalance_table_query)

def fetch_and_store_order_book_data(cursor, symbol, time_interval=10):
    try:
        response = requests.get(ORDER_BOOK_URL, params={"symbol": symbol, "limit": 20})
        order_book_data = response.json()

        timestamp = order_book_data["E"] / 1000.0 
        date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        bids = order_book_data["bids"]
        asks = order_book_data["asks"]

        bid_price, bid_volume = zip(*bids)
        ask_price, ask_volume = zip(*asks)
        total_bid_volume = sum(float(vol) for vol in bid_volume)
        total_ask_volume = sum(float(vol) for vol in ask_volume)

        print("Fetched data for symbol:", symbol)
        print("Date:", date)
        print("Bid Price:", bid_price)
        print("Bid Volume:", bid_volume)
        print("Ask Price:", ask_price)
        print("Ask Volume:", ask_volume)
        print("Total Bid Volume:", total_bid_volume)
        print("Total Ask Volume:", total_ask_volume)
        print("-----------------------------")

        sql_insert_query = f"INSERT INTO orderbook_symbol (date, market, bid_price, bid_volume, ask_price, ask_volume) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql_insert_query, (date, symbol, bid_price, bid_volume, ask_price, ask_volume))
        
        order_imbalance_bid = bid_price * total_bid_volume
        order_imbalance_ask = ask_price * total_ask_volume
        sql_insert_imbalance_query = f"INSERT INTO imbalance (date, market, order_imbalance_bid, order_imbalance_ask) VALUES (?, ?, ?, ?)"
        cursor.execute(sql_insert_imbalance_query, (date, symbol, order_imbalance_bid, order_imbalance_ask))

    except Exception as e:
        pass

def fetch_data_between_times(cursor, start_time, end_time):
    sql_fetch_query = f"SELECT * FROM orderbook_symbol WHERE date BETWEEN ? AND ?"
    cursor.execute(sql_fetch_query, (start_time, end_time))
    data = cursor.fetchall()
    return data

def main():
    symbol1 = "BTCUSDT"
    symbol2 = "ETHUSDT"
    if not are_symbols_valid(symbol1, symbol2):
        print("Invalid symbols.")
        return

    conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()
    create_tables(cursor)
    
    time_interval = 10

    try:
        while True:
            fetch_and_store_order_book_data(cursor, symbol1, time_interval)
            fetch_and_store_order_book_data(cursor, symbol2, time_interval)
            conn.commit()
            time.sleep(time_interval)
    except KeyboardInterrupt:
        conn.close()

if __name__ == "__main__":
    main()

