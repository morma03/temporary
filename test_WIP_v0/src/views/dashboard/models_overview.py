import sys
import os
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QCompleter
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, DataTable, TableColumn, DatetimeTickFormatter
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.layouts import column, row

from src.utils._config import env_vars
from src.utils._util import read_local_csv, format_underscore_str
from src.views.inputs.dynamic_data import get_dynamic_currency_list
from src.data.alphavantage import alphavantage_get_fx_daily_data, alphavantage_get_currency_list

from src.views.chart.price import plot_price_with_bollinger_model
from src.views.chart.daily_pnl import plot_daily_pnl, calculate_daily_pnl
from src.views.chart.cumulative_returns import plot_cumulative_returns, calculate_cumulative_returns
from src.trading_models.model_moving_average import model_moving_average

default_inputs = {
    'cash': 10000,
    'from_symbol': 'DOP',
    'to_symbol': 'TTD',
    'start_date': '2020-01-01',
    'end_date': '2021-01-01'
}

available_trading_models = [
    '50/50 Model',
    'Moving Average Model',
    'Bollinger Bands Model',
    'MACD Model',
    'RSI Model',
    'Stochastic Oscillator Model',
    'ADX Model',
    'Parabolic SAR Model',
    'Ichimoku Cloud Model',
    'Fibonacci Retracement Model',
    'Elliott Wave Model',
    'Volume-Weighted Average Price (VWAP) Model',
    'Average True Range (ATR) Model',
    'Commodity Channel Index (CCI) Model',
    'Relative Strength Index (RSI) Model',
    'Moving Average Convergence Divergence (MACD) Model',
]

def calculate_stats(data, trades, initial_cash=10000):
    stats = {
        'Total Trades': len(trades),
    }
    return stats

