from src.utils._config import env_vars
from src.data.alphavantage import alphavantage_get_currency_list

def get_dynamic_currency_list():
    try:
        if env_vars['LMA_HISTORICAL_FX_CLOSE_SOURCE'] == env_vars['LMA_ALPHA_VANTAGE_NAME']:
            currency_list_file_path = alphavantage_get_currency_list(
                base_url=env_vars['LMA_HISTORICAL_FX_CLOSE_SOURCE_DATA_BASE_URL'],
                data_dir=f"{env_vars['LMA_DATA_DIR_BASE']}{env_vars['LMA_DATA_DIR_RELATIVE_LIVE_SOURCE_DATA']}",
                filename='currency_list.csv'
            )
            return currency_list_file_path
    except Exception as e:
        print(f"Error fetching currency list: {e}")
        return None