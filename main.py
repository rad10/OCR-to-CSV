import json
import logging
import os
import re
from subprocess import call

from modules.corrections import JSON, connect_dict, correct_value
from modules.gui import InstallError, MainGUI, PopupTag
from modules.image_scraper import image_scraper
from modules.sanity import check_blank_row, sanity_name

# if opencv isnt installed, it'll install it for you
try:
    import numpy as nm
    import cv2
except ImportError:
    if call(["pip", "install", "opencv-python"], shell=True):
        call(["pip", "install", "--user", "opencv-python"], shell=True)
try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    if call(["pip", "install", "pillow"], shell=True):
        call(["pip", "install", "--user", "pillow"], shell=True)
except ImportError:
    import Image
    import ImageTk

# if tesseract isnt installed, itll install it for you
try:
    import pytesseract as tess
except ImportError:
    if call(["pip", "install", "pytesseract"], shell=True):
        call(["pip", "install", "--user", "pytesseract"], shell=True)
    import pytesseract as tess
# installing pdf to image libraries
try:
    from pdf2image import convert_from_path
except ImportError:
    if call(["pip install pdf2image"], shell=True):
        call(["pip install --user pdf2image"], shell=True)
    from pdf2image import convert_from_path

# Checking that external software is installed and ready to use
# check if tesseract exists
if call(["tesseract", "--help"], shell=True):
    if os.path.exists("C:\\Program Files\\Tesseract-OCR\\tesseract.exe"):
        tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
    else:
        InstallError(
            "Tesseract", "https://github.com/UB-Mannheim/tesseract/releases", "tesseract.exe").run()
# check if poppler exists
if call(["pdfimages", "-help"], shell=True):
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
        call(["del", "/s", "debugOutput\\*.jpg"], shell=True)

try:
    JSON_FILE = open("./aliases.json", "r")
except FileNotFoundError:
    JSON_FILE = open("./aliases.json", "w")
    JSON_FILE.write("{\n\"names\": {\n\"1\": [],\n\"5\": []\n}\n}")
    JSON_FILE.close()
    JSON_FILE = open("./aliases.json", "r")
finally:
    connect_dict(json.load(JSON_FILE))
    JSON_FILE.close()
JSON_CHANGE = False  # this is only used when the database is updated
Main_Display = None


def debug(label: str, content: list):
    logging.debug("%s:", label)
    if (logging.getLogger().level <= logging.DEBUG):
        for i in content:
            print(i)


def debug_image_dictionary(diction):
    """ This debugs the image dictionary. It takes a given image dictionary and makes
    a table organized format of images in a debugging folder
    """
    if (logging.getLogger().level <= logging.INFO):
        debug_output = "Sheet | SheetLen | TableRow | TableCol\n"
        for sheet in range(len(diction)):
            debug_output += "{ind: 5d} | {slen: 8d} | {trow: 8d} | {tcol: 8d}\n".format(
                ind=sheet, slen=len(diction[sheet]),
                trow=len(diction[sheet][1]), tcol=len(diction[sheet][1][0]))
        logging.info(debug_output)
        export_to_file("debugOutput/dictionaryStats.txt", debug_output)
        for sheet in range(len(diction)):
            for dates in range(len(diction[sheet][0])):
                cv2.imwrite("debugOutput/dictionary/sheet{sheet}date{date}.jpg".format(
                    sheet=sheet, date=dates), diction[sheet][0][dates])
            for row in range(len(diction[sheet][1])):
                for col in range(len(diction[sheet][1][row])):
                    cv2.imwrite("debugOutput/dictionary/sheet{sheet}table{row}{col}.jpg".format(
                        sheet=sheet, row=row, col=col), diction[sheet][1][row][col])


def export_to_file(file, content):
    open(file, "w").write(content)


def append_to_file(file, content):
    try:
        inside = open(file, "r").read()
        open(file, "w").write(inside + content)
    except:
        open(file, "w").write(content)


