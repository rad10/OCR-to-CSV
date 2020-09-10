import logging
import re
import xml.etree.ElementTree as ET
from itertools import product

import cv2
import pytesseract as tess

tess.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
JSON = {}


def connect_dict(main_JSON: dict):
    """ Used for connecting the JSON database by reference """
    for key, val in main_JSON.items():
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

TIME_FILTER = re.compile(
    r'^(1[0-2]|[1-9]):?([0-5][0-9])$')


def parse_hOCR(html):
    """ Scraped string of hOCR html text to get the outputs organized into nested lists and dictionaries\n
    @param html: a string containing the hOCR content\n
    @return a list of lists and dictionary based on the results of the hOCR
    """
    results = []
    words = []
    chars = []

    # Remove XML Namespace for my own sanity
    try:
        html = html.replace(
            b'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">',
            b'<html lang="en">')
    except TypeError:
        html = html.replace(
            "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">",
            "<html lang=\"en\">")

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
    results = [None for i in words]

    # Populating space of words
    for word in range(len(words)):
        chars = [a for a in words[word]
                 if "id" in a.attrib and "lstm_choices_" in a.attrib["id"]]
        results[word] = [None for i in chars]

        # Populating char dicts in each space
        for char in range(len(chars)):
            results[word][char] = {}
            # placing words into each char
            for cprob in chars[char]:  # getting elements themselves for dict
                results[word][char][cprob.text] = max(
                    float(cprob.attrib["title"][8:]), 1) / 100

        # Checking on letter headers
        char_header = [a for a in words[word] if not "id" in a.attrib]
        if (len(char_header) == len(chars)):
            for char in range(len(char_header)):
                if char_header[char].text in results[word][char]:
                    if float(char_header[char].attrib["title"][char_header[
                            char].attrib["title"].find("x_conf") + 7:])/100 > results[
                                word][char][char_header[char].text]:
                        results[word][char][char_header[char].text] = float(
                            char_header[char].attrib["title"][char_header[char].attrib[
                                "title"].find("x_conf") + 7:])/100
                else:
                    results[word][char][char_header[char].text] = max(float(
                        char_header[char].attrib["title"][char_header[char].attrib[
                            "title"].find("x_conf") + 7:]), 1)/100

    return results


def add_missing(result_arr, key):
    """ Takes values in a given hOCR Output and adds in characters that arent
    present that could have been mistaken for another character. For example,
    a "4" could have been mistaken for an "A". The probability of the new 
    characters are the same as the highest probability of a similiar character.\n
    @param resultArr: The output array from an hOCR output\n
    @param key: This is a string that decides which dictionary to check from.\n
    "a" represents alphabet\n
    "d" represents digits\n
    based on which one you choose wil decide what additions will be considered.\n
    @return an array similar to resultArr, but with any found similar characters
    in there given positions.
    """
    prob = 0
    for word in range(len(result_arr)):  # iterates through words in hocr
        # iterates between each character
        for char in range(len(result_arr[word])):
            # iterates translating dictionary
            for val, sim in corrections[key].items():
                prob = 0
                # will only add new character if it doesnt already exist
                if not val in result_arr[word][char].keys():
                    for j in set(result_arr[word][char]).intersection(sim):
                        # the probability of the character will be equal to the highest
                        # probability of similiar character
                        prob = max(prob, result_arr[word][char][j])
                    if (prob != 0):
                        result_arr[word][char][val] = prob
    return result_arr


def adjust_result(result_arr):
    """ This function specifically affects hOCR outputs that include alphabeticall letters.
    It iterates through the output and makes everything lowercase for better matching. If 
    both the uppercase and lowercase form of a letter exist, then it will go with the highest 
    probability for the lowercase value.\n
    @param resultArr: The hOCR output to be lowered.\n
    @return an output similar to resultArr, but all characters are lowercase.
    """
    for i in range(len(result_arr)):  # iterates through all words
        # iterates through character positions
        for char in range(len(result_arr[i])):
            # iterates through possible chars in slot
            for possible_chars in list(result_arr[i][char].keys()):
                if (possible_chars == None):
                    pass
                elif possible_chars.isupper():
                    # making lower val equal to previous val
                    # takes max prob if lower and upper exist
                    if possible_chars.lower() in result_arr[i][char]:
                        result_arr[i][char][possible_chars.lower()] = max(
                            result_arr[i][char][possible_chars], result_arr[i][char][possible_chars.lower()])
                    else:
                        # otherwise creates lower char with same probability
                        result_arr[i][char][possible_chars.lower(
                        )] = result_arr[i][char][possible_chars]
                    # removes old val from dict
                    del result_arr[i][char][possible_chars]
    return result_arr


