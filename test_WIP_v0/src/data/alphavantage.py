import os
import requests
import datetime

def alphavantage_get_fx_daily_data(from_symbol, to_symbol, base_url, api_key, data_dir, outputsize='compact', datatype='csv'):
    if not base_url:
        raise EnvironmentError('BASE_URL not provided')
    if not api_key:
        raise EnvironmentError('API_KEY not provided')
    if not data_dir:
        raise EnvironmentError('LIVE_SOURCE_DATA_DIR not provided')

    os.makedirs(data_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    filename = f'FX_DAILY_{from_symbol}_{to_symbol}_{timestamp}.csv'
    file_path = os.path.join(data_dir, filename)
    print(f'file_path: {file_path}')

    if os.path.exists(file_path):
        print(f'File already exists, returning existing data. Delete data at this path to refresh:\n\n {file_path} \n\n')
        return os.path.abspath(file_path)

    params = {
        'function': 'FX_DAILY',
        'from_symbol': from_symbol,
        'to_symbol': to_symbol,
        'apikey': api_key,
        'outputsize': outputsize,
        'datatype': datatype
    }

    try:
        response = requests.get(f'{base_url}/query', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        raise SystemError(f'HTTP Error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        raise SystemError(f'Error Connecting: {errc}')
    except requests.exceptions.Timeout as errt:
        raise SystemError(f'Timeout Error: {errt}')
    except requests.exceptions.RequestException as err:
        raise SystemError(f'Request Exception: {err}')

    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    print(f'Data saved to {file_path}')
    
    return os.path.abspath(file_path)

def alphavantage_get_currency_list(base_url, data_dir='.', filename='currency_list.csv'):
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, filename)

    if os.path.exists(file_path):
        print(f'File already exists, returning existing data. Delete data at this path to refresh:\n\n {file_path} \n\n')
        return os.path.abspath(file_path)

    try:
        response = requests.get(f'{base_url}/physical_currency_list/')
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        raise SystemError(f'HTTP Error: {errh}')
    except requests.exceptions.ConnectionError as errc:
        raise SystemError(f'Error Connecting: {errc}')
    except requests.exceptions.Timeout as errt:
        raise SystemError(f'Timeout Error: {errt}')
    except requests.exceptions.RequestException as err:
        raise SystemError(f'Request Exception: {err}')

    with open(file_path, 'wb') as f:
        f.write(response.content)

    return os.path.abspath(file_path)
