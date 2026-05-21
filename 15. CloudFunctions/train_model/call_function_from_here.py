from requests import post

payload = {'datetime': '2019-05-02 00:00:00'}
r = post('https://europe-west8-pcloud2026.cloudfunctions.net/train_model', json=payload)
print(r.status_code)
print(r.text)
