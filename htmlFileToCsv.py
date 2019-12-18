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


def collectContours(image):
    # Grab absolute thresh of image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
    horizontalLines = cv2.threshold(
        horizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha

    # combining verticle and horizontal lines. This gives us an empty table so that letters dont become boxes
    blankTable = cv2.addWeighted(
        verticleLines, alpha, horizontalLines, beta, 0.0)
    blankTable = cv2.erode(~blankTable, kernel, iterations=2)
    blankTable = cv2.threshold(blankTable, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[
        1]  # sharpening new table

    # Detecting all contours, which gives me all box positions
    contours = cv2.findContours(
        blankTable, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Organizing contours
    # we got our boxes, but its mostly to sort the contours
    bboxes = [cv2.boundingRect(c) for c in contours]
    # Sort all the contours in ascending order
    contours, bboxes = zip(
        *sorted(zip(contours, bboxes), key=lambda b: b[1][1], reverse=False))
    return contours

# Generator
# PHASE 1: manipulate image to clearly show tabs


def imageScraper(file=""):
    images = []
    sheets = []  # an array with each index containing the output per page
    if not (file.split(".")[1] in ["jpg", "jpeg", "png", "pdf"]):
        return
    elif not (os.path.exists(file)):
        raise FileNotFoundError("File given does not exist.")
    if file.split(".")[1] == "pdf":
        from pdf2image import convert_from_path
        for image in convert_from_path(file):
            image = nm.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            images.append(image)
    else:
        # , cv2.IMREAD_GRAYSCALE)
        images.append(cv2.imread(file, cv2.COLOR_RGB2BGR))

    for image in images:
        contours = collectContours(image)
        # // This is to tell which boxes correlate to the date
        # Phase 1: Finding Main Boxes ##    // and which big box is the signin table
        #################################
        mainBoxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if((h, w, 3) == image.shape):
                continue
            for m in mainBoxes:
                if (x > m[0] and w < m[2]) or (y > m[1] and h < m[3]):
                    break
                elif(x <= m[0] and w >= m[2] and y <= m[1] and h >= m[3]):
                    mainBoxes.remove(m)
                    mainBoxes.append([x, y, w, h])
            else:
                mainBoxes.append([x, y, w, h])

        table = mainBoxes[0]  # img that contains whole table
        for x, y, w, h in mainBoxes:
            if((w - x > table[2] - table[0]) or (h - y > table[3] - table[1])):
                table = [x, y, w, h]
        mainBoxes.remove(table)

        # making images for date and day
        sheets.append([])
        for x, y, w, h in mainBoxes:
            sheets[-1].append(image[y:y+h, x:x+w])

    #########################################
    # Phase 2: Collecting pairs for mapping #
    #########################################

        # Collecting contours collected from table
        table = image[table[1]-5:table[1]+table[3] +
                      5, table[0]-5:table[0]+table[2]+5]
        # removed first 2 as theyre the origional image and the table magnified
        contours = collectContours(table)[2:]

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
            # remove exact duplicate coords
            if(horizontalPairs[i] == horizontalPairs[i+1]):
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
            if(verticlePairs[i] == verticlePairs[i+1]):  # remove exact duplicate coords
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
        # Removing pairs that collide with other pairs
        for i in verticlePairs:
            for j in verticlePairs:
                if(i == j):
                    continue
                # Checks if any point is inside its bounds
                if((i[0] <= j[0] and j[0] <= i[1]) or (i[0] <= j[1] and j[1] <= i[1])):
                    if(i[1] - i[0] > j[1] - j[0]):  # compares and keeps the largest bounds
                        verticlePairs.remove(j)
                    else:
                        verticlePairs.remove(i)
        for i in horizontalPairs:
            for j in horizontalPairs:
                if(i == j):
                    continue
                if((i[0] <= j[0] and j[0] <= i[1]) or (i[0] <= j[1] and j[1] <= i[1])):
                    if(i[1] - i[0] > j[1] - j[0]):
                        horizontalPairs.remove(j)
                    else:
                        horizontalPairs.remove(i)

    #####################################
    # Phase 3: Time for actual Scraping #
    #####################################
    dictionary = []  # the dictionary thatll hold all our information
    dictRow = 0
    for row in horizontalPairs:
        dictionary.append([])
        for col in verticlePairs:
                dictionary[dictRow].append(table[row[0]:row[1], col[0]:col[1]])
        dictRow += 1
    
        sheets[-1].append(dictionary)
    return sheets


def compareKnownAliases(id, col):
    names = {
        1: [
            "nick c",
            "nick cottrell",
            "matthew magyar",
            "jason magyar",
            "jayden gonzalez",
            "zyon hall",
            "julyus gonzalez",
            "emanuel bay",
            "malachi sorden"
        ],
        5: [
            "stem",
            "computer"
        ]
    }
    id = id.lower()
    closestMatch = ""
    mostMatches = 0
    matches = 0
    for alias in names[col]:
        matches = 0        
        for i in range(max(len(id), len(alias))):
            try:
                if(id[i] == alias[i]):
                    matches += 1
            except IndexError:
                break
        if (matches > mostMatches):
            closestMatch = alias
            mostMatches = matches
    return closestMatch, mostMatches


def correctValue(image, column):
    outputs = []
    # Get normal results
    outputs.append(tess.image_to_string(image))

    # Get black and white results
    temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    outputs.append(tess.image_to_string(temp))

    # get thresh results
    temp = cv2.threshold(
        temp, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    outputs.append(tess.image_to_string(temp))

    # Using contrast for more values
    for i in range(50):
        temp = cv2.addWeighted(image, (1 + i/100), image, 0, 0)
        outputs.append(tess.image_to_string(temp))
    outputs.sort()
    for i in range(len(outputs)-1, 1, -1):
        if(outputs[i] == outputs[i-1]):
            outputs.pop(i)
    ##########################
    ## APPLYING CORRECTIONS ##
    ##########################

    if column in [1, 5]:
        #######################################
        ## Corrections for names and purpose ##
        #######################################
        alphaCorrections = {
            "A": ["^"],  # A
            "B": ["8", "|3", "/3", "\\3", "13", "&", "6"],  # B
            "C": ["(", "<", "{", "[", "¢", "©"],  # C G
            "G": ["(", "<", "{", "[", "¢", "©"],
            # "D":["|]", "|)"],
            # "d":["c|", "c/", "c\\"], # D d
            "E": ["3"],  # E
            "g": ["9"],  # g
            # "H":["|-|", "+-+", "++", "4"], # H
            "I": ["1", "/", "\\", "|", "]", "["],  # I l
            "l": ["1", "/", "\\", "|", "]", "["],
            # "K":["|<", "|(", "/<", "/(", "\\<", "\\(", "1<", "1("],  # K
            "O": ["0"],  # O
            "S": ["5", "$"],  # S
            "T": ["7"],  # T
            # "W":["VV"],  # W
            # "X":["><", ")("],  # X
            "Z": ["2"]  # Z
        }

        template = ""
        additions = []
        for word in outputs:
            template = ""
            for char in range(len(word)):
                for i in alphaCorrections:
                    if word[char] in alphaCorrections[i]:
                        template += i[0]
                        break
                else:
                    template += word[char]
            additions.append(template)
        outputs.extend(additions)
        outputs.sort()
        for i in range(len(outputs)-1, 1, -1):
            if(outputs[i] == outputs[i-1]):
                outputs.pop(i)

        largest = len(max(set(outputs), key=len))
        bestGuess = ""
        closestMatch = 0
        accuracy = 0
        score = 0
        count = 0
        guesses = []
        for i in outputs:
            guesses.append(compareKnownAliases(i, column))
        guesses.sort()
        guesses.append(("", 0))  # full stop to make searcher read last item
        # print(guesses)
        check = guesses[0][0]

        for i in guesses:
            if(i[0] != check):
                # print(check, accuracy, score, count)
                if(count > closestMatch):
                    closestMatch = count
                    accuracy = score
                    bestGuess = check
                score = count = 0
                check = i[0]
            score = max(score, i[1])
            count += 1
        # print(accuracy)
        # print(bestGuess)
        if(accuracy >= len(bestGuess)/3 and len(bestGuess) <= largest):
            # print(bestGuess)
            return bestGuess
        else:
            return None
    
        digitCorrections = {
            0: ["o", "O", "Q"],  # 0
        1: ["I", "l", "/", "\\", "|", "[", "]", ")"],  # 1
            2: ["z"],  # 2
            3: ["3"],  # 3
            4: ["h"],  # 4
            5: ["s"],  # 5
            6: ["b"],  # 6
        7: ["t",")","}"],  # 7
            8: ["B", "&"],  # 8
        9: ["g", "q"],  # 9
        ":": ["'"]
        }
    if column in [2, 3]:
        template = ""
        additions = []
        for word in outputs:
            template = ""
            for char in range(len(word)):
                for i in digitCorrections:
                    if word[char] in digitCorrections[i]:
                        template += str(i)
                        break
                else:
                    template += word[char]
            additions.append(template)
        outputs.extend(additions)
        outputs.sort()

        bestGuess = max(set(outputs), key=outputs.count)
        try:
            from time import strptime
            strptime(bestGuess, "%H:%M")
            return bestGuess
        except:
            return None
    return None

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
