import re
import logging
import cv2
import pytesseract as tess
import xml.etree.ElementTree as ET
from itertools import product

tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
JSON = {}


def connectDict(mainJSON: dict):
    for key, val in mainJSON.items():
        JSON[key] = val
    try:  # if I connect the dictionary by a variable, I can connect it by reference
        globals()["mainJSON"] = JSON
    except:  # prevents crashes when the value comes from a function return
        pass


corrections = {
    "a": {
        "A": {"^"},  # A
        "B": {"8", "&", "6", "3"},  # B
        "C": {"(", "<", "{", "[", "¢", "©"},  # C G
        "G": {"(", "<", "{", "[", "¢", "©", "6", "e"},
        "E": {"3", "€"},  # E
        "e": {"G"},
        "g": {"9"},  # g
        "I": {"1", "/", "\\", "|", "]", "["},  # I l
        "l": {"1", "/", "\\", "|", "]", "["},
        "O": {"0"},  # O
        "S": {"5", "$"},  # S
        "T": {"7"},  # T
        "Z": {"2"},  # Z
        " ": {None}
    },
    "d": {
        "0": {"o", "O", "Q", "C", "c"},  # 0
        "1": {"I", "l", "/", "\\", "|", "[", "]", "(", ")", "j"},  # 1
        "2": {"z", "Z", "7", "?"},  # 2
        "3": {"E", "B"},  # 3
        "4": {"h", "H", "y", "A"},  # 4
        "5": {"s", "S"},  # 5
        "6": {"b", "e"},  # 6
        "7": {"t", ")", "}", "Z", "z", "2", "?"},  # 7
        "8": {"B", "&"},  # 8
        "9": {"g", "q"},  # 9
        ":": {"'", ".", ",", "i", ";"}
    }
}

timeFilter = re.compile(
    r'^(1[0-2]|[1-9]):?([0-5][0-9])$')


def parseHocr(html):
    results = []
    words = []
    chars = []

    # Remove XML Namespace for my own sanity
    try:
        html = html.replace(
            b'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">', b'<html lang="en">')
    except TypeError:
        html = html.replace(
            "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">", "<html lang=\"en\">")

    root = ET.fromstring(html)

    try:
        # body.div.div.p.span#line_1_1
        base = root[1][0][0][0][0]  # Ends at span#line_1_1
    except IndexError:
        base = root.find("body/div/div/p/span")
        if base == None:
            logging.error("Error: couldnt follow tree properly")
            return [[]]

    # Allocating space for all words
    words = [a for a in base if "id" in a.attrib and "word_" in a.attrib["id"]]
    results = [None] * len(words)

    # Populating space of words
    for word in range(len(words)):
        chars = [a for a in words[word]
                 if "id" in a.attrib and "lstm_choices_" in a.attrib["id"]]
        results[word] = [None] * len(chars)

        # Populating char dicts in each space
        for char in range(len(chars)):
            results[word][char] = {}
            # placing words into each char
            for cprob in chars[char]:  # getting elements themselves for dict
                results[word][char][cprob.text] = max(
                    float(cprob.attrib["title"][8:]), 1) / 100

        # Checking on letter headers
        charHeader = [a for a in words[word] if not "id" in a.attrib]
        if (len(charHeader) == len(chars)):
            for char in range(len(charHeader)):
                if charHeader[char].text in results[word][char]:
                    if float(charHeader[char].attrib["title"][charHeader[
                            char].attrib["title"].find("x_conf") + 7:])/100 > results[
                                word][char][charHeader[char].text]:
                        results[word][char][charHeader[char].text] = float(
                            charHeader[char].attrib["title"][charHeader[char].attrib[
                                "title"].find("x_conf") + 7:])/100
                else:
                    results[word][char][charHeader[char].text] = max(float(
                        charHeader[char].attrib["title"][charHeader[char].attrib[
                            "title"].find("x_conf") + 7:]), 1)/100

    return results


