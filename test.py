import requests

response = requests.post(
    "http://192.168.1.14:8080/api",
    json={"command": "create_task", "task_data":{"client": "Test Client", "project": "Test Project", "title": "Test Task", "description": "This is a test task.", "last_edit_by": "michal@cloudbusiness.cz"}}
)

print(response.json())
