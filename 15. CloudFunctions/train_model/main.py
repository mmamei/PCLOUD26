def train_model(request):
	import calendar
	from datetime import datetime
	import json
	import os

	import joblib
	import pandas as pd
	from google.cloud import firestore
	from google.cloud import storage
	from sklearn.linear_model import LinearRegression

	if request.method == 'OPTIONS':
		headers = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET,POST',
			'Access-Control-Allow-Headers': 'Content-Type',
			'Access-Control-Max-Age': '3600',
			'Access-Control-Allow-Credentials': 'true'
		}
		return ('', 204, headers)

	headers = {
		'Access-Control-Allow-Origin': '*'
	}

	request_json = request.get_json(silent=True)
	if request_json is None and 'data' in request.values:
		request_json = json.loads(request.values['data'])

	db = firestore.Client(database='test1')
	query = db.collection('pm10').order_by('datetime', direction=firestore.Query.DESCENDING)

	training_until = None
	if request_json and request_json.get('datetime'):
		training_until = datetime.strptime(request_json['datetime'], '%Y-%m-%d %H:%M:%S')
		query = query.where('datetime', '<=', training_until)

	docs = list(query.limit(10).stream())

	if len(docs) < 4:
		return (json.dumps({'error': 'Not enough documents to train the model'}), 400, headers)

	records = []
	for doc in reversed(docs):
		item = doc.to_dict()
		records.append(
			{
				'datetime': item['datetime'],
				'pm10': float(item['pm10'])
			}
		)

	df = pd.DataFrame(records)
	df['datetime'] = pd.to_datetime(df['datetime'])
	df = df.sort_values('datetime').reset_index(drop=True)

	df['weekday'] = df['datetime'].apply(lambda value: calendar.day_name[value.weekday()])
	df['weekend01'] = df['weekday'].apply(lambda value: 1 if value in ('Saturday', 'Sunday') else 0)
	df['PM10-1'] = df['pm10'].shift(1)
	df['PM10-2'] = df['pm10'].shift(2)
	df['PM10-3'] = df['pm10'].shift(3)
	df = df.iloc[3:, :].copy()

	feature_columns = ['PM10-1', 'PM10-2', 'PM10-3', 'weekend01']
	model = LinearRegression()
	model.fit(df.loc[:, feature_columns], df['pm10'])

	model_path = os.path.join('/tmp', 'model_PM10.pkl')
	joblib.dump(model, model_path)

	storage_client = storage.Client()
	bucket = storage_client.bucket('pcloud2026_ml_models')
	blob = bucket.blob('model_PM10.pkl')
	blob.upload_from_filename(model_path)

	latest_datetime = df['datetime'].max().strftime('%Y-%m-%d %H:%M:%S')
	db.collection('training').document('last_train').set({'last_train': latest_datetime})

	return (
		json.dumps(
			{
				'message': 'Model trained successfully',
				'documents_used': len(records),
				'rows_used_for_training': len(df),
				'training_until': latest_datetime,
				'model_path': 'gs://pcloud2026_ml_models/model_PM10.pkl'
			}
		),
		200,
		headers
	)
