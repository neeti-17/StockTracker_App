from django.shortcuts import render
from yahoo_fin.stock_info import *
from django.http.response import HttpResponse
import yfinance as yf
from django.shortcuts import render
import time
import queue
from threading import Thread
from asgiref.sync import sync_to_async
 
# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)
    return render(request,'stock/stockpicker.html',{'stockpicker': stock_picker})

    # stock_picker = [
    #     "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    #     "HINDUNILVR.NS", "SBIN.NS", "HDFC.NS", "KOTAKBANK.NS", "LT.NS",
    #     "AXISBANK.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "BAJFINANCE.NS",
    #     "MARUTI.NS", "HCLTECH.NS", "ADANIGREEN.NS", "ULTRACEMCO.NS", "ONGC.NS",
    #     "WIPRO.NS", "HINDALCO.NS", "TITAN.NS", "ADANIPORTS.NS", "DIVISLAB.NS",
    #     "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "COALINDIA.NS",
    #     "NESTLEIND.NS", "SUNPHARMA.NS", "GRASIM.NS", "BAJAJFINSV.NS", "DRREDDY.NS",
    #     "BRITANNIA.NS", "BPCL.NS", "HEROMOTOCO.NS", "TATAMOTORS.NS", "SHREECEM.NS",
    #     "SBILIFE.NS", "BAJAJ-AUTO.NS", "APOLLOHOSP.NS", "M&M.NS", "CIPLA.NS",
    #     "ADANIENT.NS", "DLF.NS", "PIDILITIND.NS", "EICHERMOT.NS", "INDUSINDBK.NS"
    # ]
    # print(stock_picker)
    # return render(request, 'stock/stockpicker.html', {'stockpicker': stock_picker})


def stockTracker(request):
    stockpicker = request.GET.getlist('stockpicker')
    print(stockpicker)
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")
        
    for i in stockpicker :
        details = get_quote_table(i)
        data.update({i : details})
    print(data)
    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()
    start = time.time()
    # for i in stockpicker:
    #     result = get_quote_table(i)
    #     data.update({i: result})
    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}), args = (que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)
    end = time.time()
    time_taken =  end - start
    print(time_taken)
    return render(request,'stock/stocktracker.html',{'details': details})


# def stockTracker(request):
#     stock = yf.Ticker("RELIANCE.NS")
#     details = stock.info  # This returns a dictionary with stock details
#     return render(request, 'stock/stocktracker.html', {'details': details})

