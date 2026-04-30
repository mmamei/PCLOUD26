
from flask import Flask, request, redirect, url_for, send_file, render_template
import os
from werkzeug.utils import secure_filename
from google.cloud import storage
from google.cloud import firestore
import datetime

app = Flask(__name__)

db = 'pcloud2026-app1'
db = firestore.Client.from_service_account_json('secret.json', database=db)
#db = firestore.Client(database=db)

fstorage = storage.Client.from_service_account_json('secret.json')

@app.route('/',methods=['GET'])
def main():
     return redirect(url_for('static', filename='camera.html'))


@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return redirect(url_for('static', filename='camera.html'))
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        fname = secure_filename(file.filename)
        print(fname)
        #file.save(os.path.join('tmp/',fname))

        # trova l'orairo corrente in formato YYYYMMDD_HHMMSS
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        # sala il timestamp in un database firestore in una collezione che si chiama 'photos' e con un documento che si chiama 'latest' e un campo che si chiama 'timestamp' con il valore del timestamp
        
        
        doc_ref = db.collection('photos').document(timestamp)
        doc_ref.set({'timestamp': timestamp, 'filename': f'{timestamp}.png'})

        
        bucket = fstorage.bucket('pcloud2026-2')
        source_file_name = fname
        
        destination_blob_name = f'{timestamp}.png'
       
        blob = bucket.blob(destination_blob_name)

        #blob.upload_from_filename(os.path.join('tmp/',fname))

        blob.upload_from_string(file.read(),content_type=file.content_type)

        return 'File {} uploaded to {}.'.format(source_file_name, destination_blob_name)


@app.route('/retrieve/<fname>',methods=['GET'])
def retrieve(fname):
    storage_client = fstorage
    bucket = storage_client.bucket('pcloud2026-2')
    blob = bucket.blob(fname)
    blob.download_to_filename(os.path.join('tmp/',fname))
    return send_file(os.path.join('../../tmp/',fname))


@app.route('/retrieve2/<fname>',methods=['GET'])
def retrieve2(fname):
    storage_client = fstorage
    bucket = storage_client.bucket('pcloud2026-2')
    blob = bucket.blob(fname)
    # https://cloud.google.com/storage/docs/access-control/signing-urls-with-helpers#code-samples
    serving_url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15), # This URL is valid for 15 minutes
        method="GET") # Allow GET requests using this URL.
    return redirect(serving_url)

@app.route('/retrieve3',methods=['GET'])
def retrieve3():
    storage_client = fstorage
    bucket = storage_client.bucket('pcloud2026-2')
    fname = 'test.jpg'
    blob = bucket.blob(fname)
    blob.make_public()
    url = blob.public_url
    return redirect(url)


@app.route('/getphpto', methods=['GET', 'POST'])
def getphpto():
    if request.method == 'GET':
        return render_template('getphpto_form.html')

    start_date_str = request.form.get('start_date', '').strip()
    end_date_str = request.form.get('end_date', '').strip()

    if not start_date_str or not end_date_str:
        return render_template(
            'getphpto_form.html',
            error='Inserisci sia la data di inizio sia la data di fine.'
        )

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template(
            'getphpto_form.html',
            error='Formato data non valido. Usa YYYY-MM-DD.'
        )

    if start_date > end_date:
        return render_template(
            'getphpto_form.html',
            error='La data di inizio deve essere minore o uguale alla data di fine.'
        )

    start_ts = start_date.strftime('%Y%m%d') + '_000000'
    end_ts = end_date.strftime('%Y%m%d') + '_235959'

    query = (
        db.collection('photos')
        .where('timestamp', '>=', start_ts)
        .where('timestamp', '<=', end_ts)
        .order_by('timestamp')
    )

    bucket = fstorage.bucket('pcloud2026-2')
    photos = []

    for doc in query.stream():
        data = doc.to_dict() or {}
        timestamp = data.get('timestamp', doc.id)
        filename = data.get('filename', f'{timestamp}.png')
        blob = bucket.blob(filename)
        signed_url = blob.generate_signed_url(
            version='v4',
            expiration=datetime.timedelta(minutes=15),
            method='GET'
        )
        photos.append({
            'timestamp': timestamp,
            'filename': filename,
            'url': signed_url,
        })

    return render_template(
        'getphpto_gallery.html',
        photos=photos,
        start_date=start_date_str,
        end_date=end_date_str,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, ssl_context='adhoc')