def match_name(outputs: list, threshold=0.0):
    """This function is how we get accurate values from the images in each
    dictionary. This one in particular tries to match output to a specific
    name.\n
    @param {list} outputs: The list object that comes from parsing the hOCR
    output of 3 objects.\n
    @param {double} threshold: Optional variable. Changes the percentage of
    characters that need to match the origional of it to return. Higher
    threshholds mean more strict requirements and higher chance of getting
    nothing. Lower threshholds mean higher chance to get a value that may or
    may not be incorrect.\n
    @returns: {tuple} it returns a tuple containing the expected name, the
    probability of that name being true, and a bool discussing whether it passed
    the threshold.
    """
    for i in range(len(outputs)):  # Iterating through all outputs
        outputs[i] = add_missing(outputs[i], "a")
        outputs[i] = adjust_result(outputs[i])

        # Attempting to separate first and last name
        if(len(outputs[i]) > 0):
            # find the largest portion of words. likely either first or last name
            largest_word = max(outputs[i], key=len)
            if(largest_word == outputs[i][0]):
                while(len(outputs[i]) > 2):
                    # Example: Firstname La stN ame
                    outputs[i][1].extend(outputs[i][2])
                    # Firstname LastName
                    outputs[i].pop(2)
            elif(largest_word == outputs[i][-1]):
                while(len(outputs[i]) > 2):
                    # Example Fir stNa me Lastname
                    outputs[i][0].extend(outputs[i][1])
                    # FirstName Lastname
                    outputs[i].pop(1)
            # if the largest portion is in the middle or isnt the largest,
            # then theres no way to guess how to stitch parts together. leave it
            # alone then

    ####################################
    ## CALCULATING NAME PROBABILITIES ##
    ####################################

    temp_name = ""
    temp_list = []
    best_name = "Nan"
    best_prob = 0
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
                if not " " in name:
                    continue  # skip any names with no spaces
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
                temp_name = name.replace(" ", "")
                for li in output:
                    temp_list.extend(li)

                for i in range(min(len(temp_name), len(temp_list))):
                    if temp_name[i] in temp_list[i].keys():
                        probability += temp_list[i][temp_name[i]]
                    elif temp_name[i].upper() in temp_list[i].keys():
                        probability += temp_list[i][temp_name[i].upper()]
                    elif (i < len(temp_list) - 1) and temp_name[i] in temp_list[i + 1].keys():
                        probability += temp_list[i + 1][temp_name[i]] * 0.75
                    elif (i > 0) and temp_name[i] in temp_list[i - 1].keys():
                        probability += temp_list[i - 1][temp_name[i]] * 0.5
                    else:
                        probability += 0  # 0.25

            logging.debug("MatchName %s: %lf", name, probability)
            if(probability > best_prob):
                best_name = name
                best_prob = probability
    logging.info("MatchName Best: %s %lf", best_name, best_prob)
    if (best_name == "Nan"):
        return (best_name, best_prob, False)
    if (best_prob/len(best_name.replace(" ", "")) >= threshold):
        return (best_name, best_prob, True)
    return (best_name, best_prob, False)


def match_time(outputs: list, threshold=0.0):
    """This function is how we get accurate values from the images in each
    dictionary. This one in particular tries to match output to a specific time.\n
    @param {list} outputs: The list object that comes from parsing the hOCR output
    of 3 objects.\n
    @param {double} threshold: Optional variable. Changes the percentage of
    characters that need to match the origional of it to return. Higher threshholds
    mean more strict requirements and higher chance of getting nothing. Lower
    threshholds mean higher chance to get a value that may or may not be incorrect.\n
    @returns: {tuple} it returns a tuple containing the expected name, the probability
    of that name being true, and a bool discussing whether it passed the threshold.
    """
    ####################
    ## Enriching Data ##
    ####################
    time = ""
    time_alt = ""
    probability = 0
    probability_addition = 0
    best_time = "Nan"
    best_prob = 0
    best_alt_prob = 0

    # Adding alternatives
    for i in range(2, -1, -1):
        outputs[i] = add_missing(outputs[i], "d")  # adds alternate digits

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
            probability_addition = 0
            # print(timed)
            for cnum in range(len(timed)):
                probability += outputs[i][0][cnum][timed[cnum]]

            logging.debug("Time: %s - %lf", time, probability)
            if bool(TIME_FILTER.match(time)):
                # BOOSTING PROBABILITY FROM OTHER OUTPUTS

                prob_add = 0  # additional probability to add based on other two outputs
                prob_add_alt = 0  # addition probability if alternate is better

                # Creating alternate with/out colon
                if not ":" in time:
                    time_alt = time[:-2] + ":" + time[-2:]
                else:
                    time_alt = time.replace(":", "")

                logging.info("Probability: %lf", probability)
                logging.info("Time: %s", time)
                logging.info("Time Alternate: %s", time_alt)

                for j in range(len(outputs)):
                    if j == i:  # preventing iterating through itself
                        continue

                    for slot in range(min(len(time), len(outputs[j][0]))):
                        # if the char in the outputs dict, itll add its value
                        # itll only add values if it could fit it
                        if time[slot] in outputs[j][0][slot].keys():
                            prob_add += outputs[j][0][slot][time[slot]]
                        else:
                            prob_add = 0  # do this to remove probability if it doesnt perfectly fit in match
                            break
                    for slot in range(min(len(time_alt), len(outputs[j][0]))):
                        if time_alt[slot] in outputs[j][0][slot].keys():
                            prob_add_alt += outputs[j][0][slot][time_alt[slot]]
                        else:
                            prob_add_alt = 0
                            break

                    # Double assurance for non values
                    if ":" in time or prob_add > prob_add_alt:
                        probability_addition += prob_add
                    else:
                        probability_addition += prob_add_alt
                    # probAdd = max(probAdd, 0)
                    # probAddAlt = max(probAddAlt, 0)

                    # probabilityAddition += probAdd + probAddAlt
                logging.info("Time Probability: %s, %s, %lf, %lf, %lf",
                             time, time_alt, probability, probability_addition,
                             probability + probability_addition)

                # Deciding best decision
                if (probability + probability_addition >= best_prob + best_alt_prob and probability > best_prob):
                    if ":" in time:
                        best_time = time
                    else:
                        best_time = time_alt
                    best_prob = probability
                    best_alt_prob = probability_addition

        # To decide if time probability is past its threshold
        if (best_alt_prob + best_prob > best_prob * len(outputs) * threshold):
            return (best_time, best_prob + best_alt_prob, True)
    return (best_time, best_prob + best_alt_prob, False)


