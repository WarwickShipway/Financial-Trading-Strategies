#*- coding: utf-8 -*-

'''
NOTES
to install dataframes type "pip install pandas_datareader"
  then reset kernal CTRL + .(punct. mark) inside the kernal

may need pip install fix-yahoo-finance
  import fix_yahoo_finance as yf
  yf.pdr_override()
  df = data.get_data_yahoo(symbol, t0, t1)
  
 test different  eg, 'morningstar'

Quandl module is subscription
'''

# data manipulation
import pandas as pd
import pandas_datareader.data as web
# plots
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
#from matplotlib.finance import candlestick_ohlc
#from mplfinance import candlestick_ohlc
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
# web scraping
import bs4 as bs
import pickle
import requests

style.use('ggplot') # example style

# ---- #
# extract FTSE100 index prices. These prices are too historical, need a better soup
# write index or add to dict/list? Currently doing both

def FTSE100_index_price():
    resp = requests.get('https://en.wikipedia.org/wiki/FTSE_100_Index')
    #soup = bs.BeautifulSoup(resp.text, "lxml")
    #soup = bs.BeautifulSoup("html.parser", "lxml") 
    soup = bs.BeautifulSoup(resp.text, "html.parser")
    table = soup.find('table', {'class': 'wikitable sortable'})
    FTSE100_dates, FTSE100_prices = [], []
    for row in table.findAll('tr')[1:]:
        FTSE100_date = row.findAll('td')[0].text
        FTSE100_price = row.findAll('td')[1].text
        FTSE100_dates.append(FTSE100_date)       
        FTSE100_prices.append(FTSE100_price)
        
    with open("FTS100_price.pickle","wb") as f:
        pickle.dump(FTSE100_price,f)
        
    with open("FTS100_price.txt", "w") as f:
        for FTSE100_price in FTSE100_prices:
            f.write(FTSE100_price)
        
    return (FTSE100_dates, FTSE100_prices)

# ---- #
# extract single company share price, financial pricing scraper from yahoo daily reader

t0 = dt.datetime(2020, 2, 1)
#t1 = dt.datetime(2020, 2, 1)
t1 = dt.datetime.now()

ticker = 'BP.L'#'GOOG'#'TSLA'#'BP.L'#'XUKS.L'#
df = web.DataReader(ticker, 'yahoo', t0, t1)

df['10RollMean'] = df['Adj Close'].rolling(window = 10, min_periods = 0).mean()
df['100RollMean'] = df['Adj Close'].rolling(window = 100, min_periods = 0).mean()
# min_periods = 0 so it doesnt need 100 data points to start rolling av

# Resample to 10 day data, tracking back further
# ohlc is open, high, low, close
df_ohlc = df['Adj Close'].resample('240H').ohlc()
df_volume = df['Volume'].resample('240H').sum()

#print(df_ohlc.head())

ax1 = plt.subplot(111) # plot 1
ax1.xaxis_date()

ax1.plot(df.index, df['Adj Close'], label = "close")
ax1.plot(df.index, df['10RollMean'], label = "10d rolling mean")
ax1.plot(df.index, df['100RollMean'], label = "100d rolling mean")

df_ohlc.reset_index(inplace=True) # reset index so all columns consist of data
df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

candlestick_ohlc(ax1, df_ohlc.values, width = 5, colorup = 'g')

# ---- #
# CURRENTLY DEVELOPING. Need to fix date history
# call FTSE function to plot over company trends. 
# see 8.1.7 for timestamp definition - https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

FTSE = FTSE100_index_price()

print(FTSE)

df_FTSE_date = pd.DataFrame(FTSE[0])
print(df_FTSE_date)

#df_FTSE_date = df_FTSE_date.map(mdates.date2num)

#ax1.plot(FTSE[0], FTSE[1], label = "FTSE index")

ax1.set_facecolor('w')
ax1.legend(fancybox = True, framealpha = 1, facecolor = 'white')
ax1.grid(color = 'xkcd:grey')

#plt.show() # Python 2.7 required only