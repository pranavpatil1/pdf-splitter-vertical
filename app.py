from flask import Flask, render_template, request, redirect, url_for
from flask import send_file

from werkzeug.utils import secure_filename
import hashlib
import time
import os
import fitz
import matplotlib.pyplot as plt
from pathlib import Path
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from PIL import Image
import numpy as np
import cv2
import sys
import os
import copy
from splitter import split

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 100 # 10 MB max
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        filename = uploaded_file.filename
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        prefix=hash.hexdigest()
        infile = str(prefix) + "_" + secure_filename(uploaded_file.filename)
        outfile = "out_" + infile
        uploaded_file.save(str(prefix) + "_" + secure_filename(uploaded_file.filename))
        split(infile, outfile)
        return send_file(outfile, attachment_filename="split_"+secure_filename(uploaded_file.filename), as_attachment=True)

    return redirect(url_for('index'))
