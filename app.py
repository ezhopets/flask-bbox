import os
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, send_file, render_template

from bbox import bbox

PPM_DIR = "tmp"
IMAGES_DIR = "images"
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, template_folder='templates')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_DIR'], filename)
            file.save(filename)

            filename = bbox(filename, PPM_DIR, IMAGES_DIR, UPLOAD_DIR)
            if filename is not None:
                return redirect('/downloadfile/' + filename)
        return render_template('uploadfile_error.html')

    return render_template('uploadfile.html')


@app.route("/downloadfile/<filename>", methods=['GET'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_DIR + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


if __name__ == "__main__":
    app.config['UPLOAD_DIR'] = UPLOAD_DIR
    app.run(host='0.0.0.0')
