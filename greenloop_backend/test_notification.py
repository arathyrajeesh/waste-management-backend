import json
import urllib.request
from urllib.error import HTTPError

with open('auth_response.json', 'r') as f:
    data = json.load(f)
    token = data['tokens']['access']

def assign_worker(complaint_id, worker_id):
    url = f"http://127.0.0.1:8001/api/complaints/{complaint_id}/"
    data = json.dumps({"assigned_worker": worker_id}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PATCH')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        print(f"Status: {response.getcode()}")
        print(json.dumps(json.loads(response.read()), indent=2))
    except HTTPError as e:
        print(f"Error: {e.code}")
        print(e.read().decode())

print("Assigning worker ID 5 to complaint ID 4...")
assign_worker(4, 5)
