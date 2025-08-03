import requests
import json
import gfdb
import gfi


##response = requests.post('http://127.0.0.1:8080/api', json={"command": "insert_timetrack", "data": {"support_id": "SUP250001", "email": "michal@cloudbusiness.cz"}})
##response = requests.post('http://127.0.0.1:8080/api', json={"command": "end_timetrack", "data": {"support_id": "SUP250001", "email": "michal@cloudbusiness.cz"}})
#
#payload = {"command":"insert_client","data":{"first_name": "Michal", "last_name": "Schenk", "email": "michal@cloudbusiness.cz"}}
#response = requests.post('http://127.0.0.1:8080/api', json=payload)
#print(response.json())



#import gfdb
#
##print(gfdb.get_client(id=1)['emails'])
#
#
#
#
#print(gfdb.get_client_emails(client_id=gfdb.get_client(id=gfdb.get_task(support_id="SUP250001")['client_id'])['id'])[0]['email'])
#
#task_id = "SUP250001"
#task = gfdb.get_task(support_id=task_id)
#client = gfdb.get_client(id=task['client_id'])
#mails = gfdb.get_client_emails(client_id=client['id'])
#mail=mails[0]['email']
#print(mail)


#gfi.getSolidpixelsData()
gfdb.transfer_emailsToTasks()


#print(gfdb.get_client(id=gfdb.get_client_emails(email="kozakova@interieryhk.cz")[0]['client_id']))