# PDF splitter

This program will split a PDF vertically into N equal pages. This is useful because OneNote always exports PDFs as one long page and (robotics) professors & TAs hate that!

## Installation

You can do either

```
pip3 install -r requirements.txt
```

or alternatively

```
pip3 install PyPDF2
```

To run, and split a page into N pages, run the following command. input.pdf should already exist while output.pdf will be created.

```
python3 splitter.py input.pdf output.pdf N
```
