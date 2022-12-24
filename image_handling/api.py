import cv2
import numpy as np
from flask import Flask, flash, request, send_file
from werkzeug.utils import secure_filename

from facial_stuffs import *
from image_stuffs import *

from config import *

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
EDIT_PREFIX = 'edited_'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = INPUT_DIR

f = FaceRecognizer()

@app.route('/')
def home():
    return 'Hello, world!'

@app.route('/mosaic', methods=['GET'])
def mosaic_get():
    image_name = request.args['image']

    try:
        image = cv2.imread(INPUT_DIR + image_name)
    except:
        return 'false'

    detections = f.image_to_detections(image)
    image = mosaic_image(image, detections[0])
    cv2.imwrite(OUTPUT_DIR + EDIT_PREFIX + image_name, image)

    return 'true'

@app.route('/mosaic', methods=['POST'])
def mosaic_post():
    if 'file' not in request.files:
        flash('No file part')
        return 'No file part.'
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

    file_bytes = np.fromfile(file, np.uint8)

    img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    detections = f.image_to_detections(img)
    img = mosaic_image(img, detections[0])
    cv2.imwrite(OUTPUT_DIR + EDIT_PREFIX + filename, img)

    return send_file(OUTPUT_DIR + EDIT_PREFIX + filename, mimetype='image/png')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(port=PORT)