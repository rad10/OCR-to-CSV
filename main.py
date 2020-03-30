# import this library to automatically download and install the rest of the libraries if they do not exist
import re
import json
import logging
from modules.imageScraper import imageScraper
from modules.corrections import correctValue, connectDict, JSON
from modules.gui import mainGUI, InstallError, PopupTag
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
    import Image
    import ImageTk

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

# Checking that external software is installed and ready to use
# check if tesseract exists
if os.system("tesseract --help"):
    if os.path.exists("C:\\Program Files\\Tesseract-OCR\\tesseract.exe"):
        tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
    else:
        InstallError(
            "Tesseract", "https://github.com/UB-Mannheim/tesseract/releases", "tesseract.exe").run()
# check if poppler exists
if os.system("pdfimages -help"):
    InstallError("Poppler", "https://poppler.freedesktop.org/",
                 "pdfimages.exe").run()


# Functions


logging.getLogger().setLevel(logging.WARNING)
if "info" in os.sys.argv:
    logging.basicConfig(format="%(asctime)s: INFO %(message)s",
                        datefmt="%H:%M:%S", level=logging.INFO)
elif "debug" in os.sys.argv:
    logging.basicConfig(format="%(asctime)s: DEBUG %(message)s",
                        datefmt="%H:%M:%S", level=logging.DEBUG)
    if not os.path.exists("debugOutput/."):
        os.makedirs("debugOutput/dictionary", exist_ok=True)
        os.makedirs("debugOutput/scrapper", exist_ok=True)
    else:
        os.system("del /s debugOutput\\*.jpg")

JSONFile = open("./aliases.json", "r")
connectDict(json.load(JSONFile))
JSONFile.close()
JSONChange = False  # this is only used when the database is updated
mainDisplay = None


def debug(label: str, content: list):
    logging.debug("%s:", label)
    if(logging.getLogger().level <= logging.DEBUG):
        for i in content:
            print(i)


def debugImageDictionary(diction):
    if (logging.getLogger().level <= logging.INFO):
        debugOutput = "Sheet | SheetLen | TableRow | TableCol\n"
        for sheet in range(len(diction)):
            debugOutput += "{ind: 5d} | {slen: 8d} | {trow: 8d} | {tcol: 8d}\n".format(ind=sheet, slen=len(
                diction[sheet]), trow=len(diction[sheet][-1]), tcol=len(diction[sheet][-1][0]))
        logging.info(debugOutput)
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
        sheetMax = len(sheetsDict)
        sheetInd = 0
        rowInd = 0
        progressMax = 1

        # Getting max for progress bar
        for sheet in sheetsDict:
            progressMax += len(sheet[-1]) - 1
        mainDisplay.progressBar.configure(
            mode="determinate", maximum=progressMax)
    for sheet in sheetsDict:
        results.append([])
        if gui:
            sheetInd += 1
            rowMax = len(sheet[-1]) - 1
            mainDisplay.sheetStatus.configure(
                text="Sheet: " + str(sheetInd) + " of " + str(sheetMax))

        # Collecting dates on page first
        dates = []
        dformat = re.compile(r'\d{1,2}\/\d{1,2}\/(\d{4}|\d{2})')
        dstr = ""
        for date in sheet[:-1]:
            dstr = tess.image_to_string(date).replace(
                "\n", "").replace(" ", "")
            if (bool(dformat.match(dstr))):
                dates.insert(0, (dstr, 1, True))
            else:
                dates.append((dstr, 1, True))

        # | Full name | Time in | Time out | hours (possibly blank) | purpose | date | day (possibly blank) |
        for row in sheet[-1][1:]:  # skips first row which is dummy
            if gui:
                rowInd += 1
                mainDisplay.progressBar.step()
                mainDisplay.rowStatus.configure(
                    text="Row: " + str(rowInd) + " of " + str(rowMax))
                mainDisplay.root.update_idletasks()
            results[-1].append([])
            for col in range(1, len(row)):  # skip first col which is dummy
                logging.info("Sheet[%d]: [%d, %d]", int(
                    sheetInd), int(rowInd), int(col))
                temp = correctValue(row[col], col)
                results[-1][-1].append(temp)
            if(results[-1][-1].count(("", 0, True)) == len(results[-1][-1])):
                results[-1].pop(-1)
            else:
                results[-1][-1].extend(dates)
        if (logging.getLogger().level <= logging.DEBUG):
            for e in range(len(results)):
                debug("Results Sheet[" + str(e) + "]", results[e])
        # Iterating through results to see where errors occured
        for row in range(len(results[-1])):
            for col in range(len(results[-1][row][:-len(dates)])):
                if (results[-1][row][col][2] == False):
                    results[-1][row][col] = mainDisplay.requestCorrection(
                        sheet[-1][row + 1][col + 1], col + 1, results[-1][row][col][0])
                    if (col + 1 in [1, 5]):
                        for entry in JSON["names"][str(col + 1)]:
                            if (results[-1][row][col][0].lower() == entry):
                                break
                        else:
                            JSONChange = True
                            # if the name possibly entered in by the user doesnt exist in the database, add it
                            JSON["names"][str(
                                col + 1)].append(results[-1][row][col][0].lower())
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
            cvarray += (directory[i][e][0]+",")
        cvarray += (directory[i][-1][0]+"\n")
    logging.debug("cvarray:\n%s", cvarray)
    return (cvarray+"\n")


def main():
    ##########################################
    ## Phase 3: Hooking everything together ##
    ##########################################

    try:
        signinsheet = mainDisplay.signinsheet
        outputCSV = mainDisplay.outputCSV
        imageDictionary = imageScraper(signinsheet)
        debugImageDictionary(imageDictionary)
        textDictionary = TranslateDictionary(imageDictionary, gui=True)
        csvString = ""
        for sheet in textDictionary:
            csvString += arrayToCsv(sheet)
        exportToFile(mainDisplay.outputCSV, csvString)
        mainDisplay.errorLabel.configure(text="All finished.")
    except BaseException:
        import traceback
        PopupTag(mainDisplay, "Error", "Looks like something went wrong.\n" +
                 str(os.sys.exc_info())+"\n"+str(traceback.format_exc()), "#ff0000").run()
        raise
    PopupTag(mainDisplay, "Done",
             "Congrats! its all finished.\nLook at your csv and see if it looks alright.").run()
    if (JSONChange):
        JSON["names"]["1"].sort()  # Sorting new libraries for optimization
        JSON["names"]["5"].sort()
        JSONFile = open("aliases.json", "w")
        json.dump(JSON, JSONFile, indent=4, separators=(
            ",", ": "), ensure_ascii=True, sort_keys=True)
        JSONFile.close()

    # Cleaning old ocr files from tmp
    os.system("del /s /q %tmp%\\tess_*.hocr")
    return


mainDisplay = mainGUI(main)
if __name__ == "__main__":
    mainDisplay.run()
