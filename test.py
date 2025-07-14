import requests

response = requests.post(
    "http://192.168.0.50:8080/api",
    json={"command": "create_task", "task_data":{"client": "Test Client", "project": "Test Project", "title": "Test Task", "description": "This is a test task."}}
)

print(response.json())
