import os
from dotenv import load_dotenv

from src.utils._util import load_and_print_env_vars

load_dotenv()

env_vars = load_and_print_env_vars()