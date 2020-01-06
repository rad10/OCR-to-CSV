# import this library to automatically download and install the rest of the libraries if they do not exist
import tkinter
from tkinter import filedialog, ttk
from math import floor
from time import sleep
import re
import json

# if opencv isnt installed, it'll install it for you
from sys import argv
import os
try:
    import numpy as nm
    import cv2
except ImportError:
    if(os.system("pip install opencv-python")):
        os.system("pip install --user opencv-python")
    import numpy as nm
    import cv2
try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    if(os.system("pip install pillow")):
        os.system("pip install --user pillow")
    from PIL import Image, ImageTk
except ImportError:
    import Image, ImageTk

# if tesseract isnt installed, itll install it for you
try:
    import pytesseract as tess
except ImportError:
    if(os.system("pip install pytesseract")):
        os.system("pip install --user pytesseract")
    import pytesseract as tess
# installing pdf to image libraries
try:
    from pdf2image import convert_from_path
except ImportError:
    if(os.system("pip install pdf2image")):
        os.system("pip install --user pdf2image")
    from pdf2image import convert_from_path

### Checking that external software is installed and ready to use
def installError(name, URL, filename):
    def download():
        import webbrowser
        webbrowser.open(URL, autoraise=True)

    def navigate():
        path = filedialog.askopenfilename(
            filetypes=((name, filename), (name, filename)))
        if(os.getenv("path")[-1] != ";"):
            path = ";" + path
        path = path.replace("/", "\\").replace("\\" + filename, "")
        if(len(os.getenv("path") + path) >= 1024):
            info0.configure(
                text="Error: we could not add the file to your path for you. You will have to do this manually.")
        if os.getenv("userprofile") in path:
            if(os.system("setx PATH \"%path%" + path + "\"")):
                print("Failed to do command")
        else:
            if(os.system("setx PATH /M \"%path%" + path + "\"")):
                print("failed to do command")

    ie = tkinter.Tk(baseName="Missing Software")
    ie.title("Missing Software")
    ie.geometry("438x478")
    ie.minsize(120, 1)
    ie.maxsize(1370, 749)
    ie.resizable(1, 1)
    ie.configure(background="#d9d9d9")
    font11 = "-family {Segoe UI} -size 18 -weight bold"
    font13 = "-family {Segoe UI} -size 16 -weight bold"
    Header = tkinter.Label(ie, text="Software Not Installed")
    Header.place(relx=0.16, rely=0.042, height=61, width=294)
    Header.configure(font=font11, activeforeground="#372fd7", background="#d9d9d9",
                     disabledforeground="#a3a3a3", foreground="#2432d9")
    info0 = tkinter.Label(
        ie, text="Warning: Youre missing {name}. it is a required software to make this tool run. To fix this issue, please follow the instructions below.".format(name=name))
    info0.place(relx=0.16, rely=0.167, height=151, width=294)
    info0.configure(font="-family {Segoe UI} -size 14", background="#ffffff",
                    disabledforeground="#a3a3a3", foreground="#000000", wraplength="294")
    info1 = tkinter.Label(
        ie, text="If you havent already installed this software, please follow the download link.")
    info1.place(relx=0.16, rely=0.523, height=31, width=294)
    info1.configure(background="#eeeeee", disabledforeground="#a3a3a3",
                    foreground="#000000", wraplength="294")
    tor = tkinter.Label(ie, text="Or")
    tor.place(relx=0.457, rely=0.69, height=36, width=40)
    tor.configure(font="-family {Segoe UI} -size 16 -weight bold",
                  background="#d9d9d9", disabledforeground="#a3a3a3", foreground="#29c1dc")
    info2 = tkinter.Label(
        ie, text="If you've already installed the software, please lead us to where it is as we cannot find it.")
    info2.place(relx=0.16, rely=0.774, height=41, width=294)
    info2.configure(background="#eeeeee", wraplength="294",
                    disabledforeground="#a3a3a3", foreground="#000000")
    download = tkinter.Button(
        ie, text="Download {name}".format(name=name), command=download)
    download.place(relx=0.16, rely=0.607, height=34, width=297)
    download.configure(font=font11, activebackground="#ececec", activeforeground="#000000", background="#48d250",
                       disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    navigate = tkinter.Button(
        ie, text="Navigate to {name}".format(name=name), command=navigate)
    navigate.place(relx=0.16, rely=0.879, height=34, width=297)
    navigate.configure(font=font13, activebackground="#ececec", activeforeground="#000000", background="#eaecec",
                       disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")

    ie.mainloop()
    os.sys.exit(1)
# check if tesseract exists
if not os.system("tesseract --help"):
    if os.path.exists("C:\\Program Files\\Tesseract-OCR\\tesseract.exe"):
        tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
    else:
        installError("Tesseract", "https://github.com/UB-Mannheim/tesseract/releases", "tesseract.exe")
# check if poppler exists
if not os.system("pdfimages -help"):
    installError("Poppler", "https://poppler.freedesktop.org/", "pdfimages.exe")
del installError


# Functions
Debug = False

if Debug and not os.path.exists("debugOutput/."):
    os.makedirs("debugOutput/dictionary", exist_ok=True)
    os.makedirs("debugOutput/scrapper", exist_ok=True)
elif Debug:
    os.system("del /s debugOutput\\*.jpg")

JSONFile = open("./aliases.json", "r")
JSON = json.load(JSONFile)
JSONFile.close()
JSONChange = False  # this is only used when the database is updated


def debug(content):
    if Debug:
        print(content)


def debugImageDictionary(diction):
    if Debug:
        debugOutput = "Sheet | SheetLen | TableRow | TableCol\n"
        for sheet in range(len(diction)):
            debugOutput += "{ind: 5d} | {slen: 8d} | {trow: 8d} | {tcol: 8d}\n".format(ind=sheet, slen=len(
                diction[sheet]), trow=len(diction[sheet][-1]), tcol=len(diction[sheet][-1][0]))
        print(debugOutput)
        exportToFile("debugOutput/dictionaryStats.txt", debugOutput)
        for sheet in range(len(diction)):
            for dates in range(len(diction[sheet][:-1])):
                cv2.imwrite("debugOutput/dictionary/sheet{sheet}date{date}.jpg".format(
                    sheet=sheet, date=dates), diction[sheet][dates])
            for row in range(len(diction[sheet][-1])):
                for col in range(len(diction[sheet][-1][row])):
                    cv2.imwrite("debugOutput/dictionary/sheet{sheet}table{row}{col}.jpg".format(
                        sheet=sheet, row=row, col=col), diction[sheet][-1][row][col])


def exportToFile(dir, content):
    open(dir, "w").write(content)


def appendToFile(dir, content):
    try:
        inside = open(dir, "r").read()
        open(dir, "w").write(inside + content)
    except:
        open(dir, "w").write(content)


def collectContours(image):
    """ Sub function used by scrapper.\n
    @param image: an opencv image\n
    @return returns an ordered list of contours found in the image.\n
    This function was heavily influenced by its source.\n
    @source: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
    """
    debugIndex = 0
    # Grab absolute thresh of image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(
        image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    invert = 255 - thresh

    if Debug:
        while(os.path.exists("debugOutput/scrapper/{ind}1invert.jpg".format(ind=debugIndex))):
            debugIndex += 1
        cv2.imwrite(
            "debugOutput/scrapper/{ind}1invert.jpg".format(ind=debugIndex), invert)
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

    if Debug:
        cv2.imwrite(
            "debugOutput/scrapper/{ind}2verticleLines.jpg".format(ind=debugIndex), verticleLines)

    # Collecting Horizontal Lines
    horizontalLines = cv2.erode(invert, hori_kernel, iterations=3)
    horizontalLines = cv2.dilate(horizontalLines, hori_kernel, iterations=3)
    horizontalLines = cv2.threshold(
        horizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    if Debug:
        cv2.imwrite(
            "debugOutput/scrapper/{ind}3horizontalLines.jpg".format(ind=debugIndex), horizontalLines)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha

    # combining verticle and horizontal lines. This gives us an empty table so that letters dont become boxes
    blankTable = cv2.addWeighted(
        verticleLines, alpha, horizontalLines, beta, 0.0)
    blankTable = cv2.erode(~blankTable, kernel, iterations=2)
    blankTable = cv2.threshold(blankTable, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[
        1]  # sharpening new table

    if Debug:
        cv2.imwrite(
            "debugOutput/scrapper/{ind}4blankTable.jpg".format(ind=debugIndex), blankTable)
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


def imageScraper(file, outputArray=None):
    """This function if phase 1 of the process. It starts by taking the image/pdf
    of the signin sheet and breaks the table apart to isolate each value in the exact
    order that they came in.\n
    @param file: the image/pdf that needs to be scraped into its values.\n
    @param outputArray: a parameter passed by reference due to the nature
    of tkinters buttons. If the param is not filled, it will just return the result.\n
    @return a multidimension array of images that containes the values of all the slots in the table.
    """
    images = []
    sheets = []  # an array with each index containing the output per page
    debugIndex = 0
    if not (file.split(".")[1] in ["jpg", "jpeg", "png", "pdf"]):
        return
    elif not (os.path.exists(file)):
        raise FileNotFoundError("File given does not exist.")
    if file.split(".")[1] == "pdf":
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

        if Debug:
            cv2.imwrite(
                "debugOutput/scrapper/mainTable{image}.jpg".format(image=debugIndex), table)
            debugIndex += 1

        # Grabbing verticle and horizontal images of table for better scraping
        tableCompute = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
        tableCompute = cv2.threshold(
            tableCompute, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        tableInvert = 255 - tableCompute
        tKernelLength = nm.array(tableCompute).shape[1]//80
        tKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        #############################
        # Collecting Verticle Pairs #
        #############################
        verticlePairs = []
        # Creating verticle kernel lines
        tKernelVerticle = cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, tKernelLength))
        tVerticleLines = cv2.erode(tableInvert, tKernelVerticle, iterations=3)
        tVerticleLines = cv2.dilate(
            tVerticleLines, tKernelVerticle, iterations=3)
        tVerticleLines = cv2.threshold(
            tVerticleLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if Debug:
            cv2.imwrite(
                "debugOutput/scrapper/table{}VertLines.jpg".format(debugIndex), tVerticleLines)
        # Added this line because it needs a white background rather than black background
        tVerticleLines = 255 - tVerticleLines
        # Adding edge lines for contour collection
        cv2.line(tVerticleLines, (0, floor(tVerticleLines.shape[0] * 0.01)), (
            tVerticleLines.shape[1], floor(tVerticleLines.shape[0] * 0.01)), (0, 0, 0), 5)
        cv2.line(tVerticleLines, (0, floor(tVerticleLines.shape[0] * 0.99)), (
            tVerticleLines.shape[1], floor(tVerticleLines.shape[0] * 0.99)), (0, 0, 0), 5)
        # Collecting verticle contours
        contours = cv2.findContours(
            tVerticleLines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        # Figuring out the length that relates to the majority of the table, (aka, longer lengths relates to length of table rather than random lines)
        maxLength = 0
        tableHeightPair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # if the height of the contour is at least 90% as long as the whole table, its safe to assume that that belongs to the whole table
            if(h >= table.shape[0] * 0.9):
                tableHeightPair = (y, h)
                break
            elif(h > maxLength):  # if the height isnt a significant size, then the best choice is the longest length
                maxlength = h
                tableHeightPair = (y, h)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if((y, h) == tableHeightPair):
                verticlePairs.append((x, x + w))
        verticlePairs.sort()

        if Debug:
            print("Debug VerticlePairs:", verticlePairs)

        # Fixing overlapping of some pairs
        for v in range(len(verticlePairs) - 1):
            # if the tail end of a pair overlaps the beginning of the next pair, then swap positions. itll make it slightly smaller, but it will miss table walls
            if(verticlePairs[v][1] > verticlePairs[v + 1][0]):
                temp = verticlePairs[v][1]
                verticlePairs[v] = (verticlePairs[v][0],
                                    verticlePairs[v + 1][0])
                verticlePairs[v + 1] = (temp, verticlePairs[v + 1][1])

        # this is the gap before the table from the left side
        verticlePairs.pop(0)
        # this is the gap after the table from the right side
        verticlePairs.pop(-1)

        if Debug:
            print("Debug VerticlePairs:", verticlePairs)
            debugimg = cv2.cvtColor(tVerticleLines, cv2.COLOR_GRAY2BGR)
            for v in verticlePairs:
                cv2.line(debugimg, (v[0], 0),
                         (v[0], debugimg.shape[0]), (0, 0, 255))
                cv2.line(debugimg, (v[1], 0),
                         (v[1], debugimg.shape[0]), (0, 0, 255))
            cv2.imwrite(
                "debugOutput/scrapper/table{}VertContours.jpg".format(debugIndex), debugimg)

        ###############################
        # Collecting Horizontal Pairs #
        ###############################
        horizontalPairs = []
        # Creating horizontal kernel lines
        tKernelHorizontal = cv2.getStructuringElement(
            cv2.MORPH_RECT, (tKernelLength, 1))
        tHorizontalLines = cv2.erode(
            tableInvert, tKernelHorizontal, iterations=3)
        tHorizontalLines = cv2.dilate(
            tHorizontalLines, tKernelHorizontal, iterations=3)
        tHorizontalLines = cv2.threshold(
            tHorizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if Debug:
            cv2.imwrite(
                "debugOutput/scrapper/table{}HorLines.jpg".format(debugIndex), tHorizontalLines)
        # Added this line because it needs a white background rather than black background
        tHorizontalLines = 255 - tHorizontalLines
        # Adding edge lines for contour collection
        cv2.line(tHorizontalLines, (floor(tHorizontalLines.shape[1] * 0.01), 0), (floor(
            tHorizontalLines.shape[1] * 0.01), tHorizontalLines.shape[0]), (0, 0, 0), 5)
        cv2.line(tHorizontalLines, (floor(tHorizontalLines.shape[1] * 0.99), 0), (floor(
            tHorizontalLines.shape[1] * 0.99), tHorizontalLines.shape[0]), (0, 0, 0), 5)
        # Collecting Horizontal contours
        contours = cv2.findContours(
            tHorizontalLines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Figuring out the length that relates to the majority of the table, (aka, longer lengths relates to length of table rather than random lines)
        maxLength = 0
        tableWidthPair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # if the width of the contour is at least 90% as long as the whole table, its safe to assume that that belongs to the whole table
            if(w >= tHorizontalLines.shape[1] * 0.9):
                tableWidthPair = (x, w)
                break
            elif(w > maxLength):  # if the width isnt a significant size, then the best choice is the longest length
                maxLength = w
                tableWidthPair = (x, w)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if((x, w) == tableWidthPair):
                horizontalPairs.append((y, y + h))
        horizontalPairs.sort()

        if Debug:
            print("Debug HorizontalPairs:", horizontalPairs)

        # Fixing overlapping of some pairs
        for h in range(len(horizontalPairs) - 1):
            # if the tail end of a pair overlaps the beginning of the next pair, then swap positions. itll make it slightly smaller, but it will miss table walls
            if(horizontalPairs[h][1] > horizontalPairs[h + 1][0]):
                temp = horizontalPairs[h][1]
                horizontalPairs[h] = (
                    horizontalPairs[h][0], horizontalPairs[h + 1][0])
                horizontalPairs[h + 1] = (temp, horizontalPairs[h + 1][1])

        # this is the gap before the table from the left side
        horizontalPairs.pop(0)
        # this is the gap after the table from the right side
        horizontalPairs.pop(-1)

        if Debug:
            print("Debug HorizontalPairs:", horizontalPairs)
            debugimg = cv2.cvtColor(tHorizontalLines, cv2.COLOR_GRAY2BGR)
            for h in horizontalPairs:
                cv2.line(debugimg, (0, h[0]),
                         (debugimg.shape[1], h[0]), (0, 0, 255))
                cv2.line(debugimg, (0, h[1]),
                         (debugimg.shape[1], h[1]), (0, 0, 255))
            cv2.imwrite(
                "debugOutput/scrapper/table{}HorContours.jpg".format(debugIndex), debugimg)

        #####################################
        # Phase 3: Time for actual Scraping #
        #####################################
        sheets[-1].append([])
        # the dictionary thatll hold all our information
        dictionary = sheets[-1][-1]
        dictRow = 0
        for row in horizontalPairs:
            dictionary.append([])
            for col in verticlePairs:
                dictionary[dictRow].append(table[row[0]:row[1], col[0]:col[1]])
                if Debug:
                    cv2.imwrite("debugOutput/dictionary/raw/table{}{}.jpg".format(dictRow,
                                                                                  col[1]-col[0]), table[row[0]:row[1], col[0]:col[1]])
            dictRow += 1

    if(outputArray == None):
        return sheets
    else:
        globals()[outputArray] = sheets.copy()
        return


def compareKnownAliases(id, col=1):
    """Uses a dictionary of known valid aliases to find the most accurate guess for a name.\n
    @param id: The string that you want a guess as what name it closest resembles.\n
    @param col: the column of the string thats being checked. This is important as it clarifies 
    whether its a name being searched or a purpose.\n
    @return: it returns the name it believes closest resembles the string given and it will return 
    the number of characters the string has in common with it. If the string matches with nothing, 
    it will return ("", 0) but this is rare.
    """
    id = id.lower()
    closestMatch = ""
    mostMatches = 0
    matches = 0
    for alias in JSON["names"][str(col)]:
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


def correctValue(image, column, threshold=0.3):
    """This function is how we get accurate values from the images in each dictionary.\n
    @param {cvimg} image: The image that is being transcribed.\n
    @param {int} column: The column in the table that the image is in. This is very important as its part of how the translator corrects the outputs.\n
    @param {double} threshold: Optional variable. Changes the percentage of characters that need to match the origional of it to return. Higher threshholds mean more strict requirements and higher chance of getting nothing. Lower threshholds mean higher chance to get a value that may or may not be incorrect.\n
    @returns: It will return the name that closest resembles the image, or it will return \"RequestCorrection:\" if no name could be accepted.\n
    It works by taking an image and running tesseract to get the value from the unchanges color image, then it grabs the ocr output from the same image with different effects, such as greyscale, thresholds, and contrast increase.\n
    The next step for it is to take each unique value make, then run it through another function that creates a new string with the characters in it resembling what should be in there (no numbers or symbols in names, no chars in numbers, etc.) and adds it to the pile of strings.\n
    The last step is for it take all the new unique strings and run them through another function to see which names the strings closest resemble. The name with the most conclusions is considered the best guess.\n
    However, the best guess may not be accepted if the name doesnt share enough characters in common with all the guesses, then its scrapped and nothing is returned.
    """
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

    if(outputs.count("") >= 2):  # quick check incase box is looking empty; will only skip if 2/3 or more are blank
        if Debug:
            print("Looks empty")
        # inverts the threshed image, removes 8px border in case it includes external lines or table borders
        invert = 255 - temp[8:-8, 8:-8]
        # countnonzero only counts white pixels, so i need to invert to turn black pixels white
        pixelCount = cv2.countNonZero(invert)
        pixelTotal = temp.shape[0] * temp.shape[1]

        if Debug:
            print("debug blankPercent:", pixelCount/pixelTotal)
        # will only consider empty if image used less than 1% of pixels. yes, that small
        if(pixelCount/pixelTotal <= 0.01 or column == 5):
            if Debug:
                print("It's Blank")
            return ""  # Skipping ahead if its already looking like theres nothing
        else:
            if Debug:
                print("we couldnt read it")
            # if theres enough pixels to describe a possbile image, then it isnt empty, but it cant read it
            return "RequestCorrection:NaN"

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
            "E": ["3", "€"],  # E
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
        for i in range(len(outputs)-1, 0, -1):  # Remove duplicate entries
            if(outputs[i] == outputs[i-1]):
                outputs.pop(i)

        # Removing blank entries. it wasnt considered blank, so it shouldnt be there
        for i in range(len(outputs) - 1, -1, -1):
            if(outputs[i] == ""):
                outputs.pop(i)

        if Debug:
            print("Debug Words[outputs]:", outputs)
        largest = len(max(set(outputs), key=len))
        bestGuess = ""  # variable that determines result
        closestMatch = 0  # the number of times best guess occurs in our guesses
        accuracy = 0  # the max number of characters that matches with the best guess
        score = 0  # temp var for accuracy
        count = 0  # temp variable for closestMatch
        guesses = []
        for i in outputs:
            guesses.append(compareKnownAliases(i, column))
        guesses.sort()
        guesses.append(("", 0))  # full stop to make searcher read last item
        if Debug:
            print("Debug Words[Guesses]:", guesses)
        check = guesses[0][0]

        for i in guesses:
            if(i[0] != check):
                # print(check, accuracy, score, count)
                # if the name occurs more often than previous string or the number of accurate characters is more than the length of previous string
                if((count > closestMatch and accuracy <= len(check)) or score > len(bestGuess)):
                    closestMatch = count
                    accuracy = score
                    bestGuess = check
                score = count = 0
                check = i[0]
            score = max(score, i[1])
            count += 1

        if Debug:
            print("Debug Words[accuracy]:", accuracy)
            print("Debug Words[bestGuess]:", bestGuess)
        if (bestGuess == ""):
            # if we did our job correctly, the name/purpose should never be blank
            return "RequestCorrection:NaN"
        elif(accuracy >= len(bestGuess)*threshold and (len(bestGuess) <= largest or threshold == 0)):
            return bestGuess
        else:
            return "RequestCorrection:" + bestGuess

    elif column in [2, 3, 4]:
        ####################################
        ## Corrections to Dates and Hours ##
        ####################################
        digitCorrections = {
            0: ["o", "O", "Q", "C", "c"],  # 0
            1: ["I", "l", "/", "\\", "|", "[", "]", "(", ")"],  # 1
            2: ["z", "Z"],  # 2
            3: ["3", "E"],  # 3
            4: ["h", "y", "A"],  # 4
            5: ["s", "S"],  # 5
            6: ["b", "e"],  # 6
            7: ["t", ")", "}"],  # 7
            8: ["B", "&"],  # 8
            9: ["g", "q"],  # 9
            ":": ["'", ".", ","]
        }
        if column in [2, 3]:
            # Source for regex string http://regexlib.com/DisplayPatterns.aspx?cattabindex=4&categoryId=5&AspxAutoDetectCookieSupport=1
            timeFilter = re.compile(
                r'^((([0]?[1-9]|1[0-2])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$')

        template = ""
        additions = []
        for word in outputs:
            if column in [2, 3] and bool(timeFilter.match(word)):
                continue
            if column in [2, 3] and word.isdigit():
                if(len(word) >= 3 and len(word) <= 6):
                    template = word
                    for i in range(len(template) - 2, 0, -2):
                        template = template[:i] + ":" + template[i:]
                    additions.append(template)
                    continue
            template = ""
            for char in range(len(word)):
                for i in digitCorrections:
                    if word[char] in digitCorrections[i]:
                        template += str(i)
                        break
                else:
                    template += word[char]
            if column in [2, 3] and template.isdigit():
                if(len(word) >= 3 and len(word) <= 6):
                    for i in range(len(template) - 2, 0, -2):
                        template = template[:i] + ":" + template[i:]
            additions.append(template)
        outputs.extend(additions)
        outputs.sort()

        correctFormat = []  # the array that will only take in outputs that fit formatting
        for word in outputs:
            if column in [2, 3] and bool(timeFilter.match(word)):
                correctFormat.append(word)
            elif column == 4 and (word.isdigit() or word.isdecimal()):
                correctFormat.append(word)

        if (len(correctFormat) == 0):
            bestGuess = max(set(outputs), key=outputs.count)
        else:
            bestGuess = max(set(correctFormat), key=correctFormat.count)
        if (threshold == 0):
            return bestGuess
        if column in [2, 3]:
            if Debug:
                print("debug time[outputs]:", outputs)
                print("debug time[bestguess]:", bestGuess)
                print("debug time[correctFormat]:", correctFormat)
            if(bool(timeFilter.match(bestGuess))):
                return bestGuess
            else:
                return "RequestCorrection:" + str(bestGuess)
        elif(column == 4):
            if Debug:
                print("debug hours[outputs]:", outputs)
                print("debug hours[bestguess]:", bestGuess)
            if(bestGuess.isdigit() or bestGuess.isdecimal()):
                # will only return the hours if theyre a valid number
                return bestGuess
            else:
                return ""  # This is the one exception to the errors The reason why is because we can calculate the hours if we have two valid times
    return "RequestCorrection:"


def requestCorrection(displayImage, col, guess=""):
    """This is the function used when a string doesnt confidently match a name.\n
    @param displayImage: The image placed on the display for user to see.\n
    @param {int} col: The column number that the image was found in. This is needed for placing the AI's guess.\n
    @param {string} guess: This is to straight up overwrite the AI's guess with the string. This can be helpful so that the AI doesnt have to process the image again.\n
    @return: the users answer.
    """
    global labelImage
    global errorLabel
    global confidenceDescription
    global AIGuess
    global guessButton
    global orLabel
    global correctionEntry
    global submitButton

    result = ""  # the string to be returned for final answer

    # Setting up image to place in GUI
    image = Image.fromarray(displayImage)
    if(displayImage.shape[1] > labelImage.winfo_width()):
        hgt, wth = displayImage.shape[:2]
        ratio = labelImage.winfo_width()/wth
        image = image.resize(
            (floor(wth * ratio), floor(hgt * ratio)), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)

    # setting values to labels in gui
    labelImage.configure(image=image)
    labelImage.image = image
    errorLabel.configure(
        text="Uh oh. It looks like we couldnt condifently decide who or what this is. We need you to either confirm our guess or type in the correct value")
    confidenceDescription.configure(text="Were not confident, but is it:")
    AIGuess.configure(text=guess)
    orLabel.configure(text="or")

    # basically waits till user presses a button and changes variable scope
    root.update_idletasks()
    root.wait_variable(decision)
    result = correctionEntry.get()

    # Resetting changes made
    labelImage.configure(image=None)
    labelImage.image = None
    errorLabel.configure(text="")
    confidenceDescription.configure(text="")
    AIGuess.configure(text="")
    orLabel.configure(text="")
    correctionEntry.delete(0, "end")
    root.update_idletasks()
    sleep(1)
    decision.set(0)

    if(guessButton):
        guessButton = False
        submitButton = False
        return guess
    elif(submitButton):
        guessButton = False
        submitButton = False
        return result


def TranslateDictionary(sheetsDict, gui=False, outputDict=None):
    """ Phase two of plan. This function goes through the image dictionary passed 
    to it and creates a matrix of the dictionary in text.\n
    @param sheetsDict: a matrix of images made from a table.\n
    @param gui: whether to switch on global gui manipulation for the progress bar.\n
    @param outputDict: a variable passed by reference instead of using return.\n
    @return a matrix of strings that represents the text in the image dictionary.
    """
    global JSON
    global JSONChange
    results = []
    # GUI widgets to manipulate while in middle of function
    if(gui):
        global sheetStatus
        global rowStatus
        global progressBar
        sheetMax = len(sheetsDict)
        sheetInd = 0
        rowInd = 0
        progressMax = 1

        # Getting max for progress bar
        for sheet in sheetsDict:
            progressMax += len(sheet[-1]) - 1
        progressBar.configure(mode="determinate", maximum=progressMax)
    for sheet in sheetsDict:
        results.append([])
        if gui:
            sheetInd += 1
            rowMax = len(sheet[-1]) - 1
            sheetStatus.configure(
                text="Sheet: " + str(sheetInd) + " of " + str(sheetMax))

        # Collecting dates on page first
        dates = []
        for date in sheet[:-1]:
            dates.append(tess.image_to_string(date))
        # | Full name | Time in | Time out | hours (possibly blank) | purpose | date | day (possibly blank) |
        for row in sheet[-1][1:]:  # skips first row which is dummy
            if gui:
                rowInd += 1
                progressBar.step()
                rowStatus.configure(
                    text="Row: " + str(rowInd) + " of " + str(rowMax))
                root.update_idletasks()
            results[-1].append([])
            for col in range(1, len(row)):  # skip first col which is dummy
                temp = correctValue(row[col], col)
                if(temp == None):  # the correction failed. the user must return the correction
                    temp = "RequestCorrection"
                results[-1][-1].append(temp)
            results[-1][-1].extend(dates)

        if Debug:
            print("Debug Results:", results)
        # Iterating through results to see where errors occured
        for row in range(len(results[-1])):
            for col in range(len(results[-1][row][:-len(dates)])):
                if (results[-1][row][col][0:18] == "RequestCorrection:"):
                    results[-1][row][col] = requestCorrection(
                        sheet[-1][row + 1][col + 1], col + 1, results[-1][row][col][18:])
                    if (col + 1 in [1, 5]):
                        for entry in JSON["names"][str(col + 1)]:
                            if (results[-1][row][col].lower() == entry):
                                break
                        else:
                            JSONChange = True
                            # if the name possibly entered in by the user doesnt exist in the database, add it
                            JSON["names"][str(
                                col + 1)].append(results[-1][row][col].lower())
    if(outputDict == None):
        return results
    else:
        globals()[outputDict] = results.copy()
        return


def arrayToCsv(directory):
    """takes a matrix and returns a string in CSV format.
    var directory: a string[][] matrix that contains the information of people at the center.
    returns: a string that contains all the information in CSV format.
    """
    cvarray = ''
    for i in range(len(directory)):
        for e in range(len(directory[i])-1):
            cvarray += (directory[i][e]+",")
        cvarray += (directory[i][-1]+"\n")
        debug(("cvarray["+str(i)+"]:", cvarray))
    return (cvarray+"\n")


# Gui Variables
signinsheet = ""
outputCSV = os.getenv("userprofile").replace(
    "\\", "/") + "/Documents/signinSheetOutput.csv"
guessButton = False
submitButton = False
# Gui Functions


def reconfigOutput():
    global outputCSV
    global outputFile
    outputCSV = filedialog.askopenfilename(filetypes=(
        ("Comma Style Values", "*.csv"), ("Comma Style Values", "*.csv")))
    if(outputCSV != ""):
        outputFile.configure(text=outputCSV.split("/")[-1])


def guessSwitch():
    global guessButton
    guessButton = True
    decision.set(1)


def submitSwitch(event=None):
    global submitButton
    if(event != None and correctionEntry.get() == ""):
        return
    submitButton = True
    decision.set(1)


def popupTag(title, text, color="#000000"):
    # Popup box for errors and completion
    def end():
        popupBox.destroy()
        root.destroy()
    popupBox = tkinter.Toplevel()
    popupBox.geometry("335x181+475+267")
    popupBox.minsize(120, 1)
    popupBox.maxsize(1370, 749)
    popupBox.resizable(1, 1)
    popupBox.configure(background="#d9d9d9")
    popupBox.title = title

    popupDescription = tkinter.Text(popupBox)
    popupDescription.insert("end", text)
    popupDescription.configure(foreground=color, wrap="word", state="disabled", background="#FFFFFF", font="TkTextFont", highlightbackground="#d9d9d9", highlightcolor="black", insertbackground="black",
                               selectbackground="#c4c4c4", selectforeground="black")
    popupDescription.place(relx=0.03, rely=0.055, height=91, width=314)
    popupOK = tkinter.Button(popupBox, text="OK", command=end)
    popupOK.configure(activebackground="#ececec", activeforeground="#000000", background="#ebebeb",
                      disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    popupOK.place(relx=0.328, rely=0.663, height=34, width=117)
    popupBox.mainloop()


def main():
    ##########################################
    ## Phase 3: Hooking everything together ##
    ##########################################
    global signinsheet
    global inputFile
    global errorLabel

    try:
        signinsheet = filedialog.askopenfilename(filetypes=(
            ("PDF Files", "*.pdf"), ("Jpeg Files", "*.jpg"), ("Png Files", "*.png")))
        inputFile.configure(text=signinsheet.split("/")[-1])
        imageDictionary = imageScraper(signinsheet)
        debugImageDictionary(imageDictionary)
        textDictionary = TranslateDictionary(imageDictionary, gui=True)
        csvString = ""
        for sheet in textDictionary:
            csvString += arrayToCsv(sheet)
        exportToFile(outputCSV, csvString)
        errorLabel.configure(text="All finished.")
    except BaseException:
        import traceback
        popupTag("Error", "Looks like something went wrong.\n" +
                 str(os.sys.exc_info())+"\n"+str(traceback.format_exc()), "#ff0000")
        raise
    popupTag(
        "Done", "Congrats! its all finished.\nLook at your csv and see if it looks alright.")
    if (JSONChange):
        JSON["names"]["1"].sort()  # Sorting new libraries for optimization
        JSON["names"]["5"].sort()
        JSONFile = open("aliases.json", "w")
        json.dump(JSON, JSONFile, indent=4, separators=(
            ",", ": "), ensure_ascii=True, sort_keys=True)
        JSONFile.close()
    return


if __name__ == "__main__":
    root = tkinter.Tk(screenName="OCR To CSV Interpreter")
    root.title("OCR To CSV Interpreter")
    root.geometry("600x450+401+150")
    root.configure(background="#d9d9d9")
    root.minsize(120, 1)
    root.maxsize(1370, 749)
    root.resizable(1, 1)

    decision = tkinter.BooleanVar()

    inputFile = tkinter.Button(root, text="Select Signin Sheet", command=main)
    inputFile.configure(activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
                        disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    inputFile.place(relx=0.033, rely=0.044, height=34, width=157)

    outputFile = tkinter.Button(
        root, text=outputCSV.split("/")[-1], command=reconfigOutput)
    outputFile.configure(activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
                         disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    outputFile.place(relx=0.033, rely=0.156, height=34, width=157)

    labelImage = tkinter.Label(root, text="No corrections required yet.")
    labelImage.configure(background="#e6e6e6",
                         disabledforeground="#a3a3a3", foreground="#000000")
    labelImage.place(relx=0.417, rely=0.022, height=221, width=314)

    errorLabel = tkinter.Label(root)
    errorLabel.configure(wraplength=224, activebackground="#f9f9f9", activeforeground="black", background="#e1e1e1",
                         disabledforeground="#a3a3a3", foreground="#ff0000", highlightbackground="#d9d9d9", highlightcolor="black")
    errorLabel.place(relx=0.017, rely=0.267, height=111, width=224)

    confidenceDescription = tkinter.Label(root)
    confidenceDescription.configure(activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
                                    disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black")
    confidenceDescription.place(relx=0.267, rely=0.556, height=31, width=164)

    AIGuess = tkinter.Button(root, text="No guesses yet.", command=guessSwitch)
    AIGuess.configure(activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
                      disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    AIGuess.place(relx=0.55, rely=0.556, height=34, width=227)

    orLabel = tkinter.Label(root)
    orLabel.configure(activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
                      disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black")
    orLabel.place(relx=0.017, rely=0.689, height=31, width=64)

    correctionEntry = tkinter.Entry(root)
    correctionEntry.configure(background="white", disabledforeground="#a3a3a3", font="TkFixedFont", foreground="#000000",
                              highlightbackground="#d9d9d9", highlightcolor="black", insertbackground="black", selectbackground="#c4c4c4", selectforeground="black")
    correctionEntry.place(relx=0.133, rely=0.689, height=30, relwidth=0.557)

    submit = tkinter.Button(root, text="Submit", command=submitSwitch)
    submit.configure(activebackground="#ececec", activeforeground="#000000", background="#d9d9d9",
                     disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    submit.place(relx=0.717, rely=0.689, height=34, width=127)
    root.bind("<Return>", submitSwitch)

    # Status bars
    sheetStatus = tkinter.Label(root, text="Sheet: 0 of 0")
    sheetStatus.configure(activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
                          disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black")
    sheetStatus.place(relx=0.017, rely=0.844, height=21, width=94)

    rowStatus = tkinter.Label(root, text="Row: 0 of 0")
    rowStatus.configure(activebackground="#f9f9f9", activeforeground="black", background="#d9d9d9",
                        disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black")
    rowStatus.place(relx=0.217, rely=0.844, height=21, width=64)

    progressBar = ttk.Progressbar(root)
    progressBar.place(relx=0.017, rely=0.911, relwidth=0.95,
                      relheight=0.0, height=22)

    # Run main program
    root.mainloop()
