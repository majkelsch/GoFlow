import requests
import json

response = requests.get('http://127.0.0.1:8080/api', json={"command": "get_projects"})
print(response.json())