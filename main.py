# import this library to automatically download and install the rest of the libraries if they do not exist
import tkinter
from tkinter import filedialog, ttk
from math import floor
from time import sleep
import re
import json
import logging
from modules.imageScraper import imageScraper
from modules.corrections import correctValue, connectDict, JSON

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
if os.system("tesseract --help"):
    if os.path.exists("C:\\Program Files\\Tesseract-OCR\\tesseract.exe"):
        tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
    else:
        installError(
            "Tesseract", "https://github.com/UB-Mannheim/tesseract/releases", "tesseract.exe")
# check if poppler exists
if os.system("pdfimages -help"):
    installError("Poppler", "https://poppler.freedesktop.org/",
                 "pdfimages.exe")
del installError


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
        return (guess, 100, True)
    elif(submitButton):
        guessButton = False
        submitButton = False
        return (result, 100, True)


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
                progressBar.step()
                rowStatus.configure(
                    text="Row: " + str(rowInd) + " of " + str(rowMax))
                root.update_idletasks()
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
                    results[-1][row][col] = requestCorrection(
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

    # Cleaning old ocr files from tmp
    os.system("del /s /q %tmp%\\tess_*.hocr")
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
