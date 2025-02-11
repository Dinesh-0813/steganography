from flask import Flask, request, render_template, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from google.cloud import storage
from Crypto.Cipher import AES
import base64
import speech_recognition as sr

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'

# Google Cloud Storage setup
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'
bucket_name = 'your_bucket_name'

# Encryption functions
def encrypt_data(data, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    key = request.form['key']
    message = request.form['message']

    if file and key and message:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        encrypted_message = encrypt_data(message, key)

        # Upload the file to Google Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(filepath)

        return jsonify({"message": "File uploaded successfully!", "filename": filename})
    return "Error: Missing required fields"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'
