import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_daily_pnl(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['green' if ret >= 0 else 'red' for ret in df['daily_return']]
    ax.bar(df['timestamp'], df['daily_return'], color=colors, width=0.8)

    ax.set_title("Daily Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Return")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()

    ax.grid(alpha=0.3)
    fig.tight_layout()

    return fig

def calculate_daily_pnl(df):
    position = 0  
    entry_price = 0
    returns = []
    trades = [] 

    df = df.sort_values('timestamp').reset_index(drop=True)
    for i in range(len(df)):
        if position == 0:
            if df.loc[i, 'buy_signal']:
                position = 1
                entry_price = df.loc[i, 'close']
                returns.append(0) 
            else:
                returns.append(0) 
        elif position == 1:
            if df.loc[i, 'sell_signal']:
                exit_price = df.loc[i, 'close']
                trade_return = (exit_price - entry_price) / entry_price
                returns.append(trade_return)
                trades.append(trade_return)
                position = 0
                entry_price = 0
            else:
                daily_return = (df.loc[i, 'close'] - df.loc[i-1, 'close']) / df.loc[i-1, 'close']
                returns.append(daily_return)
                
    df['daily_return'] = returns
    df['trades'] = [np.nan]*len(df)
    trade_indices = df[(df['sell_signal']) & (df['daily_return'] != 0)].index
    df.loc[trade_indices, 'trades'] = trades
    return df, trades

# TODO: Histogram of daily returns
# TODO: Plot multiple daily returns for different models