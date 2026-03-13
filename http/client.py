from requests import get, post

base_url = 'http://localhost:80'

r = post(f'{base_url}/sensors/sensor1', 
         data={'data':'2026-03-13', 'val': 25.5})
print(r.status_code)
