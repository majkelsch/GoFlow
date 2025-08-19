# Custom libs
import app_secrets
import gfi
import gfe
import gftools

# Libs
import datetime
import time

#############



def main_loop():
    gftools.create_flag("status_scripts", "functional")
    while True:
        try:
            gfi.getSolidpixelsData()
            gfi.getGmailData()
            gfe.exportTasksToSheets()
        except Exception as e:
            gftools.create_flag("status_scripts", "problems")
            print(f"[{datetime.datetime.now()}] Error in main_loop: {e}")
        time.sleep(gftools.get_config("updateTime") or 60)


while True:
    try:
        main_loop()
        break
    except KeyboardInterrupt:
        gftools.create_flag("status_scripts", "down")
        break
    except Exception as e:
        wait_minutes = 5
        gftools.create_flag("status_scripts", "problems")
        print(f"[{datetime.datetime.now()}] Fatal error occurred. Restarting in {wait_minutes} minutes...")
        time.sleep(wait_minutes * 60)


    


