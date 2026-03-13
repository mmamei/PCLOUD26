from google.cloud import storage
client = storage.Client.from_service_account_json('secret.json')
#bucket = client.create_bucket('upload-mamei-1')
b  = 'pcloud2026-1'
bucket = client.lookup_bucket(b)
if bucket is None:
    bucket = client.create_bucket(b)
    print("Bucket {} creato.".format(b))
else:
    print("Bucket {} già esistente.".format(b))
source_file_name = 'test.jpg'
destination_blob_name = source_file_name
blob = bucket.blob(destination_blob_name)
blob.upload_from_filename(source_file_name)
print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))