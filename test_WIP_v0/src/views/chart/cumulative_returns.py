import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, DataTable, TableColumn, DatetimeTickFormatter, NumeralTickFormatter

def plot_cumulative_returns(df):
    source = ColumnDataSource(df)

    p = figure(x_axis_type="datetime", width=800, height=400, title="Cumulative Returns")

    p.line('timestamp', 'cumulative_return', source=source, line_width=2, color='green', legend_label="Cumulative Return")

    p.xaxis.formatter = DatetimeTickFormatter(days="%Y-%m-%d", months="%Y-%m", years="%Y")
    p.xaxis.major_label_orientation = np.pi / 4

    hover = HoverTool(
        tooltips=[
            ("Date", "@timestamp{%F}"),
            ("Cumulative Return", "@cumulative_return{0.00%}"),
        ],
        formatters={'@timestamp': 'datetime'},
        mode='vline'
    )
    p.add_tools(hover)
    p.legend.location = "top_left"
    p.yaxis.formatter = NumeralTickFormatter(format="0.00%")
    p.grid.grid_line_alpha = 0.3

    return p

def calculate_cumulative_returns(df):
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    return df

# TODO: Plot multiple cumulative returns for different models