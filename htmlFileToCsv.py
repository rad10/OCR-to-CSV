# import this library to automatically download and install the rest of the libraries if they do not exist
import pip

# if opencv isnt installed, it'll install it for you
from sys import argv
import os
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
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# from tkinter import TK

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

def help():
    print(__file__, "[OPTION]", "[HTML File]")
    print("This program is intended to take data from inkspace HTML files and append it to a CSV file in the same directory.")
    print("INSTRUCTIONS: save inkspace output to an HTML file in the same directory as this program. Once done, run this program. Profit.")
    print("OPTIONS:")
    print("-h | --help\t\t\tPrints this help screen.")
    print("-d | --display\t\t\tPrints the output of the CSV into the console as well as into the file.")


# Generator
# PHASE 1: manipulate image to clearly show tabs
def imageScraper(file=""):
    if not (file.split(".")[1] in ["jpg", "jpeg", "png", "pdf"]):
        return
    elif not (os.path.exists(file)):
        raise FileNotFoundError("File given does not exist.")
    if file.split(".")[1] == "pdf":
        from pdf2image import convert_from_path
        image = convert_from_path(file)[0]
        image = nm.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
    image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

    # IMAGE Created

    # Adjusted form to remove filler on top of paper. isolates table for scanning
    image = image[int(len(image) * 0.19):]

    # Grab absolute thresh of image
    thresh = cv2.threshold(
        image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    invert = 255 - thresh

    #######################################
    # Defining kernels for line detection #
    #######################################
    kernel_length = nm.array(image).shape[1]//80
    verticle_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, kernel_length))  # kernel for finding all verticle lines
    # kernel for finding all horizontal lines
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 3x3 kernel

    # Collecting Verticle Lines
    verticleLines = cv2.erode(invert, verticle_kernel, iterations=3)
    verticleLines = cv2.dilate(verticleLines, verticle_kernel, iterations=3)
    verticleLines = cv2.threshold(
        verticleLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Collecting Horizontal Lines
    horizontalLines = cv2.erode(invert, hori_kernel, iterations=3)
    horizontalLines = cv2.dilate(horizontalLines, hori_kernel, iterations=3)
    horizontalLines = cv2.threshold(horizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha

    # combining verticle and horizontal lines. This gives us an empty table so that letters dont become boxes
    blankTable = cv2.addWeighted(verticleLines, alpha, horizontalLines, beta, 0.0)
    blankTable = cv2.erode(~blankTable, kernel, iterations=2)
    blankTable = cv2.threshold(blankTable, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] # sharpening new table

    # Detecting all contours, which gives me all box positions
    contours = cv2.findContours(blankTable, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Organizing contours
    bboxes = [cv2.boundingRect(c) for c in contours] # we got our boxes, but its mostly to sort the contours
    contours, bboxes = zip(*sorted(zip(contours, bboxes), key=lambda b: b[1][1], reverse=False)) # Sort all the contours in ascending order

    contours = contours[2:] # Removed first two contours, which are just the whole page and the whole table

    #########################################
    # Phase 2: Collecting pairs for mapping #
    #########################################
    horizontalPairs = []
    verticlePairs = []

    # Collecting box pairs from contours
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        horizontalPairs.append((y, y+h))
        verticlePairs.append((x, x+w))
    horizontalPairs.sort()
    verticlePairs.sort()

    # Remove all duplicate and similiar points
    i = 0
    while i < len(horizontalPairs) - 1:
        if(horizontalPairs[i] == horizontalPairs[i+1]): # remove exact duplicate coords
            horizontalPairs.pop(i + 1)
        elif (horizontalPairs[i][0] == horizontalPairs[i+1][0] and horizontalPairs[i][1] < horizontalPairs[i+1][1]):
            horizontalPairs.pop(i + 1)
        elif (horizontalPairs[i][0] == horizontalPairs[i+1][0] and horizontalPairs[i][1] > horizontalPairs[i+1][1]):
            horizontalPairs.pop(i)
        elif (horizontalPairs[i][1] == horizontalPairs[i+1][1] and horizontalPairs[i][0] < horizontalPairs[i+1][0]):
            horizontalPairs.pop(i + 1)
        elif (horizontalPairs[i][1] == horizontalPairs[i+1][1] and horizontalPairs[i][0] > horizontalPairs[i+1][0]):
            horizontalPairs.pop(i)
        elif(horizontalPairs[i][0]-5 < horizontalPairs[i+1][0] and horizontalPairs[i][0] + 5 > horizontalPairs[i+1][0]):
            xpair1 = max(horizontalPairs[i][0], horizontalPairs[i+1][0])
            xpair2 = min(horizontalPairs[i][1], horizontalPairs[i+1][1])
            horizontalPairs[i] = (xpair1, xpair2)
            horizontalPairs.pop(i+1)
        else:
            i += 1
    i = 0
    while(i < len(verticlePairs) - 1):
        if(verticlePairs[i] == verticlePairs[i+1]): # remove exact duplicate coords
            verticlePairs.pop(i+1)
        elif (verticlePairs[i][0] == verticlePairs[i+1][0] and verticlePairs[i][1] < verticlePairs[i+1][1]):
            verticlePairs.pop(i + 1)
        elif (verticlePairs[i][0] == verticlePairs[i+1][0] and verticlePairs[i][1] > verticlePairs[i+1][1]):
            verticlePairs.pop(i)
        elif (verticlePairs[i][1] == verticlePairs[i+1][1] and verticlePairs[i][0] < verticlePairs[i+1][0]):
            verticlePairs.pop(i + 1)
        elif (verticlePairs[i][1] == verticlePairs[i+1][1] and verticlePairs[i][0] > verticlePairs[i+1][0]):
            verticlePairs.pop(i)
        elif(verticlePairs[i][0]-5 < verticlePairs[i+1][0] and verticlePairs[i][0] + 5 > verticlePairs[i+1][0]):
            ypair1 = max(verticlePairs[i][0], verticlePairs[i+1][0])
            ypair2 = min(verticlePairs[i][1], verticlePairs[i+1][1])
            verticlePairs[i] = (ypair1, ypair2)
            verticlePairs.pop(i+1)
        else:
            i += 1

    #####################################
    # Phase 3: Time for actual Scraping #
    #####################################
    dictionary = []  # the dictionary thatll hold all our information
    dictRow = 0
    for row in horizontalPairs:
        dictionary.append([])
        for col in verticlePairs:
            dictionary[dictRow].append(image[row[0]:row[1], col[0]:col[1]])
        dictRow += 1
    
    debug_output = "debugOutput/"
    
    return dictionary


# imageScraper("dictTemplate.jpg")


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


# main()
