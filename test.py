import requests
import json
import gfdb
import gfi
import gfe
import gftools

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
#gfi.getGmailData()
#gfdb.transfer_emailsToTasks()

#print(gfdb.get_client(id=1)['projects'][0]['id'])

#
# 
#gfe.exportTasksToSheets()


#client_id = gfdb.get_client(id=gfdb.get_client_emails(email="bodylovebrno@email.cz")[0]['client_id'])['id']
#print(gfdb.get_client(id=client_id)['projects'][0]['id'])



#print(gfdb.get_project(id=0))

#gfdb.assignProjectToClient(1,1)
#gfdb.assignProjectToClient(1,2)


#print(gfdb.get_client(id=1)['projects'])



gftools.wait_for_flag("gs_sync", "syncing", 5, lambda: gfe.end_task(support_id="SUP250001"), max_retries=5, debug=True)