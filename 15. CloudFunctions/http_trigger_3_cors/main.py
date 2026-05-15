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
    return ('ok', 200, headers)

    
