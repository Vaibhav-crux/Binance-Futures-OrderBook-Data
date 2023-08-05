
# Binance Futures Order Book Data

This Python script fetches and stores order book data from the Binance Futures Testnet API. It connects to the Binance API, retrieves order book data for specified symbols, and stores the data in an SQLite database. Additionally, it calculates order imbalance for the fetched data and stores it in the database.

## Features

- Fetches and stores order book data from the Binance Futures Testnet API
- Calculates order imbalance for the fetched data
- Adjustable time interval for data fetching

## Requirements

- Python 3.x
- SQLite database
- Binance Futures Testnet API key and secret (replace with your actual API keys)

## Installation

1. Clone this repository to your local machine.
2. Install the required Python libraries using pip:

```bash
pip install requests