def addMissing(resultArr, key):
    prob = 0
    for word in range(len(resultArr)):  # iterates through words in hocr
        # iterates between each character
        for char in range(len(resultArr[word])):
            # iterates translating dictionary
            for val, sim in corrections[key].items():
                prob = 0
                # will only add new character if it doesnt already exist
                if not val in resultArr[word][char].keys():
                    for j in set(resultArr[word][char]).intersection(sim):
                        # the probability of the character will be equal to the highest probability of similiar character
                        prob = max(prob, resultArr[word][char][j])
                    if (prob != 0):
                        resultArr[word][char][val] = prob
    return resultArr


def adjustResult(resultArr):
    for i in range(len(resultArr)):  # iterates through all words
        # iterates through character positions
        for char in range(len(resultArr[i])):
            # iterates through possible chars in slot
            for possibleChars in list(resultArr[i][char].keys()):
                if (possibleChars == None):
                    pass
                elif possibleChars.isupper():
                    # making lower val equal to previous val
                    # takes max prob if lower and upper exist
                    if possibleChars.lower() in resultArr[i][char]:
                        resultArr[i][char][possibleChars.lower()] = max(
                            resultArr[i][char][possibleChars], resultArr[i][char][possibleChars.lower()])
                    else:
                        # otherwise creates lower char with same probability
                        resultArr[i][char][possibleChars.lower(
                        )] = resultArr[i][char][possibleChars]
                    # removes old val from dict
                    del resultArr[i][char][possibleChars]
    return resultArr


def matchName(outputs: list, threshold=0.0):
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
    for i in range(3):  # Iterating through all outputs
        outputs[i] = addMissing(outputs[i], "a")
        outputs[i] = adjustResult(outputs[i])

        # Attempting to separate first and last name
        if(len(outputs[i]) > 0):
            # find the largest portion of words. likely either first or last name
            largestWord = max(outputs[i], key=len)
            if(largestWord == outputs[i][0]):
                while(len(outputs[i]) > 2):
                    # Example: Firstname La stN ame
                    outputs[i][1].extend(outputs[i][2])
                    # Firstname LastName
                    outputs[i].pop(2)
            elif(largestWord == outputs[i][-1]):
                while(len(outputs[i]) > 2):
                    # Example Fir stNa me Lastname
                    outputs[i][0].extend(outputs[i][1])
                    # FirstName Lastname
                    outputs[i].pop(1)
            # if the largest portion is in the middle or isnt the largest,
            # then theres no way to guess how to stitch parts together. leave it alone then

    ####################################
    ## CALCULATING NAME PROBABILITIES ##
    ####################################

    tempName = ""
    tempList = []
    bestName = "Nan"
    bestProb = 0
    probability = 0
    for name in JSON["names"]["1"]:
        for output in outputs:
            probability = 0

            # Calculation for single words
            if(len(output) == 1):
                for char in range(min(len(name), len(output[0]))):
                    # if the character is in the same position
                    if name[char] in output[0][char].keys():
                        probability += output[0][char][name[char]]
                        # if the character is in next position and none is currently available
                    elif (None in output[0][char].keys()) and (
                            char < len(output[0]) - 1) and name[char] in output[0][char + 1].keys():
                        probability += output[0][char + 1][name[char]]
                    # if the character is in next pos
                    elif (char < len(output[0]) - 1) and name[char] in output[0][char + 1].keys():
                        probability += output[0][char + 1][name[char]] * 0.75
                    # if character is in previous position
                    elif (char > 0) and name[char] in output[0][char - 1].keys():
                        probability += output[0][char - 1][name[char]] * 0.5
                    else:  # if the character just doesnt exist
                        probability += 0  # 0.25

            # Calculation for exactly two words
            # separate first and last name and evaluate
            elif (len(output) == 2):
                namep = name.split(" ", 2)
                for word in range(2):
                    for char in range(min(len(namep[word]), len(output[word]))):
                        if namep[word][char] in output[word][char].keys():
                            probability += output[word][char][namep[word][char]]
                        elif (char < len(output[word]) - 1) and namep[word] in output[word][char + 1].keys():
                            probability += output[word][char +
                                                        1][namep[word][char]] * 0.75
                        elif (char > 0) and namep[word][char] in output[word][char - 1].keys():
                            probability += output[word][char -
                                                        1][namep[word][char]] * 0.5
                        else:
                            probability += 0  # 0.25

            # its more than 1 or 2 words. strip all words down to one line and evaluate
            else:
                tempName = name.replace(" ", "")
                for li in output:
                    tempList.extend(li)

                for i in range(min(len(tempName), len(tempList))):
                    if tempName[i] in tempList[i].keys():
                        probability += tempList[i][tempName[i]]
                    elif tempName[i].upper() in tempList[i].keys():
                        probability += tempList[i][tempName[i].upper()]
                    elif (i < len(tempList) - 1) and tempName[i] in tempList[i + 1].keys():
                        probability += tempList[i + 1][tempName[i]] * 0.75
                    elif (i > 0) and tempName[i] in tempList[i - 1].keys():
                        probability += tempList[i - 1][tempName[i]] * 0.5
                    else:
                        probability += 0  # 0.25

            logging.debug("MatchName %s: %lf", name, probability)
            if(probability > bestProb):
                bestName = name
                bestProb = probability
    logging.info("MatchName Best: %s %lf", bestName, bestProb)
    if (bestProb/len(bestName.replace(" ", "")) >= threshold):
        return (bestName, bestProb, True)
    return (bestName, bestProb, False)


