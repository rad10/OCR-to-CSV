# OCR to CSV
This project is made for intended use by STEMTech Neighborhood Academy. This tool is a rework of its predecessor, [htmlToCsv](https://github.com/rad10/htmlToCsv) as it now has a GUI and built in OCR generator.

The purpose of this project is to take data from sign in sheets and put them in a digital database so that statistical analysis can be done with the data. This project is most useful for people who need to keep track of who enters and leaves a building and it needs to be done on paper.

The task is to make a functional tool that can take data from the sign in sheets in either the form of an image or a PDF (with the latter being most preferred.) and organize that data so that it may be used in an excel sheet.

With that the 
and that is the full intention of this program.
## Special Thanks
This is special thanks for the sources and libraries used to build this thing
### Libraries used:

 - [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
 - [OpenCV](https://opencv.org/)
 - [TKinter](https://docs.python.org/3/library/tkinter.html)
### Sources:
The sources that helped me figure out how to do several of the things i needed to do.
 - [StackExchange](https://stackexchange.com/) (There are too many articles used for me to link)
 - [Medium](https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26) for my work with table slicing.
 - [PAGE](http://page.sourceforge.net/) for templating my GUI outlines

## Python
The python variation of this application was the original version of this program. It works best and is the most up to date.
> tested with `Python 3.6.4`

### Libraries Used:

 - [pytesseract](https://pypi.org/project/pytesseract/)
 - [opencv-python](https://pypi.org/project/opencv-python/)
 - [tkinter](https://docs.python.org/3/library/tkinter.html)
 - ImageTk

This variant contains internal `debug()` methods that will activate when `Debug = True` to see what values are in script. (or you can use breakpoints for debugging.)
