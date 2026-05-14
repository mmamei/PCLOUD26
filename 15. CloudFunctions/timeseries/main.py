



def predict_PM10(request):
    import joblib
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

    print('>>>>>>>>>>>>>>>>>>>>>>>')
    request_json = json.loads(request.values['data'])
    print(request_json)
    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    model = joblib.load('model_PM10.pkl')
    print(request_json)
    print(request_json['PM10-1'])
    yp = model.predict([list(request_json.values())])
    return str(yp[0]), 200, headers