def transform_model_output(model_output, initial_cash=10000):
    data = pd.DataFrame()
    trades = []
    return data, trades

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(str, pd.DataFrame)

    def __init__(self, inputs, env_vars, selected_files, selected_models, uploaded_data=None):
        super().__init__()
        self.inputs = inputs
        self.env_vars = env_vars
        self.selected_files = selected_files
        self.selected_models = selected_models
        self.uploaded_data = uploaded_data

    def run(self):
        try:
            if self.uploaded_data is not None:
                ohlc_values = self.uploaded_data
            else:
                ohlc_file_path = alphavantage_get_fx_daily_data(
                    from_symbol=self.inputs['from_symbol'],
                    to_symbol=self.inputs['to_symbol'],
                    api_key=self.env_vars['LMA_HISTORICAL_FX_CLOSE_SOURCE_DATA_API_KEY'],
                    base_url=self.env_vars['LMA_HISTORICAL_FX_CLOSE_SOURCE_DATA_BASE_URL'],
                    data_dir=f"{self.env_vars['LMA_DATA_DIR_BASE']}{self.env_vars['LMA_DATA_DIR_RELATIVE_LIVE_SOURCE_DATA']}",
                    outputsize='full'
                )
                ohlc_values = read_local_csv(ohlc_file_path)

        
            for file_name in self.selected_files:
                file_path = os.path.join('./data', file_name)
                file_data = pd.read_csv(file_path)
            

            ohlc_values['timestamp'] = pd.to_datetime(ohlc_values['timestamp'])
            mask = (ohlc_values['timestamp'] >= self.inputs['start_date']) & (ohlc_values['timestamp'] <= self.inputs['end_date'])
            ohlc_values = ohlc_values.loc[mask]

        
        
            if 'Moving Average Model' in self.selected_models:
                model_output = model_moving_average(ohlc_values)
            else:
            
                model_output = ohlc_values 

            data, trades = transform_model_output(model_output, initial_cash=self.inputs['cash'])
            data['close'] = ohlc_values['close'].values
            stats = calculate_stats(data, trades, initial_cash=self.inputs['cash'])
            model_output, trades = calculate_daily_pnl(model_output)
            model_output = calculate_cumulative_returns(model_output)
            model_output.to_csv('./model_output.csv')

            number_of_trades = len(trades)
            winning_trades = len([t for t in trades if t > 0])
            losing_trades = len([t for t in trades if t <= 0])
            win_rate = winning_trades / number_of_trades if number_of_trades > 0 else 0
            total_return = model_output['cumulative_return'].iloc[-1]

            stats = {
                'Total Return': f"{total_return:.2%}",
                'Number of Trades': number_of_trades,
                'Winning Trades': winning_trades,
                'Losing Trades': losing_trades,
                'Win Rate': f"{win_rate:.2%}" if number_of_trades > 0 else 'N/A',
            }

            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            columns = [TableColumn(field="Metric", title="Metric"),
                       TableColumn(field="Value", title="Value")]
            data_table = DataTable(source=ColumnDataSource(stats_df), columns=columns, width=800, height=280)

            price_plot = plot_price_with_bollinger_model(model_output)
            daily_returns_plot = plot_daily_pnl(model_output)
            cumulative_returns_plot = plot_cumulative_returns(model_output)

        
            layout = column(
                price_plot,
                daily_returns_plot,
                cumulative_returns_plot,
                data_table
            )

            html = file_html(layout, CDN, format_underscore_str(f"{self.env_vars['LMA_PY_ENV_NAME']} {self.env_vars['LMA_VERSION']}"))
            self.result.emit(html, model_output)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class MainModelsOverviewWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(format_underscore_str(f"{env_vars['LMA_PY_ENV_NAME']} {env_vars['LMA_VERSION']}"))

        currency_list_file_path = get_dynamic_currency_list()

        if currency_list_file_path is not None:
            currency_df = pd.read_csv(currency_list_file_path)
            currency_codes = currency_df['currency code'].tolist()
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Failed to fetch currency list.')
            currency_codes = []

    
        self.layout = QtWidgets.QHBoxLayout()

    
        charts_layout = QtWidgets.QVBoxLayout()
        self.web_view = QWebEngineView()
        self.loading_label = QtWidgets.QLabel('Loading, please wait...')
        self.loading_label.setAlignment(QtCore.Qt.AlignCenter)
        self.loading_label.setVisible(False)

        charts_layout.addWidget(self.loading_label)
        charts_layout.addWidget(self.web_view)

    
        side_panel_layout = QtWidgets.QVBoxLayout()

    
        inputs_group = QtWidgets.QGroupBox('Inputs')
        inputs_layout = QtWidgets.QFormLayout()

        self.cash_input = QtWidgets.QLineEdit(str(default_inputs['cash']))

        self.from_symbol_input = QtWidgets.QComboBox()
        self.to_symbol_input = QtWidgets.QComboBox()
        self.from_symbol_input.setEditable(True)
        self.to_symbol_input.setEditable(True)

        self.from_symbol_input.addItems(currency_codes)
        self.to_symbol_input.addItems(currency_codes)

        if default_inputs['from_symbol'] in currency_codes:
            from_index = currency_codes.index(default_inputs['from_symbol'])
            self.from_symbol_input.setCurrentIndex(from_index)
        else:
            self.from_symbol_input.setCurrentIndex(0)

        if default_inputs['to_symbol'] in currency_codes:
            to_index = currency_codes.index(default_inputs['to_symbol'])
            self.to_symbol_input.setCurrentIndex(to_index)
        else:
            self.to_symbol_input.setCurrentIndex(0)

        from_completer = QCompleter(currency_codes)
        from_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.from_symbol_input.setCompleter(from_completer)

        to_completer = QCompleter(currency_codes)
        to_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.to_symbol_input.setCompleter(to_completer)

        self.start_date_input = QtWidgets.QLineEdit(default_inputs['start_date'])
        self.end_date_input = QtWidgets.QLineEdit(default_inputs['end_date'])

        inputs_layout.addRow('Cash:', self.cash_input)
        inputs_layout.addRow('From Symbol:', self.from_symbol_input)
        inputs_layout.addRow('To Symbol:', self.to_symbol_input)
        inputs_layout.addRow('Start Date (YYYY-MM-DD):', self.start_date_input)
        inputs_layout.addRow('End Date (YYYY-MM-DD):', self.end_date_input)

        self.fetch_button = QtWidgets.QPushButton('Fetch Data and Analyze')
        self.fetch_button.clicked.connect(self.run_analysis)

        inputs_layout.addRow(self.fetch_button)

        inputs_group.setLayout(inputs_layout)

    
        files_group = QtWidgets.QGroupBox('Available Files')
        files_layout = QtWidgets.QVBoxLayout()

        file_dir = './data' 
        if os.path.exists(file_dir):
            file_paths = [os.path.join(file_dir, f) for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f))]
            file_names = [os.path.basename(f) for f in file_paths]
        else:
            file_names = []
        self.file_checkboxes = []
        for file_name in file_names:
            checkbox = QtWidgets.QCheckBox(file_name)
            self.file_checkboxes.append(checkbox)
            files_layout.addWidget(checkbox)

        files_group.setLayout(files_layout)

    
        models_group = QtWidgets.QGroupBox('Trading Models')
        models_layout = QtWidgets.QVBoxLayout()
        self.model_checkboxes = []
        for model_name in available_trading_models:
            checkbox = QtWidgets.QCheckBox(model_name)
            self.model_checkboxes.append(checkbox)
            models_layout.addWidget(checkbox)

        models_group.setLayout(models_layout)

    
        upload_download_group = QtWidgets.QGroupBox('Upload/Download')
        upload_download_layout = QtWidgets.QVBoxLayout()
        self.upload_button = QtWidgets.QPushButton('Upload CSV File')
        self.upload_button.clicked.connect(self.upload_csv_file)
        self.download_button = QtWidgets.QPushButton('Download Dashboard and Data')
        self.download_button.clicked.connect(self.download_dashboard_data)
        upload_download_layout.addWidget(self.upload_button)
        upload_download_layout.addWidget(self.download_button)

        upload_download_group.setLayout(upload_download_layout)

    
        side_panel_layout.addWidget(inputs_group)
        side_panel_layout.addWidget(files_group)
        side_panel_layout.addWidget(models_group)
        side_panel_layout.addWidget(upload_download_group)

    
        side_panel_layout.addStretch()

    
        self.layout.addLayout(charts_layout, stretch=4)
        self.layout.addLayout(side_panel_layout, stretch=1)

        self.setLayout(self.layout)

    def upload_csv_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Upload CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                uploaded_df = pd.read_csv(file_name)
                self.uploaded_data = uploaded_df
                QtWidgets.QMessageBox.information(self, 'Success', f'File {file_name} uploaded successfully.')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to upload file: {str(e)}')

    def download_dashboard_data(self):
        if not hasattr(self, 'current_html') or not hasattr(self, 'model_output'):
            QtWidgets.QMessageBox.warning(self, 'Warning', 'No dashboard or data to download. Please run analysis first.')
            return
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory to Save Files", options=options)
        if directory:
            try:
                dashboard_file = os.path.join(directory, 'dashboard.html')
                with open(dashboard_file, 'w') as f:
                    f.write(self.current_html)
                data_file = os.path.join(directory, 'model_output.csv')
                self.model_output.to_csv(data_file, index=False)
                QtWidgets.QMessageBox.information(self, 'Success', f'Dashboard and data saved successfully in {directory}.')
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to save files: {str(e)}')

    def run_analysis(self):
        try:
            inputs = {
                'cash': float(self.cash_input.text()),
                'from_symbol': self.from_symbol_input.currentText(),
                'to_symbol': self.to_symbol_input.currentText(),
                'start_date': self.start_date_input.text(),
                'end_date': self.end_date_input.text()
            }
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, 'Input Error', str(e))
            return

        selected_files = [cb.text() for cb in self.file_checkboxes if cb.isChecked()]
        uploaded_data = getattr(self, 'uploaded_data', None)
        selected_models = [cb.text() for cb in self.model_checkboxes if cb.isChecked()]

        if not selected_models:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select at least one trading model.')
            return

        self.loading_label.setVisible(True)
        self.fetch_button.setEnabled(False)

        self.thread = QtCore.QThread()
        self.worker = Worker(inputs, env_vars, selected_files, selected_models, uploaded_data)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result.connect(self.display_result)
        self.worker.error.connect(self.display_error)
        self.thread.finished.connect(lambda: self.loading_label.setVisible(False))
        self.thread.finished.connect(lambda: self.fetch_button.setEnabled(True))
        self.thread.start()

    def display_result(self, html, model_output):
        self.web_view.setHtml(html)
        self.current_html = html
        self.model_output = model_output

    def display_error(self, error_msg):
        QtWidgets.QMessageBox.critical(self, 'Error', error_msg)
