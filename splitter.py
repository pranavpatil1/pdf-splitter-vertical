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

# convert y-pixel value to index in list of windows for sliding window
def pixel2window(y, length, ysize):
    count = 0
    window_frac = 3
    for i in range(0, length, ysize // window_frac):
        if y >= i and y <= i + ysize:
            return count
        count += 1
    return count

def split(i_name=None, o_name=None, n=0):
    ## PARAMETERS FOR SPLIT
    ysize = 50          # height of window
    min_length = .7     # min length for line, fraction of width of page
    max_height = .2     # max height for line, fraction of height of window

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
        doc = fitz.open(i_name)
        page = doc.load_page(0)  # number of page
        pix = page.get_pixmap()
        pix.save(im_path)

        # convert to binary image
        image = cv2.imread(im_path)[...,::-1]
        os.remove(im_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # perform morphological transformations to isolate horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,1))
        detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        # get contours for lines
        cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        
        # result = image.copy()
        # for c in cnts:
        #     cv2.drawContours(result, [c], -1, (36,255,12), 2)

        # cv2.imshow('result', result[3000:])
        # cv2.waitKey()

        # for now split at average x value of each line, 1 page per split
        contours = [[] for _ in range(image.shape[0])] # 20px (y-axis) segments
        contour_count = 0
        for c in cnts:
            x = [c[i][0][0] for i in range(len(c))]
            y = [c[i][0][1] for i in range(len(c))]
            for i in range(len(x)):
                contours[pixel2window(y[i], image.shape[0], ysize)].append((x[i], y[i], contour_count))
            contour_count += 1

        ends = []

        # loop through windows and add horizontal line x-values to ends list
        for i in range(len(contours) - 1):
            xcurr = [contours[i][j][0] for j in range(len(contours[i]))]
            ycurr = [contours[i][j][1] for j in range(len(contours[i]))]
            ids = [contours[i][j][2] for j in range(len(contours[i]))]
            if len(xcurr) > 0:
                # length = max(x) - min(x) for each contour
                ids_unique = list(set(ids))
                x_by_id = [[] for _ in range(len(ids_unique))]
                for j in range(len(xcurr)):
                    x_by_id[ids_unique.index(ids[j])].append(xcurr[j])

                length_list = [max(_) - min(_) for _ in x_by_id]
                # length = max(xcurr) - min(xcurr)
                length = max(length_list)
                height = max(ycurr) - min(ycurr)
                # print(length, length / len(image[0]))
                if length / len(image[0]) > min_length:
                    # print('breakkkk')
                    ys = [contours[i][j][1] for j in range(len(contours[i]))]
                    pos = round(sum(ys)/len(ys))
                    if pos not in ends:
                        ends.append(pos)

        ends.append(len(image))
        ends = sorted(ends)

        ## create new pages
        pages = []
        start = 0
        for end in ends:
            if start > end:
                break
            
            new_page = image[int(start):int(end)]

            shape = (len(new_page), len(new_page[0]), 3)
            new_page = np.array(new_page).reshape(shape)
            im = Image.fromarray(new_page)
            pages.append(im)

            start = end
        
        if o_name != None:
            pages[0].save(o_name, "PDF" ,resolution=100.0, save_all=True, append_images=pages[1:])
        else:
            return pages

if __name__ == '__main__':
    if len(sys.argv) == 4:
        i_name = sys.argv[1]
        o_name = sys.argv[2]
        n = int(sys.argv[3])
    if len(sys.argv) == 3:
        i_name = sys.argv[1]
        o_name = sys.argv[2]
        n = 0
    else:
        print ("HELP: python3 splitter.py input.pdf output.pdf")
        exit(1)
