# import this library to automatically download and install the rest of the libraries if they do not exist
import pip

# if opencv isnt installed, itll install it for you
from sys import argv
try:
    import numpy as nm
    import cv2
except ImportError:
    if(hasattr(pip, "main")):
        pip.main(["install", "opencv-python"])
    else:
        pip._internal.main(["install", "opencv-python"])
    import numpy as nm
    import cv2
try:
    from PIL import Image
except ImportError:
    import Image

# if tesseract isnt installed, itll install it for you
try:
    import pytesseract as tess
except ImportError:
    if(hasattr(pip, "main")):
        pip.main(["install", "pytesseract"])
    else:
        pip._internal.main(["install", "pytesseract"])
    import pytesseract as tess

from tkinter import TK

# Functions
Debug = False


def debug(content):
    if Debug:
        print(content)


def readfile(dir):
    return open(dir, "r").read()


def exportToFile(dir, content):
    open(dir, "w").write(content)


def appendToFile(dir, content):
    try:
        inside = open(dir, "r").read()
        open(dir, "w").write(inside + content)
    except:
        open(dir, "w").write(content)


def isNum(num):
    try:
        return float(str(num)).is_integer()
    except:
        return False

def checkHoriz(img, ind, height=1):
    value = True
    for i in range(height):  # i increments by additional heights for thickness of border
        sum = 0
        for space in img[ind + i]:
            if space > 0:
                sum += 1
        # will return false as soon as one thickness is not a border
        value *= (sum > len(img)/2)
    return value


def checkVert(img, ind, width=1):
    value = True
    for i in range(width):
        sum = 0
        for space in img:
            if space[ind + i] > 0:
                sum += 1
        value *= (sum > len(img)/2)
    return value

def help():
    print(__file__, "[OPTION]","[HTML File]")
    print("This program is intended to take data from inkspace HTML files and append it to a CSV file in the same directory.")
    print("INSTRUCTIONS: save inkspace output to an HTML file in the same directory as this program. Once done, run this program. Profit.")
    print("OPTIONS:")
    print("-h | --help\t\t\tPrints this help screen.")
    print("-d | --display\t\t\tPrints the output of the CSV into the console as well as into the file.")


# Generator
#### PHASE 1: manipulate image to clearly show tabs
def imageScraper(file=""):
    if not (file.split(".") in ["jpg", "jpeg", "png"]):
        return
    image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

    spreadsheet = []
    vertBorders = []  # array thatll have all points of borders
    horizBorders = []
    boldVert = [0, 0] # start and end
    boldHoriz = [0, 0] # start and end
    # find borders
    for h in range(len(image) - 4):
        if checkHoriz(image, h, 4) and boldHoriz[0] > 0:
            boldHoriz[1] = h
        elif checkHoriz(image, h, 4):
            boldHoriz[0] = h + 4

    for w in range(len(image[0]) - 4):
        if checkVert(image, w, 4) and boldVert[0] > 0:
            boldVert[1] = w
        elif checkVert(image, w, 4):
            boldVert[0] = w + 4

    spreadsheet = image[boldHoriz[0]:boldHoriz[1], boldVert[0]:boldVert[1]]


def arrayToCsv(directory):
    """takes a matrix and returns a string in CSV format.
    var directory: a string[][] matrix that contains the information of people at the center.
    returns: a string that contains all the information in CSV format.
    """
    cvarray = ''
    for i in range(len(directory)):
        for e in range(len(directory[i])-1):
            if (isNum(directory[i][e])):
                cvarray += (directory[i][e]+", ")
            else:
                cvarray += (directory[i][e]+", ")
        cvarray += (directory[i][-1]+"\n")
        debug(("cvarray["+str(i)+"]:", cvarray))
    return (cvarray+"\n")


# Actual Script
def main():
    input = []
    display = False  # Option to display results of CSV in console as well as names.csv
    if len(argv) > 1:
        for i in argv[1:]:
            if (i == "/help" or i == "-help" or i == "==help" or i == "-h" or i == "/h"):
                help()
                return
            elif (i == "/d"or i == "-d"or i == "/display"or i == "-display"or i == "--display"):
                display = True
            if (i.split(".")[1].lower() == "html"):
                input.append(i)
        #debug("argv: " + str(input))
        #debug("listdir: " + str(input))
    if(len(input) == 0):
        help()
        return
    output = ''
    if(display):
        print(output)
    appendToFile("names.csv", output)


main()
