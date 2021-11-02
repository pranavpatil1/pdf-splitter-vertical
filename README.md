# PDF splitter

Split PDF vertically based on horizontal line separators or into N pages of uniform length. From our experience, this keeps professors and TAs very happy!

## Installation

```
pip install -r requirements.txt
```

To run with horizontal line page separators, do
```
python splitter.py input.pdf output.pdf
```
Otherwise, to split into N pages, do
```
python splitter.py input.pdf output.pdf N
```