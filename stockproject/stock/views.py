from django.shortcuts import render
from yahoo_fin.stock_info import get_quote_table
from django.http import HttpResponse
import queue
from threading import Thread
import time

# Define the hardcoded list of Nifty 50 stocks
NIFTY_50_TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'SBIN.NS', 'HDFC.NS', 'KOTAKBANK.NS', 'LT.NS',
    'AXISBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'ASIANPAINT.NS', 'BAJFINANCE.NS',
    'MARUTI.NS', 'HCLTECH.NS', 'ULTRACEMCO.NS', 'ONGC.NS', 'WIPRO.NS'
]

def stockPicker(request):
    # Use hardcoded list instead of tickers_nifty50()
    stock_picker = NIFTY_50_TICKERS
    return render(request, 'stock/stockpicker.html', {'stockpicker': stock_picker})

def stockTracker(request):
    # Use hardcoded NIFTY_50_TICKERS directly
    available_stocks = NIFTY_50_TICKERS

    # Get selected stocks from the request
    stockpicker = request.GET.getlist('stockpicker')
    print(stockpicker)
    data = {}

    # Ensure all selected stocks are in the Nifty 50 list
    for stock in stockpicker:
        if stock not in available_stocks:
            return HttpResponse(f"Error: {stock} is not available in Nifty 50 stocks.")

    # Multithreaded stock data fetching
    def fetch_stock_data(stock, q):
        try:
            details = get_quote_table(stock)
            q.put({stock: details})
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")
            q.put({stock: None})  # Handle missing data

    # Set up threads to fetch data concurrently
    q = queue.Queue()
    threads = []
    start_time = time.time()

    for stock in stockpicker:
        thread = Thread(target=fetch_stock_data, args=(stock, q))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect data from each thread
    while not q.empty():
        data.update(q.get())

    # Log time taken to fetch data
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    # Render the template with fetched data
    return render(request, 'stock/stocktracker.html', {'details': data})
