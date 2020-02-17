import re
import logging
import cv2
import pytesseract as tess

tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
JSON = {}


def connectDict(mainJSON: dict):
    for key, val in mainJSON.items():
        JSON[key] = val
    try:  # if I connect the dictionary by a variable, I can connect it by reference
        globals()["mainJSON"] = JSON
    except:  # prevents crashes when the value comes from a function return
        pass


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
    if (col == 1 and id.count(" ") == 1):
        for alias in JSON["names"]["1"]:
            matches = 0
            for i in range(min(alias.find(" "), id.find(" "))):
                if(id[i] == alias[i]):
                    matches += 1
            lalias = alias.find(" ") + 1
            lid = id.find(" ") + 1
            for i in range(min(len(alias) - lalias, len(id) - lid)):
                if(id[lid + i] == alias[lalias + i]):
                    matches += 1
            if (matches > mostMatches):
                closestMatch = alias
                mostMatches = matches
    else:
        for alias in JSON["names"][str(col)]:
            matches = 0
            for i in range(min(len(id), len(alias))):
                if(id[i] == alias[i]):
                    matches += 1
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
        return ""  # Skipping ahead if its already looking like theres nothing
    del invert, pixelCount, pixelTotal

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

    # quick check incase box is looking empty; will only skip if 2/3 or more are blank
    if(outputs.count("") >= len(outputs)*0.5):
        logging.info("we couldnt read it")
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

        for string in outputs:  # Remove duplicate entries
            for copies in range(outputs.count(string) - 1):
                outputs.remove(string)

        # Removing blank entries. it wasnt considered blank, so it shouldnt be there
        for blanks in range(outputs.count("")):
            outputs.remove("")

        logging.debug("Words[outputs]: %s", outputs)
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
        logging.debug("Words[Guesses]: %s", guesses)
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

        logging.debug("Words[accuracy]: %s", accuracy)
        logging.info("Words[bestGuess]: %s", bestGuess)
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
            "0": ["o", "O", "Q", "C", "c"],  # 0
            "1": ["I", "l", "/", "\\", "|", "[", "]", "(", ")", "j"],  # 1
            "2": ["z", "Z"],  # 2
            "3": ["E"],  # 3
            "4": ["h", "H", "y", "A"],  # 4
            "5": ["s", "S"],  # 5
            "6": ["b", "e"],  # 6
            "7": ["t", ")", "}"],  # 7
            "8": ["B", "&"],  # 8
            "9": ["g", "q"],  # 9
            ":": ["'", ".", ","]
        }

        template = ""
        correctFormat = []  # the array that will only take in outputs that fit formatting

        logging.debug("outputs[nums]: %s", outputs)
        if column in [2, 3]:
            # Source for regex string http://regexlib.com/DisplayPatterns.aspx?cattabindex=4&categoryId=5&AspxAutoDetectCookieSupport=1
            timeFilter = re.compile(
                r'^((([0]?[1-9]|1[0-2])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?( )?(AM|am|aM|Am|PM|pm|pM|Pm))|(([0]?[0-9]|1[0-9]|2[0-3])(:|\.)[0-5][0-9]((:|\.)[0-5][0-9])?))$')

            # Removing outputs either too big or too small to be plausible time.
            colonSet = set(digitCorrections[":"])
            colonSet.add(":")
            for i in range(len(outputs) - 1, -1, -1):
                if ((len(outputs[i]) < 3 + bool(set(outputs[i]) & colonSet)) or (len(outputs[i]) > 4 + bool(set(outputs[i]) & colonSet))):
                    outputs.pop(i)

            logging.debug("time[outputs]: %s", outputs)
            # Doing translations
            # by using a while loop, I allow the program to keep checkign until the entire array is gone, assuring no out of place characters
            while(0 < len(outputs)):
                # checking if item is already time or digit incase we can skip it
                # if the string matches a time, sends it straight to correct values
                if(bool(timeFilter.match(outputs[0]))):
                    for e in range(outputs.count(outputs[0])):
                        correctFormat.append(outputs[0])
                # If its a number, then it will turn the number into a time and put it into resulting check if its a proper time.
                elif (outputs[0].isdigit() or outputs[0].isdecimal()):
                    # make template word so that it can be molded into a time.
                    template = outputs[0]
                    for e in range(len(template) - 2, 0, -2):
                        template = template[:e] + ":" + template[e:]
                    # if the time is legit, then add all repeating similiar strings
                    if(bool(timeFilter.match(template))):
                        for e in range(outputs.count(outputs[0])):
                            correctFormat.append(template)
                else:
                    for digit, sets in digitCorrections.items():  # iterate through entire translation dictionary
                        # iterates only between the characters that can be replaced.
                        for elem in set(sets).intersection(set(outputs[0])):
                            for e in range(outputs.count(outputs[0])):
                                outputs.append(
                                    outputs[0].replace(elem, digit))
                # once added additional lines or added legit guesses, removed all of string to avoid checking it again.
                template = outputs[0]
                for e in range(outputs.count(outputs[0])):
                    outputs.remove(template)

        elif(column == 4):
            while(0 < len(outputs)):
                if (outputs[0].isdigit() or outputs[0].isdecimal()):
                    # if the number discovered is less than 12 hours, because no one is expected to be there the entire day.
                    if (int(outputs[0]) < 12):
                        for e in range(outputs.count(outputs[0])):
                            correctFormat.append(outputs[0])
                else:  # if the string has alpha letters in it: attempt to translate
                    for digit, sets in digitCorrections.items():
                        for elem in set(sets).intersection(set(outputs[0])):
                            for e in range(outputs.count(outputs[0])):
                                outputs.append(
                                    outputs[0].replace(elem, digit))
                template = outputs[0]
                for e in range(outputs.count(outputs[0])):
                    outputs.remove(template)
        if (len(correctFormat) == 0):
            return "RequestCorrection:NaN"
        else:
            bestGuess = max(set(correctFormat), key=correctFormat.count)
        if (threshold == 0):
            return bestGuess
        if column in [2, 3]:
            logging.info("time[bestguess]: %s", bestGuess)
            logging.debug("time[correctFormat]: %s", correctFormat)
            if(bool(timeFilter.match(bestGuess))):
                return bestGuess
            else:
                return "RequestCorrection:" + str(bestGuess)
        elif(column == 4):
            logging.info("hours[bestguess]: %s", bestGuess)
            if(bestGuess.isdigit() or bestGuess.isdecimal()):
                # will only return the hours if theyre a valid number
                return bestGuess
            else:
                return ""  # This is the one exception to the errors The reason why is because we can calculate the hours if we have two valid times
    return "RequestCorrection:"
