from flask import Flask,request,redirect,url_for
import json
from google.cloud import bigquery

project_id = 'pcloud2026'
region = 'europe-west8'
db_id = 'appbq'
table_id = 'pm10'
db = bigquery.Client.from_service_account_json('secret.json')
table_full_id = f'{project_id}.{db_id}.{table_id}'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('static', filename='index.html'))

@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('static', filename='graph.html'))

@app.route('/graph', methods=['GET'])
def graph():
    return redirect(url_for('static', filename='graph.html'))



@app.route('/sensors',methods=['GET'])
def sensors():
    return json.dumps(list(db.keys())), 200


@app.route('/sensors/<s>',methods=['POST'])
def add_data(s):
    data = request.values['data']
    val = float(request.values['val'])

    rows = [{'sensor': s, 'value': val, 'datetime': data}]
    errors = db.insert_rows_json(table_full_id, rows)  # Make an API request.
        
    return 'ok',200

@app.route('/sensors/<s>',methods=['GET'])
def get_data(s):

    query = f"""
    SELECT *
    FROM `{table_full_id}`
    """
    query_job = db.query(query)
    r = []
    i = 0
    for row in query_job:
        #print(row)
        # Row values can be accessed by field name or index.
        #print(f'name={row[0]} datetime={row["datetime"]}')
        r.append([i, row['value']])
        i += 1
    return json.dumps(r),200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

