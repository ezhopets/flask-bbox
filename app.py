import os
from werkzeug.utils import secure_filename
from flask import Flask,flash,request,redirect,send_file,render_template

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure

import cv2
from pdf2image import convert_from_path
import zipfile
import shutil


PPM_DIR = "tmp"
IMAGES_DIR = "images"
UPLOAD_DIR = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_DIR'] = UPLOAD_DIR


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            os.mkdir(UPLOAD_DIR)
        except:
            pass

        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_DIR'], filename)
            file.save(filename)

            bbox(filename, PPM_DIR, IMAGES_DIR)

            filename = zip_dir(IMAGES_DIR)

            remove_dir(IMAGES_DIR)
            remove_dir(PPM_DIR)

            return redirect('/downloadfile/'+ filename)
        return render_template('uploadfile_error.html')

    return render_template('uploadfile.html')


@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_DIR + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')

def parse_layout(page, pages, layout, numpage, numline, IMAGES_DIR):
    page_width, page_height = page.mediabox[-2:]

    for lt_obj in layout:
        if isinstance(lt_obj, LTTextLine):
            line = next(numline)
            name = f"./{IMAGES_DIR}/{numpage + 1}_{line}.jpg"

            pages[numpage].save(name, 'JPEG')
            image = cv2.imread(name)
            height = image.shape[0]
            width = image.shape[1]

            start_point = (int(lt_obj.bbox[0]), int(height - lt_obj.bbox[1]))
            end_point = (int(lt_obj.bbox[2]), int(height - lt_obj.bbox[3]))

            image = cv2.rectangle(image, start_point, end_point, (0, 0, 255))
            cv2.imwrite(name, image)

        elif isinstance(lt_obj, LTFigure) or isinstance(lt_obj, LTTextBox):
            parse_layout(page, pages, lt_obj, numpage, numline, IMAGES_DIR)


def zip_dir(path):
    zf = zipfile.ZipFile(f"{UPLOAD_DIR}{path}.zip", 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(path):
        for file_name in files:
            zf.write(os.path.join(root, file_name), arcname = file_name)
        return f"{path}.zip"

def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print(f"Error: {dir_path} : {e.strerror}")


def newline( ):
    i = 0
    while True:
        yield i
        i += 1


def bbox(filename, PPM_DIR, IMAGES_DIR):
    try:
        os.mkdir(PPM_DIR)
        os.mkdir(IMAGES_DIR)
        os.mkdir(UPLOAD_DIR)
    except:
        pass

    pages = convert_from_path(filename, dpi=72, output_folder=PPM_DIR)

    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    print(f"Number of pages: {len(pages)}")
    for numpage, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        layout = device.get_result()
        parse_layout(page, pages, layout, numpage, newline(), IMAGES_DIR)
        print(f"Current page: {numpage + 1}")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
