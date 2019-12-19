# import this library to automatically download and install the rest of the libraries if they do not exist
import tkinter
from tkinter import filedialog, ttk
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
    from PIL import Image, ImageTk
except ImportError:
    import Image
    import ImageTk

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


# Functions
Debug = False


def debug(content):
    if Debug:
        print(content)


def exportToFile(dir, content):
    open(dir, "w").write(content)


def appendToFile(dir, content):
    try:
        inside = open(dir, "r").read()
        open(dir, "w").write(inside + content)
    except:
        open(dir, "w").write(content)

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
    n = 0
    while n < len(horizontalPairs) - 1:
        # remove exact duplicate coords
        if(horizontalPairs[n] == horizontalPairs[n+1]):
            horizontalPairs.pop(n + 1)
        elif (horizontalPairs[n][0] == horizontalPairs[n+1][0] and horizontalPairs[n][1] < horizontalPairs[n+1][1]):
            horizontalPairs.pop(n + 1)
        elif (horizontalPairs[n][0] == horizontalPairs[n+1][0] and horizontalPairs[n][1] > horizontalPairs[n+1][1]):
            horizontalPairs.pop(n)
        elif (horizontalPairs[n][1] == horizontalPairs[n+1][1] and horizontalPairs[n][0] < horizontalPairs[n+1][0]):
            horizontalPairs.pop(n + 1)
        elif (horizontalPairs[n][1] == horizontalPairs[n+1][1] and horizontalPairs[n][0] > horizontalPairs[n+1][0]):
            horizontalPairs.pop(n)
        elif(horizontalPairs[n][0]-5 < horizontalPairs[n+1][0] and horizontalPairs[n][0] + 5 > horizontalPairs[n+1][0]):
            xpair1 = max(horizontalPairs[n][0], horizontalPairs[n+1][0])
            xpair2 = min(horizontalPairs[n][1], horizontalPairs[n+1][1])
            horizontalPairs[n] = (xpair1, xpair2)
            horizontalPairs.pop(n+1)
        else:
            n += 1
    n = 0
    while(n < len(verticlePairs) - 1):
        if(verticlePairs[n] == verticlePairs[n+1]):  # remove exact duplicate coords
            verticlePairs.pop(n+1)
        elif (verticlePairs[n][0] == verticlePairs[n+1][0] and verticlePairs[n][1] < verticlePairs[n+1][1]):
            verticlePairs.pop(n + 1)
        elif (verticlePairs[n][0] == verticlePairs[n+1][0] and verticlePairs[n][1] > verticlePairs[n+1][1]):
            verticlePairs.pop(n)
        elif (verticlePairs[n][1] == verticlePairs[n+1][1] and verticlePairs[n][0] < verticlePairs[n+1][0]):
            verticlePairs.pop(n + 1)
        elif (verticlePairs[n][1] == verticlePairs[n+1][1] and verticlePairs[n][0] > verticlePairs[n+1][0]):
            verticlePairs.pop(n)
        elif(verticlePairs[n][0]-5 < verticlePairs[n+1][0] and verticlePairs[n][0] + 5 > verticlePairs[n+1][0]):
            ypair1 = max(verticlePairs[n][0], verticlePairs[n+1][0])
            ypair2 = min(verticlePairs[n][1], verticlePairs[n+1][1])
            verticlePairs[n] = (ypair1, ypair2)
            verticlePairs.pop(n+1)
        else:
            n += 1
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
                        break  # needed in case i is removed to move to next iteration of i
        for i in horizontalPairs:
            for j in horizontalPairs:
                if(i == j):
                    continue
                if((i[0] <= j[0] and j[0] <= i[1]) or (i[0] <= j[1] and j[1] <= i[1])):
                    if(i[1] - i[0] > j[1] - j[0]):
                        horizontalPairs.remove(j)
                    else:
                        horizontalPairs.remove(i)
                        break  # needed in case i is removed to move to next iteration of i

    #####################################
    # Phase 3: Time for actual Scraping #
    #####################################
    sheets[-1].append([])
    dictionary = sheets[-1][-1]  # the dictionary thatll hold all our information
    dictRow = 0
    for row in horizontalPairs:
        dictionary.append([])
        for col in verticlePairs:
                dictionary[dictRow].append(table[row[0]:row[1], col[0]:col[1]])
        dictRow += 1
    
        sheets[-1].append(dictionary)
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


