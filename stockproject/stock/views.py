from django.shortcuts import render
from yahoo_fin.stock_info import *
from django.http.response import HttpResponse
import yfinance as yf
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async

# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)
    return render(request, 'stock/stockpicker.html', {'stockpicker': stock_picker})

def stockTracker(request):
    stockpicker = request.GET.getlist('stockpicker')
    print(stockpicker)
    data = {}
    available_stocks = tickers_nifty50()
    
    # Verify that all selected stocks are available in Nifty 50
    for i in stockpicker:
        if i not in available_stocks:
            return HttpResponse("Error: Selected stock not available in Nifty 50.")
    
    # Fetch details for each selected stock
    for i in stockpicker:
        try:
            details = get_quote_table(i)
        except AttributeError as e:
            print(f"Error fetching data for {i}: {e}")
            details = None  # Handle missing data
        data.update({i: details})
    
    print(data)
    
    # Set up multithreading for concurrent fetching
    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    start = time.time()
    
    # Create and start threads
    for i in range(n_threads):
        thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}), args=(que, stockpicker[i]))
        thread_list.append(thread)
        thread.start()

    # Join threads
    for thread in thread_list:
        thread.join()

    # Collect results from the queue
    while not que.empty():
        result = que.get()
        data.update(result)
    
    end = time.time()
    time_taken = end - start
    print(f"Time taken: {time_taken} seconds")
    
    return render(request, 'stock/stocktracker.html', {'details': data})
