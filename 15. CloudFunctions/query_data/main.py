def query_data(request):
    from google.cloud import firestore
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
    N = int(request_json['N'])
    
    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    db = firestore.Client(database='test1')

    docs = db.collection('pm10').order_by('datetime', direction=firestore.Query.DESCENDING).limit(N).stream()

    results = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        results.append(item['pm10'])

    return (json.dumps(results), 200, headers)

    