def match_hour(outputs: list, threshold=0.3):
    """This function is how we get accurate values from the images in each dictionary.
    This one in particular tries to match output to a number that represents the
    amount of hours there.\n
    @param {list} outputs: The list object that comes from parsing the hOCR output
    of 3 objects.\n
    @param {double} threshold: Optional variable. Changes the percentage of characters
    that need to match the origional of it to return. Higher threshholds mean
    more strict requirements and higher chance of getting nothing. Lower
    threshholds mean higher chance to get a value that may or may not be
    incorrect.\n
    @returns: {tuple} it returns a tuple containing the expected name, the
    probability of that name being true, and a bool discussing whether it passed
    the threshold.
    """
    hour = ""
    best_hour = ""
    probability = 0
    alt_prob = 0
    best_prob = 0
    best_alt = 0

    # Refining the selection
    for i in range(len(outputs)):
        outputs[i] = add_missing(outputs[i], "d")

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
            alt_prob = 0

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
                    alt_prob += temp

                logging.info("Hour %s: %lf %lf = %lf", hour,
                             probability, alt_prob, probability + alt_prob)
                # Deciding best one
                if (probability + alt_prob > best_prob + best_alt and probability > best_prob):
                    best_hour = hour
                    best_prob = probability
                    best_alt = alt_prob

    if (best_prob + best_alt > best_prob * len(outputs) * threshold):
        return (best_hour, best_prob + best_alt, True)
    return (best_hour, best_prob + best_alt, False)


def match_purpose(outputs: list, threshold=0.3):
    """This function is how we get accurate values from the images in each
    dictionary. This one in particular tries to match output to a specific prupose.\n
    @param {list} outputs: The list object that comes from parsing the hOCR output
    of 3 objects.\n
    @param {double} threshold: Optional variable. Changes the percentage of characters
    that need to match the origional of it to return. Higher threshholds mean
    more strict requirements and higher chance of getting nothing. Lower threshholds
    mean higher chance to get a value that may or may not be incorrect.\n
    @returns: {tuple} it returns a tuple containing the expected purpose, the probability
    of that name being true, and a bool discussing whether it passed the threshold.
    """
    temp_purpose = ""
    temp_list = []
    best_purpose = "Nan"
    best_prob = 0
    probability = 0

    for i in range(len(outputs)):
        outputs[i] = add_missing(outputs[i], "a")
        outputs[i] = adjust_result(outputs[i])

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
                temp_purpose = purpose.replace(" ", "")
                for li in output:
                    temp_list.extend(li)

                for i in range(min(len(temp_purpose), len(temp_list))):
                    if temp_purpose[i] in temp_list[i].keys():
                        probability += temp_list[i][temp_purpose[i]]
                    elif temp_purpose[i].upper() in temp_list[i].keys():
                        probability += temp_list[i][temp_purpose[i].upper()]
                    elif (i < len(temp_list) - 1) and temp_purpose[i] in temp_list[i + 1].keys():
                        probability += temp_list[i + 1][temp_purpose[i]] * 0.75
                    elif (i > 0) and temp_purpose[i] in temp_list[i - 1].keys():
                        probability += temp_list[i - 1][temp_purpose[i]] * 0.5
                    else:
                        probability += 0  # 0.25

            logging.debug("MatchPurpose %s: %lf", purpose, probability)
            if(probability > best_prob):
                best_purpose = purpose
                best_prob = probability
    logging.info("MatchPurpose Best: %s %lf", best_purpose, best_prob)

    if (best_purpose == "Nan"):
        return (best_purpose, best_prob, False)
    if (best_prob/len(best_purpose.replace(" ", "")) >= threshold):
        return (best_purpose, best_prob, True)
    return (best_purpose, best_prob, False)


