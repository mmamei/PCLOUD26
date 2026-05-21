from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import send_file
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import texttospeech, storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="secret.json"
app = Flask(__name__)
import json
@app.route("/", methods=['POST', 'GET'])
def index():
    return redirect(url_for('static', filename='camera.html'))
    #return send_file("static/output.mp3",as_attachment=True)


cont = 0
@app.route('/upload',methods=['POST'])
def upload():
    global cont
    cont += 1
    storage_client = storage.Client.from_service_account_json('secret.json')
    # check if the post request has the file part
    file = request.files['file']
    bucket = storage_client.bucket('pcloud2026-1')
    blob = bucket.blob(f'test5.jpg')
    blob.upload_from_string(file.read(), content_type=file.content_type)

    vertexai.init(project='pcloud2026', location="europe-west8")
    model = GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content(
        [
            # Part.from_image(Image.load_from_file("image.jpg"))
            Part.from_uri(
                "gs://pcloud2026-1/test5.jpg",
                mime_type="image/jpeg",
            ),
            "Descrivi cosa è rappresentato nell'immagine in massimo 10 parole, iniziando con: Vedo..",
        ]
    )

    txt = response.text

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=txt)
    voice = texttospeech.VoiceSelectionParams(
        language_code="it-IT", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open('16. GenAI/static/output.mp3', 'wb') as out:
        out.write(response.audio_content)
    return json.dumps(['output.mp3',txt])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=222, debug=True, ssl_context='adhoc')