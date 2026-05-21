def save_data(request):
    from google.cloud import firestore
    from datetime import datetime
    import json
    if request.method == 'OPTIONS':
        print('------ options')
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)

    request_json = json.loads(request.values['data'])
    request_json['datetime'] = datetime.strptime(request_json['datetime'], '%Y-%m-%d %H:%M:%S')
    request_json['pm10'] = float(request_json['PM10'])
    del request_json['PM10']
    #request_json = request.data.decode('utf-8')
    print('>>>>>>>>>>>>>>>>>>>>>>>')
    print(request_json)
    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    # request_json = {'datetime': '2020-01-15 00:00:00', 'PM10': '71.0'}
    db = firestore.Client(database='test1')
    
    # converti in stringa request_json['datetime']
    sdatetime = request_json['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    db.collection('pm10').document(sdatetime).set(request_json)

    # leggi da firestore database test1 collection training il documento con id last_train e prendi il campo last_train
    doc_ref = db.collection('training').document('last_train')
    doc = doc_ref.get()
    if doc.exists:
        last_train = doc.to_dict()['last_train']
        print(f"Last train: {last_train}")
    else:
        print("No such document!")
    
     # se request_json['datetime'] è maggiore di last_train di almeno 7 giorni, chiama la funzione di training
     # con la libreria requests, url della funzione di training è https://europe-west8-pcloud2026.cloudfunctions.net/train_model, metodo POST

    if (request_json['datetime'] - datetime.strptime(last_train, '%Y-%m-%d %H:%M:%S')).days >= 7:
        import requests
        r = requests.post('https://europe-west8-pcloud2026.cloudfunctions.net/train_model')
        print(f"Train model response: {r.status_code} - {r.text}")  
    return ('ok', 200, headers)

    
