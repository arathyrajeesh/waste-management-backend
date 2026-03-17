import requests

session = requests.Session()
res = session.get('http://127.0.0.1:8000/admin/login/')
csrftoken = session.cookies['csrftoken']

post_data = {
    'username': 'admin@gmail.com',
    'password': 'admin135',
    'csrfmiddlewaretoken': csrftoken,
    'next': '/admin/'
}

res2 = session.post('http://127.0.0.1:8000/admin/login/', data=post_data, allow_redirects=False)
print("Status Code:", res2.status_code)
print("Headers:", res2.headers)
if res2.status_code == 200:
    print("Failed to login (still on login page)")
elif res2.status_code == 302:
    print("Redirected! Login successful.")

