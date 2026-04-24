
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from datetime import datetime
import json
from google.cloud import firestore
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


# requires pyopenssl
# pip install pyopenssl

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pcloud2026-secret-key'

db = 'app-accel'
db = firestore.Client.from_service_account_json('secret.json', database=db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username


@login_manager.user_loader
def load_user(username):
    doc = db.collection('users').document(username).get()
    if doc.exists:
        return User(username)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect(url_for('static', filename='login.html'))
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    next_page = request.form.get('next') or '/'
    doc = db.collection('users').document(username).get()
    if doc.exists and check_password_hash(doc.to_dict()['password'], password):
        login_user(User(username))
        return redirect(next_page)
    return redirect(url_for('login') + '?error=1&next=' + next_page)


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        return redirect(url_for('login') + '?error=empty')
    user_ref = db.collection('users').document(username)
    if user_ref.get().exists:
        return redirect(url_for('login') + '?error=exists')
    user_ref.set({'password': generate_password_hash(password)})
    login_user(User(username))
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET'])
@login_required
def main():
    return redirect(url_for('static', filename='app.html'))


@app.route('/graph', methods=['GET'])
@login_required
def graph():
    return redirect(url_for('static', filename='graph.html'))


@app.route('/upload_data_buffer',methods=['POST'])
def upload_data_buffer():
    #print(request.form)
    print(json.loads(request.values['data']))
    return 'saved'

@app.route('/upload_data',methods=['POST'])
def upload_data():
    i = request.values['i']
    j = request.values['j']
    k = request.values['k']
    print(i,j,k)
    return 'saved'


@app.route('/accelerometer_data', methods=['POST'])
@login_required
def accelerometer_data():
    avg_magnitude = request.values.get('average_magnitude')
    sample_count = request.values.get('sample_count')
    timestamp_ms = request.values.get('ts')

    print('accelerometer_data:', avg_magnitude, sample_count, timestamp_ms)

    coll = current_user.username
    doc_id = f"acc-{timestamp_ms}" if timestamp_ms else None
    payload = {
        'avg_magnitude': float(avg_magnitude) if avg_magnitude is not None else None,
        'timestamp_ms': int(timestamp_ms) if timestamp_ms is not None else None,
        'sample_count': int(sample_count) if sample_count is not None else None
    }

    if doc_id:
        db.collection(coll).document(doc_id).set(payload)
    else:
        db.collection(coll).add(payload)
    
    return jsonify({
        'status': 'saved',
        'average_magnitude': avg_magnitude,
        'sample_count': sample_count,
        'ts': timestamp_ms
    })


@app.route('/get_data', methods=['GET'])
@login_required
def get_data():
    coll = current_user.username

    now_ms = int(datetime.utcnow().timestamp() * 1000)
    end_sec = now_ms // 1000
    start_sec = end_sec - 59

    start_ms = start_sec * 1000
    end_ms = (end_sec + 1) * 1000 - 1

    values_by_sec = {}

    docs = db.collection(coll) \
        .where('timestamp_ms', '>=', start_ms) \
        .where('timestamp_ms', '<=', end_ms) \
        .stream()

    for entity in docs:
        item = entity.to_dict()
        ts_ms = item.get('timestamp_ms')
        avg = item.get('avg_magnitude')

        if ts_ms is None or avg is None:
            continue

        sec = int(ts_ms) // 1000
        if sec < start_sec or sec > end_sec:
            continue

        # If multiple readings fall in the same second, keep the most recent one.
        prev = values_by_sec.get(sec)
        if prev is None or ts_ms >= prev['ts_ms']:
            values_by_sec[sec] = {'ts_ms': ts_ms, 'avg': float(avg)}

    result = []
    for sec in range(start_sec, end_sec + 1):
        if sec in values_by_sec:
            result.append(values_by_sec[sec]['avg'])
        else:
            result.append(0)

    return jsonify(result)




@app.route('/upload',methods=['POST'])
def upload():
    # check if the post request has the file part

    file = request.files['file']

    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")

    file.save(os.path.join(f'tmp/test_{current_time}.png'))
    return 'saved'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, ssl_context='adhoc')

