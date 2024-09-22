import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, DataTable, TableColumn, DatetimeTickFormatter, NumeralTickFormatter

def plot_daily_pnl(df):
    df = df.copy()
    df['color'] = ['green' if ret >= 0 else 'red' for ret in df['daily_return']]
    source = ColumnDataSource(df)
    p = figure(x_axis_type="datetime", width=800, height=400, title="Daily Returns")
    p.vbar(x='timestamp', top='daily_return', width=0.8, color='color', source=source)
    p.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d", months="%Y-%m", years="%Y")
    p.xaxis.major_label_orientation = np.pi / 4

    hover = HoverTool(
        tooltips=[
            ("Date", "@timestamp{%F}"),
            ("Daily Return", "@daily_return{0.00%}"),
        ],
        formatters={'@timestamp': 'datetime'},
        mode='vline'
    )
    p.add_tools(hover)
    p.yaxis.formatter = NumeralTickFormatter(format="0.00%")
    p.grid.grid_line_alpha = 0.3
    return p

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