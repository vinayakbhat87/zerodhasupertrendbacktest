#from IPython.display import display
import pandas as pd
import json
import pandas_ta as ta
from datetime import datetime
import time
import copy
import sys
import numpy as np
import logging
from kiteconnect import KiteConnect

kite = KiteConnect(api_key="37776ghtsgjm261j")

# Redirect the user to the login url obtained
# from kite.login_url(), and receive the request_token
# from the registered redirect url after the login flow.
# Once you have the request_token, obtain the access_token
# as follows.

# data = kite.generate_session("5EjEAgaVsrwk7s57ChV6qxcJYbW6T57H", api_secret="wwd9z6arm1gjl76d5fk5qebrffufe46s")
# print(data["access_token"])
kite.set_access_token("yrDMtFS3ULmkyckKdhGtR3cVrENWg0o1")

bankniftyfuturecode= '21048578'

StartTime=datetime.strptime('9:25:00 AM','%I:%M:%S %p').time()
EndTime=datetime.strptime('3:25:00 PM','%I:%M:%S %p').time()
now = datetime.now().time()
fromdateforcalculatingsupertrend = "2022-07-29 09:15:00"
todateforcalculatingsupertrend = "2022-08-11 15:30:00"
histdata = pd.DataFrame(kite.historical_data(21048578,fromdateforcalculatingsupertrend, todateforcalculatingsupertrend, "5minute", False ))

histdata.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
histdata['Date'] = pd.to_datetime(histdata['Date'])
histdata['Date'] = histdata['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
print(histdata.to_string())

supertrendData = ta.supertrend(histdata['High'], histdata['Low'], histdata['Close'], 7, 1)
supertrendData.columns = ['price', 'bors','temp','temp1']
print(supertrendData.to_string())

iteration =1
lotsize = 25
alltrades=[]
tradefortheday=[]
optiontradefortheday=[]
totalprofitloss=0
maxiteration=4
text_file = open("C:/Users/My PC/PycharmProjects/zerodhasupertrendbacktest/pytonbacktest.txt", "w")
for index,row in supertrendData.iterrows():
    candledata = histdata.iloc[index]
    nextcandledata =histdata.iloc[index +1] if index!=len(supertrendData)-1 else histdata.iloc[index]

    tradetime = datetime.strptime(str(candledata[0]),"%Y-%m-%d %H:%M:%S").time()
   # print(str(supertrendData.iloc[index]['bors']) + " " + str(supertrendData.iloc[index-1]['bors']))
    if (tradetime > StartTime) and (tradetime < EndTime) and index > 0 and supertrendData.iloc[index]['bors'] != supertrendData.iloc[index-1]['bors']:
        if(supertrendData.iloc[index]['bors'] == 1): #buy
            if not tradefortheday:
                trade = {'entry': nextcandledata["Open"], 'exit':'nan', 'quantity': iteration*lotsize, 'bors': 'buy', 'pnl': 0}
            else:
                lastrade = tradefortheday[-1]
                lastrade['exit'] = nextcandledata["Open"]
                pnl =(lastrade['entry'] - lastrade['exit'])*lastrade['quantity']
                lastrade['pnl']=pnl
                iteration = iteration * 2 if pnl < 0 else 1
                iteration = iteration if iteration < maxiteration else maxiteration
                trade = {'entry': nextcandledata["Open"], 'exit': 'nan', 'quantity': iteration * lotsize, 'bors': 'buy','pnl': 0}
        else:
            if not tradefortheday:
                trade = {'entry': nextcandledata["Open"], 'exit': 'nan', 'quantity': iteration * lotsize, 'bors': 'sell','pnl': 0}
            else:
                lastrade = tradefortheday[-1]
                lastrade['exit'] = nextcandledata["Open"]
                pnl = (lastrade['exit'] - lastrade['entry']) * lastrade['quantity']
                lastrade['pnl'] = pnl
                iteration = iteration * 2 if pnl < 0 else 1
                iteration = iteration if iteration < maxiteration else maxiteration
                trade = {'entry': nextcandledata["Open"], 'exit': 'nan', 'quantity': iteration * lotsize, 'bors': 'sell','pnl': 0}

        tradefortheday.append(copy.deepcopy(trade))
    if(tradetime == EndTime and len(tradefortheday) > 1):
        lastrade = tradefortheday[-1]
        lastrade['exit'] = nextcandledata["Open"]
        if lastrade['bors'] == 'sell':
            lastrade['pnl'] = (lastrade['entry'] - lastrade['exit'])*lastrade['quantity']
        else:
            lastrade['pnl'] =(lastrade['exit'] - lastrade['entry']) * lastrade['quantity']

        profitfortheday=0
        for tr in tradefortheday:
            text_file.write(str(tr) + "\n")
            profitfortheday = profitfortheday + tr['pnl']

        print("pnl for " + str(candledata[0])+ " is =  " + str(profitfortheday) )
        totalprofitloss = totalprofitloss + profitfortheday
      #  print(tradefortheday)
        text_file.write("pnl for " + str(candledata[0])+ " is =  " + str(profitfortheday) + "\n")
        tradefortheday = []
        iteration = 1;

text_file.close()
print(totalprofitloss)