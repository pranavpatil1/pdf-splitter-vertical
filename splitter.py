from pdf2image import convert_from_path
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

## PARAMETERS FOR SPLIT
ysize = 75
min_length = .8

n = 0
if len(sys.argv) == 4:
    i_name = sys.argv[1]
    o_name = sys.argv[2]
    n = int(sys.argv[3])
if len(sys.argv) == 3:
    im_name = sys.argv[1]
    o_name = sys.argv[2]
else:
    print ("HELP: python3 splitter.py input.pdf output.pdf")
    exit(1)

## if provided, split into n pages of uniform length
if n != 0:
    print(f"Splitting {i_name} into {n} pages, output to {o_name}")

    pdf = PdfFileReader(i_name)

    pdf_writer = PdfFileWriter()
    first_page = pdf.getPage(0)

    i = n - 1
    while i >= 0:
        current = copy.deepcopy(first_page)
        (x, y) = current.mediaBox.upperRight
        current.mediaBox.upperRight = (x, y * (i + 1) / n)
        current.mediaBox.lowerRight = (x, y * (i) / n)
        pdf_writer.addPage(current)
        i -= 1

    with Path(o_name).open(mode="wb") as output_file:
        pdf_writer.write(output_file)

## otherwise split by designated pagebreaks
else:
    im_path = "page_image.jpg" # intermediate file
    # convert to image
    pages = convert_from_path(i_name)
    pages[0].save(im_path)

    # convert to binary image
    image = cv2.imread(im_path)
    os.remove(im_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # perform morphological transformations to isolate horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # get contours for lines
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # for now split at average x value of each line, 1 page per split
    contours = [[] for _ in range(image.shape[0] // ysize + 1)] # 20px (y-axis) segments
    for c in cnts:
        x = [c[i][0][0] for i in range(len(c))]
        y = [c[i][0][1] for i in range(len(c))]
        for i in range(len(x)):
            contours[y[i] // ysize].append((x[i], y[i]))

    ends = []
    for i in range(len(contours)):
        xs = [contours[i][j][0] for j in range(len(contours[i]))]
        if len(xs) > 1:
            length = max(xs) - min(xs)
            if (length / len(image[0])) > min_length:
                print(length, len(image[0]))
                ys = [contours[i][j][1] for j in range(len(contours[i]))]
                ends.append(round(sum(ys)/len(ys)))

    ends.append(len(image))
    ends = sorted(ends)

    def fig2img(fig):
        """Convert a Matplotlib figure to a PIL Image and return it"""
        import io
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        return img

    pages = []
    start = 0
    for end in ends:
        end = end - ysize // 2
        if start > end: # if pagebreak already detected for end of last page
            break
        new_page = image[start:end]

        shape = (len(new_page), len(new_page[0]), 3)
        new_page = np.array(new_page).reshape(shape)
        im = Image.fromarray(new_page)
        pages.append(im)

        start = end + ysize

    pages[0].save(o_name, "PDF" ,resolution=100.0, save_all=True, append_images=pages[1:])