def correctValue(image, column, threshold=0.3):
    """This function is how we get accurate values from the images in each dictionary.\n
    @param {cvimg} image: The image that is being transcribed.\n
    @param {int} column: The column in the table that the image is in. This is very important as its part of how the translator corrects the outputs.\n
    @param {double} threshold: Optional variable. Changes the percentage of characters that need to match the origional of it to return. Higher threshholds mean more strict requirements and higher chance of getting nothing. Lower threshholds mean higher chance to get a value that may or may not be incorrect.\n
    @returns: It will return the name that closest resembles the image, or it will return None if no name could be accepted.\n
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

    if(max(set(outputs), key=outputs.count) == ""):
        return "" # Skipping ahead if its already looking like theres nothing

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
        if(accuracy >= len(bestGuess)*threshold and len(bestGuess) <= largest):
            # print(bestGuess)
            return bestGuess
        else:
            return None
    
    elif column in [2, 3, 4]:
        ####################################
        ## Corrections to Dates and Hours ##
        ####################################
        digitCorrections = {
            0: ["o", "O", "Q"],  # 0
        1: ["I", "l", "/", "\\", "|", "[", "]", ")"],  # 1
            2: ["z"],  # 2
            3: ["3"],  # 3
            4: ["h"],  # 4
            5: ["s"],  # 5
            6: ["b"],  # 6
        7: ["t", ")", "}"],  # 7
            8: ["B", "&"],  # 8
        9: ["g", "q"],  # 9
        ":": ["'"]
        }
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
        if column in [2, 3]:
            try:
                from time import strptime
                # will only return the best guess if the value is a valid time
                strptime(bestGuess, "%H:%M")
                return bestGuess
            except:
                return None
        elif(column == 4):
            try:
                # will only return the hours if theyre a valid number
                return str(int(bestGuess))
            except:
                return ""  # This is the one exception to the errors The reason why is because we can calculate the hours if we have two valid times
    return None


def requestCorrection(displayImage, col):
    global labelImage
    global errorLabel
    global confidenceDescription
    global AIGuess
    global guessButton
    global orLabel
    global correctionEntry
    global submitButton

    # The guess that should have barely any restriction
    guess = correctValue(displayImage, col, 0.01)
    if (guess == None):  # if the guess relates to LITERALLY nothing available
        guess = ""

    # Setting up image to place in GUI
    image = Image.fromarray(displayImage)

    image = ImageTk.PhotoImage(image)

    # setting values to labels in gui
    labelImage.configure(image=image)
    labelImage.image = image
    errorLabel.configure(
        text="Uh oh. It looks like we couldnt\ncondifently decide who or what this is.\nWe need you to either confirm our guess\nor type in the correct value")
    confidenceDescription.configure(text="Were not confident, but is it:")
    AIGuess.configure(text=guess)
    orLabel.configure(text="or")

    # basically waits till user presses a button and changes variable scope
    while not (guessButton or submitButton):
        pass

    # Resetting changes made
    labelImage.configure(image=None)
    labelImage.image = None
    errorLabel.configure(text=None)
    confidenceDescription.configure(text=None)
    AIGuess.configure(text=None)
    orLabel.configure(text=None)
    if(guessButton):
        guessButton = False
        submitButton = False
        return guess
    elif(submitButton):
        guessButton = False
        submitButton = False
        return correctionEntry.get()


def TranslateDictionary(sheetsDict, gui=False, outputDict=None):
    results = []
    # GUI widgets to manipulate while in middle of function
    if(gui):
        global sheetStatus
        global rowStatus
        global progressBar
        sheetMax = len(sheetsDict)
        sheetInd=0
        rowInd=0
        progressMax = 0
        progressInd = 0

    for sheet in sheetsDict:
        results.append([])
        if gui:
            sheetInd += 1
            rowMax = len(sheet[-1]) - 1
            sheetStatus.configure(text="Sheet: " + str(sheetInd) + " of " + str(sheetMax))

        # Collecting dates on page first
        dates = []
        for date in sheet[:-1]:
            dates.append(tess.image_to_string(date))
        # | Full name | Time in | Time out | hours (possibly blank) | purpose | date | day (possibly blank) |
        for row in sheet[-1][1:]:  # skips first row which is dummy
            if gui:
                rowInd += 1
                rowStatus.configure(text="Row: " + str(rowInd) + " of " + str(rowMax))
            results[-1].append([])
            for col in range(1, len(row)):  # skip first col which is dummy
                temp = correctValue(row[col], col)
                if(temp == None):  # the correction failed. the user must return the correction
                    temp = requestCorrection(row[col], col)
                results[-1][-1].append(temp)
            results[-1][-1].extend(dates)
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
            if (isNum(directory[i][e])):
                cvarray += (directory[i][e]+",")
            else:
                cvarray += (directory[i][e]+",")
        cvarray += (directory[i][-1]+"\n")
        debug(("cvarray["+str(i)+"]:", cvarray))
    return (cvarray+"\n")


# Gui Variables
signinsheet = ""
outputCSV = os.getenv("userprofile").replace(
    "\\", "/") + "/Documents/signinSheetOutput.csv"
submitButton = False
guessButton = False

# Gui Functions


def reconfigOutput():
    global outputCSV
    global outputFile
    outputCSV = filedialog.askopenfilename(filetypes=(
        ("Comma Style Values", "*.csv"), ("Comma Style Values", "*.csv")))
    outputFile.configure(text=outputCSV.split("/")[-1])


def guessSwitch():
    global guessButton
    guessButton = True


def submitSwitch():
    global submitButton
    submitButton = True


def popupTag(title, text, color="#000000"):
    # Popup box for errors and completion
    popupBox = tkinter.Tk()
    popupBox.geometry("335x181+475+267")
    popupBox.minsize(120, 1)
    popupBox.maxsize(1370, 749)
    popupBox.resizable(1, 1)
    popupBox.configure(background="#d9d9d9")
    popupBox.title = title

    popupDescription = tkinter.Label(popupBox, text=text)
    popupDescription.configure(
        background="#ffffff", disabledforeground="#a3a3a3", foreground=color)
    popupDescription.place(relx=0.03, rely=0.055, height=91, width=314)
    popupOK = tkinter.Button(popupBox, text="OK", command=popupBox.destroy)
    popupOK.configure(activebackground="#ececec", activeforeground="#000000", background="#ebebeb",
                      disabledforeground="#a3a3a3", foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0")
    popupOK.place(relx=0.328, rely=0.663, height=34, width=117)
    popupBox.mainloop()


def main():
    global lineCorrection


if __name__ == "__main__":
    root = tkinter.Tk(screenName="OCR To CSV Interpreter")
    root.title("OCR To CSV Interpreter")
    root.geometry("600x450+401+150")
    root.configure(background="#d9d9d9")
    root.minsize(120, 1)
    root.maxsize(1370, 749)
    root.resizable(1, 1)

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
    errorLabel.configure(activebackground="#f9f9f9", activeforeground="black", background="#e1e1e1",
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
