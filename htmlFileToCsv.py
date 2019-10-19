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


def checkHoriz(img, ind, ratio=0.5, height=1):
    value = True
    for i in range(height):  # i increments by additional heights for thickness of border
        sum = 0
        for space in img[ind + i]:
            if space < 255:
                sum += 1
        # will return false as soon as one thickness is not a border
        value *= (sum > int(len(img)*ratio))
    return value


def checkVert(img, ind, ratio=0.5, width=1):
    value = True
    for i in range(width):
        sum = 0
        for space in img:
            if space[ind + i] < 255:
                sum += 1
        value *= (sum > int(len(img)*ratio))
    return value


def absoluteValue(image):
    for row in range(len(image)):
        for col in range(len(image[0])):
            image[row][col] = 0 if (image[row][col] < 128) else 255
    return image


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

    spreadsheet = []
    absSheet = []  # this will be a copy of spreadsheet, but with all values at abs for line detection
    vertBorders = [-1]  # array thatll have all points of borders
    horizBorders = [-1]
    boldVert = [0, 0]  # start and end
    boldHoriz = [0, 0]  # start and end
    # find borders
    for h in range(len(image)-4):
        if checkHoriz(image, h, 0.5, 4) and boldHoriz[0] > 0:
            boldHoriz[1] = h
        elif checkHoriz(image, h, 0.5, 4):
            boldHoriz[0] = h + 4

    for w in range(len(image[0]) - 4):
        if checkVert(image, w, 0.5, 4) and boldVert[0] > 0:
            boldVert[1] = w
        elif checkVert(image, w, 0.5, 4):
            boldVert[0] = w + 4

    spreadsheet = image[boldHoriz[0]:boldHoriz[1], boldVert[0]:boldVert[1]]
    absSheet = spreadsheet.copy()
    absSheet = absoluteValue(absSheet)  # get an absolute copy of spreadsheet

    # finding borders using the absolute value spreadsheet for accuracy
    for h in range(len(absSheet)):
        if checkHoriz(absSheet, h, 0.8):
            horizBorders.append(h+1)
    for w in range(len(absSheet[0])):
        if checkVert(absSheet, w, 0.75):
            vertBorders.append(w+1)

    ############################
    # Time for actual Scraping #
    ############################
    dictionary = []  # the dictionary thatll hold all our information
    currRow = -1
    hb = horizBorders
    vb = vertBorders
    cv2.imshow("tableIndex", spreadsheet[hb[0]+1:hb[1]-1, vb[0]+1:vb[1]-1])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    for row in range(len(horizBorders) - 1):
        dictionary.append([])
        currRow += 1
        for col in range(len(vertBorders) - 1):
            dictionary[row].append(tess.image_to_string(
                spreadsheet[hb[row] + 1:hb[row + 1] - 1, vb[col] + 1:vb[col+1] - 1]))


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
