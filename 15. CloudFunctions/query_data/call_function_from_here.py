from requests import post
import json
from datetime import datetime

url = 'https://europe-west8-pcloud2026.cloudfunctions.net/query_data'
#$.post(url,{'data':JSON.stringify(dati)},
r = post(url,data={'data':json.dumps({'N':5})})
print(r.status_code)
r = r.json()
print(r)

url = 'https://europe-west8-pcloud2026.cloudfunctions.net/predict_PM10'
d = {'PM10-1':r[-1],'PM10-2':r[-2],'PM10-3':r[-3],'weekend01':0}
r = post(url,data={'data':json.dumps(d)})
print(r.status_code)
print(r.text)



