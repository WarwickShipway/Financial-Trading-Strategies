# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 23:43:40 2020

@author: WRShipway
"""

import bs4 as bs
import pickle
import requests
import pandas as pd

import datetime as dt
import matplotlib.dates as mdates
import pandas_datareader.data as web

# ---- #
# save SP500 company tickers as .pickle and .txt files
def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    #soup = bs.BeautifulSoup(resp.text, "lxml")
    #soup = bs.BeautifulSoup("html.parser", "lxml") 
    soup = bs.BeautifulSoup(resp.text, "html.parser")
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
        
    with open("sp500tickers.pickle","wb") as f:
        pickle.dump(tickers,f)
        
    with open("sp500tickers.txt", "w") as f:
        for ticker in tickers:
            f.write(ticker)
        
    print(tickers)
    
    return tickers

#save_sp500_tickers()

# ---- # 
# save FTSE100 index price as list
def FTSE100_index_price():
    resp = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index')
    #soup = bs.BeautifulSoup(resp.text, "lxml")
    #soup = bs.BeautifulSoup("html.parser", "lxml") 
    soup = bs.BeautifulSoup(resp.text, "html.parser")
    table = soup.find('table', {'class': 'wikitable sortable'})
    FTSE100_prices = []
    for row in table.findAll('tr')[1:]:
        FTSE100_price = row.findAll('td')[1].text
        FTSE100_prices.append(FTSE100_price)
        
    with open("FTS100_price.pickle","wb") as f:
        pickle.dump(FTSE100_prices,f)
        
    with open("FTS100_price.txt", "w") as f:
        for price in FTSE100_prices:
            f.write(price)
        
    print(FTSE100_prices)
    
    return FTSE100_prices

#FTSE100_index_price()

'''
import requests
from bs4 import BeautifulSoup
#r = requests.get("https://www.allrecipes.com/recipes/96/salad/")

#soup = BeautifulSoup(r.text, "lxml")
#soup = BeautifulSoup(s,  "html.parser")
soup = BeautifulSoup(html, 'html.parser')
'''

# ---- #
# save FTSE100 index price as list using a different website
# wall street journal
# issue with finding table data, can extract dates but nothing else
# maybe not working as website protects from scraping bot? 
def FTSE100_index_price_wsj():
    url = 'https://www.wsj.com/market-data/quotes/index/UK/UKX/historical-prices'

    #soup = bs.BeautifulSoup(resp.text, "lxml")
    #soup = bs.BeautifulSoup("html.parser", "lxml") 

    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G928X Build/LMY47X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36'}
    resp = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(resp.text, "html.parser")
    table = soup.find('table', {'class': 'cr_dataTable'})
        
    FTSE100_dates, FTSE100_prices = [], []
    for row in table.findAll('tr')[1:]:
        FTSE100_date = row.findAll('td')[0].text
        FTSE100_dates.append(FTSE100_date)       

    print(resp) # response 200 is ok, 404 error etc
    print(soup.find('table'))
    
    print("FTSE data: {}".format(FTSE100_dates))
    return (FTSE100_dates)

FTSE100_index_price_wsj()

'''So now you have to figure out why it's None. 
Look at soup, and see if there's a table whose id is datatable_main. 
If not, obviously any attempt to find it should, and will, return None—either you're reading the wrong data, 
or you've got the wrong structure for the data. On the other hand, if you do see it, then you have to figure 
out why the find isn't finding it. Either way, finding out which it is has to be the first step to debugging. –

'''

# ---- #
# Using externally created csv file of monthly FTSE data 
# need to manipulate timestamp into pandas dataframe format (for data manipulation eg rolling mean)

from dateutil import parser

df_FTSE100 = pd.read_csv('FTSE100_index.csv')
print(df_FTSE100.head(2))
#df_FTSE100['Date'] = pd.to_datetime(df_FTSE100['Date'], format='%m%d%Y')
#df_FTSE100['Date'] = parser.parse(df_FTSE100['Date'])
#df_FTSE100['Dates'] = df_FTSE100['Dates'].map(mdates.date2num)
# required format - Date, dtype: float64

#df_FTSE100['10RollMean'] = df_FTSE100['Adj Close'].rolling(window = 10, min_periods = 0).mean()
df_FTSE100['10RollMean'] = df_FTSE100['Adj Close']

# required date formatting test
# from - Sep 01, 2020, to 2020-07-01
date_string = 'Sep 01, 2020'
#my_date = datetime.strptime(date_string, '%b%d%Y')
#print(parser.parse(date_string))

#print(my_date)
#print(df_FTSE100.head())
#print(df_FTSE100['Date'])
#print(df_FTSE100['Adj Close'])

t0 = dt.datetime(2020, 7, 1)
t1 = dt.datetime.now()
ticker = 'BP.L'#'GOOG'#'TSLA'#'BP.L'#'XUKS.L'#
df = web.DataReader(ticker, 'yahoo', t0, t1)
df['10RollMean'] = df['Adj Close'].rolling(window = 10, min_periods = 0).mean()
df['100RollMean'] = df['Adj Close'].rolling(window = 100, min_periods = 0).mean()

#print(df_FTSE100.head())
#print(df_FTSE100.dtypes)
#print(df.head())