def matchTime(outputs: list, threshold=0.0):
    ####################
    ## Enriching Data ##
    ####################
    time = ""
    timeAlt = ""
    probability = 0
    probabilityAddition = 0
    bestTime = "Nan"
    bestProb = 0
    bestAltProb = 0

    # Adding alternatives
    for i in range(2, -1, -1):
        outputs[i] = addMissing(outputs[i], "d")  # adds alternate digits

        # Checking if size constraints are correct
        if ((len(outputs[i]) > 1) or (
                # if its a size less than 3, then itll never be a time
                len(outputs[i][0]) < 3) or (
                    # if colon in middle, then
                    len(outputs[i][0]) < 4 and ":" in outputs[i][0][-3]) or (
                        len(outputs[i][0]) > 4 and not ":" in outputs[i][0][-3]) or (
                            len(outputs[i][0]) > 5)):
            print("Failed size")
            for char in outputs[i][0]:
                print(char)
            print(len(outputs[i][0]))
            outputs.pop(i)

    for i in range(len(outputs)):
        # Removing any letters in dictionary
        for slot in range(len(outputs[i][0])):
            for char in list(outputs[i][0][slot].keys()):
                if not char.isdigit() and char != ":":
                    # if the key isnt a number or a colon, then remove it
                    del outputs[i][0][slot][char]

        ###########################
        # Calculating Probability #
        ###########################

        # Permutating through all combos in the list
        for timed in product(*outputs[i][0]):
            # building the time string
            time = "".join(timed)
            probability = 0
            probabilityAddition = 0
            # print(timed)
            for cnum in range(len(timed)):
                probability += outputs[i][0][cnum][timed[cnum]]

            logging.debug("Time: %s - %lf", time, probability)
            if bool(timeFilter.match(time)):
                # BOOSTING PROBABILITY FROM OTHER OUTPUTS

                probAdd = 0  # additional probability to add based on other two outputs
                probAddAlt = 0  # addition probability if alternate is better

                # Creating alternate with/out colon
                if not ":" in time:
                    timeAlt = time[:-2] + ":" + time[-2:]
                else:
                    timeAlt = time.replace(":", "")

                logging.info("Probability: %lf", probability)
                logging.info("Time: %s", time)
                logging.info("Time Alternate: %s", timeAlt)

                for j in range(len(outputs)):
                    if j == i:  # preventing iterating through itself
                        continue

                    for slot in range(min(len(time), len(outputs[j][0]))):
                        # if the char in the outputs dict, itll add its value
                        # itll only add values if it could fit it
                        if time[slot] in outputs[j][0][slot].keys():
                            probAdd += outputs[j][0][slot][time[slot]]
                        else:
                            probAdd = 0  # do this to remove probability if it doesnt perfectly fit in match
                            break
                    for slot in range(min(len(timeAlt), len(outputs[j][0]))):
                        if timeAlt[slot] in outputs[j][0][slot].keys():
                            probAddAlt += outputs[j][0][slot][timeAlt[slot]]
                        else:
                            probAddAlt = 0
                            break

                    # Double assurance for non values
                    if ":" in time or probAdd > probAddAlt:
                        probabilityAddition += probAdd
                    else:
                        probabilityAddition += probAddAlt
                    # probAdd = max(probAdd, 0)
                    # probAddAlt = max(probAddAlt, 0)

                    # probabilityAddition += probAdd + probAddAlt
                logging.info("Time Probability: %s, %s, %lf, %lf, %lf",
                             time, timeAlt, probability, probabilityAddition, probability + probabilityAddition)

                # Deciding best decision
                if (probability + probabilityAddition >= bestProb + bestAltProb and probability > bestProb):
                    if ":" in time:
                        bestTime = time
                    else:
                        bestTime = timeAlt
                    bestProb = probability
                    bestAltProb = probabilityAddition

        # To decide if time probability is past its threshold
        if (bestAltProb + bestProb > bestProb * len(outputs) * threshold):
            return (bestTime, bestProb + bestAltProb, True)
    return (bestTime, bestProb + bestAltProb, False)


