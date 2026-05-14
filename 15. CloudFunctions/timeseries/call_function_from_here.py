from requests import post

data = {'PM10-1':465,'PM10-2':45,'PM10-3':34,'weekend01':0}
r = post('https://europe-west8-pcloud2026.cloudfunctions.net/predict_PM10',json=data)
print(r.status_code)
print(r.text)

