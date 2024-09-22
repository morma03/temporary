import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_cumulative_returns(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df['timestamp'], df['cumulative_return'], label="Cumulative Return", color='green', linewidth=2)

    ax.set_title("Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()

    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    return fig

def calculate_cumulative_returns(df):
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    return df

# TODO: Plot multiple cumulative returns for different models