def matchHour(outputs: list, threshold=0.3):
    hour = ""
    bestHour = "Nan"
    probability = 0
    altProb = 0
    bestProb = 0
    bestAlt = 0

    # Refining the selection
    for i in range(len(outputs)):
        outputs[i] = addMissing(outputs[i], "d")

        # Removing non int values
        for slot in range(len(outputs[i][0])):
            for char in list(outputs[i][0][slot].keys()):
                if not (char.isdigit() or char.isdecimal()):
                    del outputs[i][0][slot][char]

    # Calculations
    for i in range(len(outputs)):
        for hourd in product(*outputs[i][0]):
            hour = "".join(hourd)
            probability = 0
            altProb = 0

            if not (hour.isdigit() or hour.isdecimal()):
                continue

            # Building hour string
            for char in range(len(hourd)):
                probability += outputs[i][0][char][hourd[char]]

            if (hour.isdigit() or hour.isdecimal()):
                for j in range(len(outputs)):
                    temp = 0
                    if i == j:
                        continue
                    for char in range(min(len(hour), len(outputs[j][0]))):
                        if char in outputs[j][0][char]:
                            temp += outputs[j][0][char]
                        else:
                            temp = 0
                            break
                    altProb += temp

                logging.info("Hour %s: %lf %lf = %lf", hour,
                             probability, altProb, probability + altProb)
                # Deciding best one
                if (probability + altProb > bestProb + bestAlt and probability > bestProb):
                    bestHour = hour
                    bestProb = probability
                    bestAlt = altProb

    if (bestProb + bestAlt > bestProb * len(outputs) * threshold):
        return (bestHour, bestProb + bestAlt, True)
    return (bestHour, bestProb + bestAlt, False)


