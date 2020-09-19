#*- coding: utf-8 -*-
'''
libraries
https://www.quantlib.org/
https://news.efinancialcareers.com/uk-en/3000277/python-libraries-for-finance
'''
import datetime as dt
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web

# plots
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot') # example style

t0 = dt.datetime(2018, 9, 15)
t1 = dt.datetime.now()
Plot_FontSize_Switch = "Y" # "Y" if IDE resolution has changed
ShortTerm = 22 * 1
LongTerm = 22 * 4

# ---- #
# extract FTSE100 index monthly prices
# cannot get FTSE data so have it saved as a .csv
if not os.path.exists('FTSE100_index.csv'):
    print("\nPlease compile FTSE data with headers of:\n ""Date"" \n ""Adj Close""\n")
else:
    df_FTSE100 = pd.read_csv('FTSE100_index.csv', thousands=',', parse_dates=['Date'], index_col='Date')
    df_FTSE100 = df_FTSE100.sort_values(by='Date')

# These are not required as it is set in the read_csv parameters
#df_FTSE100.reset_index(inplace=True)
#df_FTSE100.set_index("Date", inplace=True)
#df_FTSE100['Date'] = df_FTSE100['Date'].apply(pd.to_datetime)

# get weekdays, reindex for price data for weekdays, replace NA
df_FTSE100_weekday = pd.date_range(start=t0, end=t1, freq='B')
df_FTSE100['Adj Close_weekday'] = df_FTSE100['Adj Close'].reindex(df_FTSE100_weekday)
df_FTSE100['Adj Close_weekday'] = df_FTSE100['Adj Close_weekday'].fillna(method='ffill')

# monthly data = 22, moving average (or use weekday data above)
#  EWMA applies weighting factors which decrease exponentially, ie heavier at current prices, to reduce lag
df_FTSE100['ShortMA'] = df_FTSE100['Adj Close'].rolling(window = ShortTerm, min_periods = 0).mean()
df_FTSE100['LongMA'] = df_FTSE100['Adj Close'].rolling(window = LongTerm, min_periods = 0).mean()
df_FTSE100['ShortEWMA'] = df_FTSE100['Adj Close'].ewm(span=ShortTerm, adjust=False).mean()

# Statistics on data
#  rate of change = close(x) / close(x-n), where n is number of days in past (eg yday) plot rate of change itself from yday backwards?
#  MA = sum(x)/n. for new day xn updates and x(0) (ie oldest) is removed use price of stock relative to moving average crossing- when MA/EWMA crosses actual price
#  Momentum - accl of price change, RSI, crossover strategy

# percent returns over 10 day window
df_FTSE100['returns'] = df_FTSE100['Adj Close'].pct_change(10)
df_FTSE100['returns'] = df_FTSE100['returns'].fillna(method='bfill')
df_FTSE100['log_returns'] = np.log(df_FTSE100['Adj Close'])
df_FTSE100['log_returns'] = df_FTSE100['log_returns'].fillna(0)

# Log returns - First the logarithm of the prices is taken and the the difference of consecutive (log) observations
# assumes re investing back into shares
df_FTSE100['log_returns_diff'] = df_FTSE100['log_returns'].diff()
df_FTSE100['log_returns_sum'] = (df_FTSE100['log_returns_diff'].cumsum())
df_FTSE100['log_returns_relative'] = np.exp(df_FTSE100['log_returns_sum'] - 1)
df_FTSE100['ShortMAChange'] = (df_FTSE100['ShortMA'] / df_FTSE100['ShortMA'].shift(ShortTerm)) - 1
df_FTSE100['LongMAChange'] = (df_FTSE100['LongMA'] / df_FTSE100['LongMA'].shift(LongTerm)) - 1

# ---- #
# Company data to compare to FTSE
ticker = 'BP.L'#'GOOG'#'TSLA'#'BP.L'#'XUKS.L'#
df_ticker = web.DataReader(ticker, 'yahoo', t0, t1)

# Statistics on data
df_ticker['ShortMA'] = df_ticker['Adj Close'].rolling(window = ShortTerm, min_periods = 0).mean()
df_ticker['LongMA'] = df_ticker['Adj Close'].rolling(window = LongTerm, min_periods = 0).mean()
df_ticker['ShortMAChange'] = (df_ticker['ShortMA'] / df_ticker['ShortMA'].shift(ShortTerm)) - 1
df_ticker['LongMAChange'] = (df_ticker['LongMA'] / df_ticker['LongMA'].shift(LongTerm)) - 1

# ---- #
# Plotting relative returns
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8,6))
ax1.xaxis_date()

ax1.plot(df_ticker.index, df_ticker['Adj Close'], label = ticker + " Adj Close")
ax1.plot(df_FTSE100['Adj Close'].index.values, df_FTSE100['Adj Close'], label = 'FTSE Adj Close')

ax2.plot(df_FTSE100['log_returns_diff'].index.values, df_FTSE100['log_returns_diff'], label = 'FTSE log diff')
ax2.plot(df_FTSE100['returns'].index.values, df_FTSE100['returns'], label = 'FTSE % change over 10 days')
ax2.plot(df_FTSE100['log_returns_sum'].index.values, df_FTSE100['log_returns_sum'], label = 'FTSE log sum')
ax2.plot(df_FTSE100['log_returns_relative'].index.values, df_FTSE100['log_returns_relative'], label = 'FTSE relative log returns')

ax3.plot(df_FTSE100['ShortMAChange'].index.values, df_FTSE100['ShortMAChange'] * 100, label = 'FTSE change in short term MA')
ax3.plot(df_FTSE100['LongMAChange'].index.values, df_FTSE100['LongMAChange'] * 100, label = 'FTSE change in long term MA')
ax3.plot(df_ticker['ShortMAChange'].index.values, df_ticker['ShortMAChange'] * 100, label = ticker + ' change in short term MA')
ax3.plot(df_ticker['LongMAChange'].index.values, df_ticker['LongMAChange'] * 100, label = ticker + ' change in long term MA')

if Plot_FontSize_Switch == "Y":
    ax1.tick_params(axis='both', labelsize=8) 
    ax3.set_ylabel('% Change in Rolling Average', fontsize = 8)
    ax3.set_xlabel('Date', fontsize = 8)
    ax1.legend(fancybox = True, framealpha = 1, facecolor = 'white', prop={'size': 8})
    ax2.legend(fancybox = True, framealpha = 1, facecolor = 'white', prop={'size': 8})
    ax3.legend(fancybox = True, framealpha = 1, facecolor = 'white', prop={'size': 8})
else:
    ax3.set_ylabel('% Change in Rolling Average')
    ax3.set_xlabel('Date')
    ax1.legend()
    ax2.legend()
    ax3.legend()

'''
# ---- #
# log / cumsum test
x = [dt.datetime.now() + dt.timedelta(hours=i) for i in range(5)]
#y = [i+random.gauss(0,1) for i,_ in enumerate(x)]
y = [1, 1, 2, 2, 3]

y2 = np.cumsum(y)
y_log = np.log(y)
y_exp = (np.exp(y_log.cumsum()) - 1)

d = {'Date': x, 'Data': y}
df_xy = pd.DataFrame(d)
print(df_xy)
y_diff = df_xy.pct_change(1)

plt.plot(x,y,label='y')
plt.plot(x,y2,label='cumsum')
plt.plot(x,y_log,label='log(y)')
plt.plot(x,y_exp,label='exp(y)')
plt.legend()
plt.gcf().autofmt_xdate()
'''