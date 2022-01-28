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

# files here will be deleted
TEMP_DIR = "tmp"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    # after the file is downloaded, clear the tmp directory (files here are after completed runs, probably)
    @app.after_request
    def delete(response):
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))
        return response

    # make sure file was uplaoded
    uploaded_file = request.files['file']
    print (uploaded_file.filename)
    if uploaded_file.filename != '':
        filename = uploaded_file.filename
        print (filename)

        file_ext = os.path.splitext(filename)[1]
        print (file_ext)
        # make sure pdf extension
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        # add hash to beginning of file to ensure uniqueness
        hash = hashlib.sha1()
        hash.update(str(time.time()).encode('utf-8'))
        prefix=hash.hexdigest()
        infile = str(prefix) + "_" + secure_filename(uploaded_file.filename)
        outfile = "out_" + infile
        # save locally because I don't know how to do it otherwise
        uploaded_file.save(infile)
        # generate a splitted file
        split(infile, outfile)
        # add tmp dir if needed
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        # move files to tmp because (nearly) done using them
        os.rename(infile, TEMP_DIR + "/" + infile)
        os.rename(outfile, TEMP_DIR + "/" + outfile)
        # send user a file to download
        return send_file(TEMP_DIR + "/" + outfile, attachment_filename="split_"+secure_filename(uploaded_file.filename), as_attachment=True)

    return redirect(url_for('index'))
