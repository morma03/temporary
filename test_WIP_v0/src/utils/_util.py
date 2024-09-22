import os

import warnings
from pprint import pprint
from numbers import Number
from typing import Dict, List, Optional, Sequence, Union, cast

import numpy as np
import pandas as pd

def try_(lazy_func, default=None, exception=Exception):
    try:
        return lazy_func()
    except exception:
        return default

def _as_str(value) -> str:
    if isinstance(value, (Number, str)):
        return str(value)
    if isinstance(value, pd.DataFrame):
        return 'df'
    name = str(getattr(value, 'name', '') or '')
    if name in ('open', 'high', 'low', 'close', 'volume'):
        return name[:1]
    if callable(value):
        name = getattr(value, '__name__', value.__class__.__name__).replace('<lambda>', 'λ')
    if len(name) > 10:
        name = name[:9] + '…'
    return name

def _as_list(value) -> List:
    if isinstance(value, Sequence) and not isinstance(value, str):
        return list(value)
    return [value]


def _data_period(index) -> Union[pd.Timedelta, Number]:
    values = pd.Series(index[-100:])
    return values.diff().dropna().median()

def debug_print(message, level="DEBUG"):
    debug_level = os.getenv('DEBUG_LEVEL', 'DEBUG').upper()
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    if level.upper() in levels and levels.index(level.upper()) >= levels.index(debug_level):
        print(f"{level}: {message}")

def load_env_vars(prefix='LMA_'):
    env_vars = {key: os.getenv(key) for key in os.environ if key.startswith(prefix)}
    return env_vars

def load_and_print_env_vars():
    env_vars = load_env_vars()
    
    debug_mode = os.getenv("DEBUG", "False").lower() in ["true", "1"]
    
    if debug_mode:
        print("\nDebug mode is ON. Loaded environment variables:")
        pprint(env_vars)
    else:
        print("Environment variables loaded")
    
    return env_vars

def read_local_csv(file_path):
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        raise SystemError(f"Error reading CSV file: {e}")
    
    return data

def format_underscore_str(value: str) -> str:
    return value.replace('_', ' ').title()