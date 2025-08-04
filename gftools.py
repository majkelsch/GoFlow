import json



def create_flag(name, signal):
    with open(f"gfcache/{name}.txt", "w") as f:
        f.write(signal)


def get_flag(name):
    try:
        with open(f"gfcache/{name}.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        return False
    
def clear_flag(name):
    try:
        with open(f"gfcache/{name}.txt", "w") as f:
            f.write("")
    except FileNotFoundError:
        print(f"Error: Flag {name} not found.")



def get_config(name):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)[name]
            return config
    except Exception as e:
        print("Error with reading the config file.")



