import dotenv
import os
import datetime
import sys


def get(key:str):
    """
    Returns the value for a key inside the `.env` file

    Parameters
    ----------
        key : string
            Key to use for search

    Returns
    -------
        string
            Value that corresponds to `key`
    """
    try:
        dotenv.load_dotenv()
        val = os.getenv(key)
        if val is None:
            raise ValueError(f"'{key}' environment variable is not set or is missing.")
        return val
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in secrets.py: {e}")
        sys.exit(1)
