import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_price_with_bollinger_model(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['timestamp'], df['close'], label='Close Price', color='blue', linewidth=2)
    ax.plot(df['timestamp'], df['bollinger_upper'], label='Upper Bollinger Band', color='orange', linewidth=1)
    ax.plot(df['timestamp'], df['bollinger_middle'], label='Middle Bollinger Band', color='green', linewidth=1)
    ax.plot(df['timestamp'], df['bollinger_lower'], label='Lower Bollinger Band', color='orange', linewidth=1)

    ax.fill_between(df['timestamp'], df['bollinger_lower'], df['bollinger_upper'], color='gray', alpha=0.1)

    buy_signals = df[df['buy_signal']]
    sell_signals = df[df['sell_signal']]

    ax.scatter(buy_signals['timestamp'], buy_signals['close'], color='green', marker='^', s=100, label='Buy Signal')
    ax.scatter(sell_signals['timestamp'], sell_signals['close'], color='red', marker='v', s=100, label='Sell Signal')

    ax.set_title("Close Price with Bollinger Bands and Buy/Sell Signals")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()

    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    return fig

# TODO: Remove bolliner bands from the plot