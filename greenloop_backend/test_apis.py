import json
import urllib.request
from urllib.error import HTTPError

with open('auth_response.json', 'r') as f:
    data = json.load(f)
    token = data['tokens']['access']

def make_request(path):
    url = f"http://127.0.0.1:8001/api/auth/{path}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    try:
        response = urllib.request.urlopen(req)
        print(f"--- {path} ---")
        print(f"Status: {response.getcode()}")
        print(json.dumps(json.loads(response.read()), indent=2))
    except HTTPError as e:
        print(f"--- {path} ---")
        print(f"Error: {e.code}")
        try:
            print(json.dumps(json.loads(e.read()), indent=2))
        except:
            print(e.read().decode())
    print("\n")

endpoints = [
    "dashboard/live-map/",
    "dashboard/ward-monitoring/",
    "dashboard/complaints/",
    "dashboard/fees/",
    "dashboard/waste-reports/",
    "users/?role=resident"
]

for ep in endpoints:
    make_request(ep)