def translate_dictionary(sheets_dict, gui=False, output_dict=None):
    """ Phase two of plan. This function goes through the image dictionary passed
    to it and creates a matrix of the dictionary in text.\n
    @param sheetsDict: a matrix of images made from a table.\n
    @param gui: whether to switch on global gui manipulation for the progress bar.\n
    @param output_dict: a variable passed by reference instead of using return.\n
    @return a matrix of strings that represents the text in the image dictionary.
    """
    global JSON
    global JSON_CHANGE
    results = [[] for x in sheets_dict]  # results the size of pages in dict

    # GUI widgets to manipulate while in middle of function
    if(gui):
        sheet_max = len(sheets_dict)
        sheet_ind = 0
        row_ind = 0
        progress_max = 1

        # Gui Texts
        text_scan = "Scanning\tSheet: {sInd} of {sMax}\tRow: {rInd} of {rMax}"
        text_sanitize = "Sanitizing\tSheet: {sInd} of {sMax}\tRow: {rInd} of {rMax}"

        # Getting max for progress bar
        for sheet in sheets_dict:
            progress_max += len(sheet[1]) - 1
        Main_Display.progress_bar.configure(
            mode="determinate", maximum=progress_max)

    # Collecting data to database
    for sheet in range(len(sheets_dict)):
        if gui:
            sheet_ind += 1
            row_max = len(sheets_dict[sheet][1]) - 1
        # Collecting dates on page first
        dates = []
        dformat = re.compile(r'\d{1,2}\/\d{1,2}\/(\d{4}|\d{2})')
        dstr = ""
        for date in sheets_dict[sheet][0]:
            dstr = tess.image_to_string(date).replace(
                "\n", "").replace(" ", "")
            if (bool(dformat.match(dstr))):
                dates.insert(0, (dstr, 1, True))
            else:
                dates.append((dstr, 1, True))

        # | Full name | Time in | Time out | hours (possibly blank) | purpose | date | day (possibly blank) |
        # skips first row which is dummy
        for row in range(1, len(sheets_dict[sheet][1])):
            if gui:
                row_ind += 1
                Main_Display.progress_bar.step()
                Main_Display.sheet_status.configure(
                    text=text_scan.format(sInd=sheet_ind, sMax=sheet_max,
                                          rInd=row_ind, rMax=row_max))
                Main_Display.root.update_idletasks()
            results[sheet].append([None for x in range(5)])  # array of 5 slots
            # skip first col which is dummy
            for col in range(1, len(sheets_dict[sheet][1][row])):
                logging.info("Sheet[%d]: [%d, %d]", int(
                    sheet_ind), int(row_ind), int(col))
                results[sheet][row - 1][col -
                                        1] = correct_value(sheets_dict[sheet][1][row][col], col)
            results[sheet][-1].extend(dates)
        if (logging.getLogger().level <= logging.DEBUG):
            for e in range(len(results)):
                debug("Results Sheet[" + str(e) + "]", results[e])

    # Checking names for repetitions
    results = sanity_name(results)

    # Analysis
    for sheet in range(len(results)):
        # Iterating through results to see where errors occured
        for row in range(len(results[sheet])):
            for col in range(len(results[sheet][row][:-len(dates)])):
                Main_Display.sheet_status.configure(
                    text=text_sanitize.format(
                        sInd=sheet + 1, sMax=len(results),
                        rInd=row + 1, rMax=len(results[sheet])))
                if (results[sheet][row][col][2] == False):
                    results[sheet][row][col] = Main_Display.request_correction(
                        sheets_dict[sheet][1][row + 1][col + 1], results[sheet][row][col][0])
                    if (col + 1 in [1, 5]):
                        for entry in JSON["names"][str(col + 1)]:
                            if (results[sheet][row][col][0].lower() == entry):
                                break
                        else:
                            JSON_CHANGE = True
                            # if the name possibly entered in by the user doesnt
                            # exist in the database, add it
                            JSON["names"][str(
                                col + 1)].append(results[sheet][row][col][0].lower())

        # Checking if any rows are blank
        for row in range(len(results[sheet])-1, -1, -1):
            if check_blank_row(results[sheet][row]):
                results[sheet].pop(row)

    if(output_dict == None):
        return results
    else:
        globals()[output_dict] = results.copy()
        return


def array_to_csv(directory):
    """takes a matrix and returns a string in CSV format.\n
    @param directory: a string[][] matrix that contains the information of
    people at the center.\n
    @return: a string that contains all the information in CSV format.
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
        signinsheet = Main_Display.signinsheet
        output_CSV = Main_Display.output_CSV
        image_dictionary = image_scraper(signinsheet)
        debug_image_dictionary(image_dictionary)
        text_dictionary = translate_dictionary(image_dictionary, gui=True)
        csv_string = ""
        for sheet in text_dictionary:
            csv_string += array_to_csv(sheet)
        export_to_file(Main_Display.output_CSV, csv_string)
        Main_Display.error_label.configure(text="All finished.")
    except BaseException:
        import traceback
        PopupTag(Main_Display, "Error", "Looks like something went wrong.\n" +
                 str(os.sys.exc_info())+"\n"+str(traceback.format_exc()), "#ff0000").run()
        raise
    PopupTag(Main_Display, "Done",
             "Congrats! its all finished.\nLook at your csv and see if it looks alright.").run()
    if (JSON_CHANGE):
        JSON["names"]["1"].sort()  # Sorting new libraries for optimization
        JSON["names"]["5"].sort()
        JSON_file = open("aliases.json", "w")
        json.dump(JSON, JSON_file, indent=4, separators=(
            ",", ": "), ensure_ascii=True, sort_keys=True)
        JSON_file.close()

    # Cleaning old ocr files from tmp
    call(["del", "/s", "/q", "%tmp%\\tess_*.hocr"], shell=True)
    return


Main_Display = MainGUI(main)
if __name__ == "__main__":
    Main_Display.run()
