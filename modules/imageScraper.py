import logging
import numpy as nm
import cv2
from pdf2image import convert_from_path
from os.path import exists


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

    if (logging.getLogger().level <= logging.DEBUG):
        while(exists("debugOutput/scrapper/{ind}1invert.jpg".format(ind=debugIndex))):
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

    if (logging.getLogger().level <= logging.DEBUG):
        cv2.imwrite(
            "debugOutput/scrapper/{ind}2verticleLines.jpg".format(ind=debugIndex), verticleLines)

    # Collecting Horizontal Lines
    horizontalLines = cv2.erode(invert, hori_kernel, iterations=3)
    horizontalLines = cv2.dilate(horizontalLines, hori_kernel, iterations=3)
    horizontalLines = cv2.threshold(
        horizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    if (logging.getLogger().level <= logging.DEBUG):
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

    if (logging.getLogger().level <= logging.DEBUG):
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
    elif not (exists(file)):
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
        sheets.append([[], []])
        for x, y, w, h in mainBoxes:
            sheets[-1][0].append(image[y:y+h, x:x+w])

        # Checking if dates are text and not random images
        for i in range(len(sheets[-1][0]) - 1, -1, -1):
            date = sheets[-1][0][i]
            tempDate = cv2.cvtColor(date, cv2.COLOR_BGR2GRAY)
            tempDate = cv2.threshold(
                tempDate, 230, 255, cv2.THRESH_BINARY_INV)[1]
            blackPixel = cv2.countNonZero(tempDate)
            totalPixel = tempDate.shape[0] * tempDate.shape[1]
            # if the space filled is not between 1%-20%, then its a dud
            if(blackPixel/totalPixel <= 0.01 or blackPixel/totalPixel >= 0.20):
                sheets[-1][0].pop(i)

        #########################################
        # Phase 2: Collecting pairs for mapping #
        #########################################

        # Collecting contours collected from table
        table = image[table[1]-5:table[1]+table[3] +
                      5, table[0]-5:table[0]+table[2]+5]

        if (logging.getLogger().level <= logging.DEBUG):
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
        verticlePoints = []
        verticlePairs = []
        # Creating verticle kernel lines
        tKernelVerticle = cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, tKernelLength))
        tVerticleLines = cv2.erode(tableInvert, tKernelVerticle, iterations=3)
        tVerticleLines = cv2.dilate(
            tVerticleLines, tKernelVerticle, iterations=3)
        tVerticleLines = cv2.threshold(
            tVerticleLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if (logging.getLogger().level <= logging.DEBUG):
            cv2.imwrite(
                "debugOutput/scrapper/table{}VertLines.jpg".format(debugIndex), tVerticleLines)
        # Collecting verticle contours
        contours = cv2.findContours(
            tVerticleLines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        # Figuring out the length that relates to the majority of the table, (aka, longer lengths relates to length of table rather than random lines)
        maxLength = 0
        tableHeightPair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if(h >= table.shape[0] * 0.9):  # (y, h) == tableHeightPair):
                verticlePoints.append(x)
                verticlePoints.append(x + w)
        verticlePoints.sort()

        # this is the gap before the table from the left side
        verticlePoints.pop(0)
        # this is the gap after the table from the right side
        verticlePoints.pop(-1)

        # taking points and making pairs
        for i in range(0, len(verticlePoints), 2):
            verticlePairs.append((verticlePoints[i], verticlePoints[i + 1]))
        logging.debug("VerticlePairs: %s", verticlePairs)

        if (logging.getLogger().level <= logging.DEBUG):
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
        horizontalPoints = []
        # Creating horizontal kernel lines
        tKernelHorizontal = cv2.getStructuringElement(
            cv2.MORPH_RECT, (tKernelLength, 1))
        tHorizontalLines = cv2.erode(
            tableInvert, tKernelHorizontal, iterations=3)
        tHorizontalLines = cv2.dilate(
            tHorizontalLines, tKernelHorizontal, iterations=3)
        tHorizontalLines = cv2.threshold(
            tHorizontalLines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if (logging.getLogger().level <= logging.DEBUG):
            cv2.imwrite(
                "debugOutput/scrapper/table{}HorLines.jpg".format(debugIndex), tHorizontalLines)
        # Collecting Horizontal contours
        contours = cv2.findContours(
            tHorizontalLines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Figuring out the length that relates to the majority of the table, (aka, longer lengths relates to length of table rather than random lines)
        maxLength = 0
        tableWidthPair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # (x, w) == tableWidthPair or w >= tHorizontalLines.shape[1] * 0.9):
            if(w >= tHorizontalLines.shape[1] * 0.9):
                horizontalPoints.append(y)
                horizontalPoints.append(y + h)
        horizontalPoints.sort()
        logging.debug("HorizontalPoints: %s", horizontalPoints)

        # this is the gap before the table from the top
        horizontalPoints.pop(0)
        # this is the gap after the table from the bottom
        horizontalPoints.pop(-1)

        # Building pairs from points
        for i in range(0, len(horizontalPoints), 2):
            horizontalPairs.append(
                (horizontalPoints[i], horizontalPoints[i + 1]))
        logging.debug("HorizontalPairs: %s", horizontalPairs)

        if (logging.getLogger().level <= logging.DEBUG):
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

        # the dictionary thatll hold all our information
        dictRow = 0
        for row in horizontalPairs:
            sheets[-1][1].append([])
            for col in verticlePairs:
                sheets[-1][1][dictRow].append(table[row[0]:row[1], col[0]:col[1]])
                if (logging.getLogger().level <= logging.DEBUG):
                    cv2.imwrite(
                        "debugOutput/dictionary/raw/table{}{}.jpg".format(
                            dictRow, col[1]-col[0]), table[row[0]:row[1], col[0]:col[1]])
            dictRow += 1

    if(outputArray == None):
        return sheets
    else:
        globals()[outputArray] = sheets.copy()
        return
