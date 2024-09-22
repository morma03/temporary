import numpy as np

from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.models import ColumnDataSource

from bokeh.models import (
    CrosshairTool,
    CustomJS,
    ColumnDataSource,
    Span,
    HoverTool,
    Range1d,
    DatetimeTickFormatter,
    WheelZoomTool,
    LinearColorMapper,
)

def plot_price_with_bollinger_model(df):
    source = ColumnDataSource(df)
    p = figure(x_axis_type="datetime", width=800, height=400, title="Close Price with Bollinger Bands and Buy/Sell Signals")
    p.line('timestamp', 'close', source=source, line_width=2, color='blue', legend_label="Close Price")
    p.line('timestamp', 'bollinger_upper', source=source, line_width=1, color='orange', legend_label="Upper Bollinger Band")
    p.line('timestamp', 'bollinger_middle', source=source, line_width=1, color='green', legend_label="Middle Bollinger Band")
    p.line('timestamp', 'bollinger_lower', source=source, line_width=1, color='orange', legend_label="Lower Bollinger Band")
    p.varea(x='timestamp', y1='bollinger_lower', y2='bollinger_upper', source=source, fill_alpha=0.1, fill_color="gray")
    buy_signals = df[df['buy_signal']]
    p.scatter(x=buy_signals['timestamp'], y=buy_signals['close'], size=10, color="green", marker="triangle", legend_label="Buy Signal")

    sell_signals = df[df['sell_signal']]
    p.scatter(x=sell_signals['timestamp'], y=sell_signals['close'], size=10, color="red", marker="inverted_triangle", legend_label="Sell Signal")

    p.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d", months="%Y-%m", years="%Y")
    p.xaxis.major_label_orientation = np.pi / 4

    hover = HoverTool(
        tooltips=[
            ("Date", "@timestamp{%F}"),
            ("Close", "@close"),
            ("Upper Band", "@bollinger_upper"),
            ("Lower Band", "@bollinger_lower"),
        ],
        formatters={'@timestamp': 'datetime'},
        mode='vline'
    )
    p.add_tools(hover)

    p.legend.location = "top_left"

    p.grid.grid_line_alpha = 0.3

    return p



# TODO: Remove bolliner bands from the plot