def correct_value(image, column, threshold=-1):
    """This function is how we get accurate values from the images in each dictionary.\n
    @param {cvimg} image: The image that is being transcribed.\n
    @param {int} column: The column in the table that the image is in. This is
    very important as its part of how the translator corrects the outputs.\n
    @param {double} threshold: Optional variable. Changes the percentage of
    characters that need to match the origional of it to return. Higher threshholds
    mean more strict requirements and higher chance of getting nothing. Lower
    threshholds mean higher chance to get a value that may or may not be incorrect.\n
    @returns: It will return the name that closest resembles the image, or it will
    return \"RequestCorrection:\" if no name could be accepted.\n
    It works by taking an image and running tesseract to get the value from the
    unchanges color image, then it grabs the ocr output from the same image with
    different effects, such as greyscale, thresholds, and contrast increase.\n
    The next step for it is to take each unique value make, then run it through
    another function that creates a new string with the characters in it resembling
    what should be in there (no numbers or symbols in names, no chars in numbers,
    etc.) and adds it to the pile of strings.\n
    The last step is for it take all the new unique strings and run them through
    another function to see which names the strings closest resemble. The name with
    the most conclusions is considered the best guess.\n
    However, the best guess may not be accepted if the name doesnt share enough
    characters in common with all the guesses, then its scrapped and nothing is
    returned.
    """
    thr = 0
    # Default settings for threshold
    if not (threshold == -1):
        thr = threshold

    # Running initial checks to see if cell is empty
    # were creating an inverted thresh of the image for counting pixels, removes
    # 8px border in case it includes external lines or table borders
    invert = cv2.cvtColor(image[8: -8, 8: -8], cv2.COLOR_BGR2GRAY)
    invert = cv2.threshold(
        invert, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    invert = 255 - invert
    # countnonzero only counts white pixels, so i need to invert to turn black pixels
    # white
    pixel_count = cv2.countNonZero(invert)
    pixel_total = invert.shape[0] * invert.shape[1]

    logging.debug("blankPercent: %s", pixel_count/pixel_total)
    # will only consider empty if image used less than 1% of pixels. yes, that small
    if(pixel_count/pixel_total <= 0.01):
        logging.info("It's Blank")
        # Skipping ahead if its already looking like theres nothing
        return ("", 0, True)
    del invert, pixel_count, pixel_total

    outputs = [None] * 3

    conf = ""
    if column in [1, 5]:
        conf = "--dpi 300 -c lstm_choice_mode=2"
    elif column in [2, 3, 4]:
        conf = "--dpi 300 -c lstm_choice_mode=2 -c hocr_char_boxes=1 --psm 8"

    # Safety net incase tesseract breaks for no reason
    try:
        # Get normal results
        outputs[0] = parse_hOCR(tess.image_to_pdf_or_hocr(
            image, lang="eng", extension="hocr", config=conf))

        # Get black and white results
        temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        outputs[1] = parse_hOCR(tess.image_to_pdf_or_hocr(
            temp, lang="eng", extension="hocr", config=conf))

        # get thresh results
        temp = cv2.threshold(
            temp, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        outputs[2] = parse_hOCR(tess.image_to_pdf_or_hocr(
            temp, lang="eng", extension="hocr", config=conf))
    except tess.pytesseract.TesseractError:
        logging.error("Tesseract Error")
        return ("Nan", 0, False)

    # quick check incase box is looking empty; will only skip if 2/3 or more are blank
    if(not (bool(outputs[0]) or bool(outputs[1]) or bool(outputs[2]))):
        logging.info("we couldnt read it")
        # if theres enough pixels to describe a possbile image, then it isnt
        # empty, but it cant read it
        return ("NaN", 0, False)

    ##########################
    ## APPLYING CORRECTIONS ##
    ##########################

    if (column == 1):
        return match_name(outputs, threshold=thr)
    elif(column == 2 or column == 3):
        return match_time(outputs, threshold=thr)
    elif (column == 4):
        return match_hour(outputs, threshold=thr)
    elif(column == 5):
        return match_purpose(outputs, threshold=thr)
    return ("NaN", 0, False)
