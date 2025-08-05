# Custom libs
import app_secrets
import gfi
import gfe

# Libs
import datetime
import time

#############

updateTime = 30

def main_loop():
    while True:
        try:
            gfi.getSolidpixelsData()
            gfi.getGmailData()
            gfe.exportTasksToSheets()
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error in main_loop: {e}")
        time.sleep(updateTime)


while True:
    try:
        main_loop()
        break
    except KeyboardInterrupt:
        break
    except Exception as e:
        wait_minutes = 5
        print(f"[{datetime.datetime.now()}] Fatal error occurred. Restarting in {wait_minutes} minutes...")
        time.sleep(wait_minutes * 60)


    


