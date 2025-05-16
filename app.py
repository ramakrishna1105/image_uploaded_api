# image_uploaded_api
from flask import Flask, request, jsonify, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import uuid
import config

app = Flask(__name__)
app.config.from_object(config)

mysql = MySQL(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

        # Save metadata in DB
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO uploaded_images (filename) VALUES (%s)", (unique_name,))
        mysql.connection.commit()
        cursor.close()

        image_url = f"http://localhost:5000/uploads/{unique_name}"
        return jsonify({'message': 'Image uploaded successfully', 'image_url': image_url}), 201
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
