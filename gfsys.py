# Custom libs
import app_secrets
import gfi
import gfe
import db_control_simple

# Libs
import datetime
import time

#############

updateTime = 30

def main_loop():
    while True:
        try:
            #gfi.getSolidpixelsData()
            #gfi.getGmailData()

            gfe.exportTasksToSheets()
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error in main_loop: {e}")
        time.sleep(updateTime)

if __name__ == "__main__":
    main_loop()
    


