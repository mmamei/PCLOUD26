from requests import post
import json
from datetime import datetime

url = 'https://europe-west8-pcloud2026.cloudfunctions.net/hello_http2'
#$.post(url,{'data':JSON.stringify(dati)},
r = post(url,data={'data':json.dumps({'time':str(datetime.now()),'value':[465,45]})})
print(r.status_code)
print(r.text)


