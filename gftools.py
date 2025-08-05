import json
from datetime import datetime
import time
import typing


########## Flags ##########

def create_flag(name, signal):
    with open(f"gfcache/{name}.txt", "w") as f:
        f.write(signal)
    if get_config("advancedDebug"):
            print(f"[CREATED FLAG]")


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
        if get_config("advancedDebug"):
            print(f"[CLEARED FLAG]")
    except FileNotFoundError:
        print(f"Error: Flag {flag_name} not found.")






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
                    print(f"Collision Signal found, retrying in {update_time}s")
                time.sleep(update_time)
            if debug:
                print(f"No Collision Signal found.")
            action()
        else:
            if debug:
                print(f"No Collision Signal found.")
            action()
    except Exception as e:
        print(f"Error: wait_for_flag {e}")




def detect_collision_flag(flag_name:str, flag_signal:str, update_time:int, action, max_retries: typing.Optional[int] | None, debug:bool = False):
    if get_flag(flag_name) == flag_signal:
        tries = 0
        while get_flag(flag_name) == flag_signal:
            if max_retries:
                if tries > max_retries:
                    raise Exception(f"Reached max_retries: {max_retries}")
                else:
                    tries += 1
            if debug:
                print(f"Collision Signal found, retrying in {update_time}s")
            time.sleep(update_time)
        if debug:
            print(f"No Collision Signal found")
        action()
    else:
        if debug:
            print(f"No Collision Signal found.")
        action()

########## Configs ##########

def get_config(name):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)[name]
            return config
    except Exception as e:
        print("Error with reading the config file.")


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
