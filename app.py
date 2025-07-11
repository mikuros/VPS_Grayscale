#!/root/miniconda3/envs/kasou/bin/python
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import cv2
import uuid
import traceback#エラー掴む用にインポートした
import glob
import time

app = Flask(__name__, template_folder='templates')#template_folderは書かなくてもデフォでtemplatesを探しに行く。

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:#エラー掴む用に追加した
        print("error in index route:", e)
        traceback.print_exc()
        return "Internal error", 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return 'No file part', 400

    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        original_path = os.path.join(UPLOAD_FOLDER, f'{file_id}.jpg')
        processed_path = os.path.join(PROCESSED_FOLDER, f'{file_id}.jpg')
        
        file.save(original_path)

        # OpenCVでグレースケール変換
        image = cv2.imread(original_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(processed_path, gray)

        return redirect(url_for('result', file_id=file_id))
    
    return 'Invalid file', 400

@app.route('/result/<file_id>')
def result(file_id):
    processed_path = os.path.join(PROCESSED_FOLDER, f'{file_id}.jpg')
    if not os.path.exists(processed_path):
        return 'File not found', 404
    return render_template('result.html', file_id=file_id)

@app.route('/download/<file_id>')
def download(file_id):
    return send_from_directory(PROCESSED_FOLDER, f'{file_id}.jpg', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
