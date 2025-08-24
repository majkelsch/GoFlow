import json
from datetime import datetime
import time
import typing
import base64
import logging
from typing import Optional, Type, Any

########## Flags ##########

def create_flag(name, signal):
    with open(f"gfcache/{name}.txt", "w") as f:
        f.write(signal)
    log(f"[CREATED FLAG]")


def get_flag(flag_name):
    try:
        with open(f"gfcache/{flag_name}.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return False
    
def clear_flag(flag_name):
    try:
        with open(f"gfcache/{flag_name}.txt", "w") as f:
            f.write("")
        log(f"[CLEARED FLAG]")
    except FileNotFoundError:
        log(f"Error: Flag {flag_name} not found.", level='error')






def wait_for_flag(flag_name:str, signal:str, update_time:int, action, max_retries: typing.Optional[int] = None, debug:bool = False):
    """
    Wait until certain flag event is triggered

    Parameters
    ----------
        flag_name : string
            Name of the flag file without `.txt` suffix
        signal : string
            Expected signal
        update_time : int
            Amout of second to wait between retries
        action
            Function to trigger, please use `lamba: func()`
        max_retries : int
            Max amount of retries before giving up and raising an Exception
    """

    try:
        tries = 0
        if get_flag(flag_name) != signal:
            while get_flag(flag_name) != signal:
                if max_retries:
                    if tries >= max_retries:
                        raise Exception(f"Reached max_retries: {max_retries}")
                    else:
                        tries += 1
                if debug:
                    log(f"Collision Signal found, retrying in {update_time}s")
                time.sleep(update_time)
            if debug:
                log(f"No Collision Signal found.")
            action()
        else:
            if debug:
                log(f"No Collision Signal found.")
            action()
    except Exception as e:
        log(f"Error: wait_for_flag {e}", level='error')




def detect_collision_flag(flag_name:str, flag_signal:str, update_time:int, action, max_retries: typing.Optional[int] | None, debug:bool = False):
    try:
        if get_flag(flag_name) == flag_signal:
            tries = 0
            while get_flag(flag_name) == flag_signal:
                if max_retries:
                    if tries > max_retries:
                        raise Exception(f"Reached max_retries: {max_retries}")
                    else:
                        tries += 1
                if debug:
                    log(f"Collision Signal found, retrying in {update_time}s")
                time.sleep(update_time)
            if debug:
                log(f"No Collision Signal found")
            action()
        else:
            if debug:
                log(f"No Collision Signal found.")
            action()
    except Exception as e:
        log(f"Error: wait_for_flag {e}", level='error')

########## Configs ##########

def get_config(name:str):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)[name]
            return config
    except Exception as e:
        log(f"Error with reading the config file: {e}", level='error')


########## Conversions ##########

def parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
        

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def url_b64_decode(data:str):
    return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8')


def url_b64_encode(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')



########## Loggig [WIP] ##########

logger = logging.getLogger("goflow")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("goflow.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def log(msg: str, level: str = "info"):
    """
    Logs a message to the console (if advancedDebug is enabled) and always to a file.

    Parameters
    ----------
    msg : str
        The message to log.
    level : str
        Logging level: 'info', 'warning', 'error', 'debug'.
    """
    log_func = getattr(logger, level, logger.info)
    log_func(msg)



def read_logs() -> str:
    """
    Reads the log file and returns its content.

    Returns
    -------
    str
        Content of the log file. 
    """

    try:
        with open("goflow.log", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Log not found."
    except Exception as e:
        return f"Error reading log file: {e}"
