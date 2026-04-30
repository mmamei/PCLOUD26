from google.cloud import storage
import os

cred_file = 'credentials.json' if os.path.exists('credentials.json') else 'secret.json'
client = storage.Client.from_service_account_json(cred_file)
bucket = client.bucket(os.environ.get('GCS_BUCKET', 'pcloud2026-2'))
source_file_name = 'test.jpg'
destination_blob_name = source_file_name
blob = bucket.blob(destination_blob_name)
blob.upload_from_filename(source_file_name)
print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))