def matchPurpose(outputs: list, threshold=0.3):
    tempPurpose = ""
    tempList = []
    bestPurpose = "Nan"
    bestProb = 0
    probability = 0

    for i in range(len(outputs)):
        outputs[i] = addMissing(outputs[i], "a")
        outputs[i] = adjustResult(outputs[i])

    # iterating through possible results
    for output in outputs:
        for purpose in JSON["names"]["5"]:
            probability = 0

            # Checking for 1 word purposes
            if (len(output) == 1):
                if " " in purpose:  # skip any purpose that isnt exactly one word
                    continue
                for slot in range(min(len(purpose), len(output[0]))):
                    # if the character is in the same position
                    if purpose[slot] in output[0][slot].keys():
                        probability += output[0][slot][purpose[slot]]
                    # if the character is in next position and none is currently available
                    elif (None in output[0][slot].keys()) and (
                            slot < len(output[0]) - 1) and purpose[slot] in output[0][slot + 1].keys():
                        probability += output[0][slot + 1][purpose[slot]]
                    # if the character is in next pos
                    elif (slot < len(output[0]) - 1) and purpose[slot] in output[0][slot + 1].keys():
                        probability += output[0][slot +
                                                 1][purpose[slot]] * 0.75
                    # if character is in previous position
                    elif (slot > 0) and purpose[slot] in output[0][slot - 1].keys():
                        probability += output[0][slot - 1][purpose[slot]] * 0.5
                    else:  # if the character just doesnt exist
                        probability += 0  # 0.25
            else:  # for literally any other value
                tempPurpose = purpose.replace(" ", "")
                for li in output:
                    tempList.extend(li)

                for i in range(min(len(tempPurpose), len(tempList))):
                    if tempPurpose[i] in tempList[i].keys():
                        probability += tempList[i][tempPurpose[i]]
                    elif tempPurpose[i].upper() in tempList[i].keys():
                        probability += tempList[i][tempPurpose[i].upper()]
                    elif (i < len(tempList) - 1) and tempPurpose[i] in tempList[i + 1].keys():
                        probability += tempList[i + 1][tempPurpose[i]] * 0.75
                    elif (i > 0) and tempPurpose[i] in tempList[i - 1].keys():
                        probability += tempList[i - 1][tempPurpose[i]] * 0.5
                    else:
                        probability += 0  # 0.25

            logging.debug("MatchPurpose %s: %lf", purpose, probability)
            if(probability > bestProb):
                bestPurpose = purpose
                bestProb = probability
    logging.info("MatchPurpose Best: %s %lf", bestPurpose, bestProb)
    if (bestProb/len(bestPurpose.replace(" ", "")) >= threshold):
        return (bestPurpose, bestProb, True)
    return (bestPurpose, bestProb, False)


def correctValue(image, column, threshold=-1):
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
    thr = 0
    # Default settings for threshold
    if not (threshold == -1):
        thr = threshold

    # Running initial checks to see if cell is empty
    # were creating an inverted thresh of the image for counting pixels, removes 8px border in case it includes external lines or table borders
    invert = cv2.cvtColor(image[8: -8, 8: -8], cv2.COLOR_BGR2GRAY)
    invert = cv2.threshold(
        invert, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    invert = 255 - invert
    # countnonzero only counts white pixels, so i need to invert to turn black pixels white
    pixelCount = cv2.countNonZero(invert)
    pixelTotal = invert.shape[0] * invert.shape[1]

    logging.debug("blankPercent: %s", pixelCount/pixelTotal)
    # will only consider empty if image used less than 1% of pixels. yes, that small
    if(pixelCount/pixelTotal <= 0.01):
        logging.info("It's Blank")
        # Skipping ahead if its already looking like theres nothing
        return ("", 0, True)
    del invert, pixelCount, pixelTotal

    outputs = [None] * 3

    conf = ""
    if column in [1, 5]:
        conf = "--dpi 300 -c lstm_choice_mode=2"
    elif column in [2, 3, 4]:
        conf = "--dpi 300 -c lstm_choice_mode=2 -c hocr_char_boxes=1 --psm 8"

    # Get normal results
    outputs[0] = parseHocr(tess.image_to_pdf_or_hocr(
        image, lang="eng", extension="hocr", config=conf))

    # Get black and white results
    temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    outputs[1] = parseHocr(tess.image_to_pdf_or_hocr(
        temp, lang="eng", extension="hocr", config=conf))

    # get thresh results
    temp = cv2.threshold(
        temp, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    outputs[2] = parseHocr(tess.image_to_pdf_or_hocr(
        temp, lang="eng", extension="hocr", config=conf))

    # quick check incase box is looking empty; will only skip if 2/3 or more are blank
    if(not (bool(outputs[0]) or bool(outputs[1]) or bool(outputs[2]))):
        logging.info("we couldnt read it")
        # if theres enough pixels to describe a possbile image, then it isnt empty, but it cant read it
        return ("NaN", 0, False)

    ##########################
    ## APPLYING CORRECTIONS ##
    ##########################

    if (column == 1):
        return matchName(outputs, threshold=thr)
    elif(column == 2 or column == 3):
        return matchTime(outputs, threshold=thr)
    elif (column == 4):
        return matchHour(outputs, threshold=thr)
    elif(column == 5):
        return matchPurpose(outputs, threshold=thr)
    return ("NaN", 0, False)
