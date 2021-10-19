from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from pathlib import Path
import copy
import sys

n = 2
i_name = ""
if len(sys.argv) == 4:
    i_name = sys.argv[1]
    o_name = sys.argv[2]
    n = int(sys.argv[3])
else:
    print ("HELP: python3 splitter.py input.pdf output.pdf N")
    exit(1)

print (f"Splitting {i_name} into {n} pages, output to {o_name}")

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