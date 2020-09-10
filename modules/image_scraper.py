import logging
from os.path import exists

import cv2
import numpy as np
from pdf2image import convert_from_path


def collect_contours(image):
    """ Sub function used by scrapper.\n
    @param image: an opencv image\n
    @return returns an ordered list of contours found in the image.\n
    This function was heavily influenced by its source.\n
    @source: https://medium.com/coinmonks/a-box-detection-algorithm-for-any-image-containing-boxes-756c15d7ed26
    """
    debug_index = 0
    # Grab absolute thresh of image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(
        image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    invert = 255 - thresh

    if (logging.getLogger().level <= logging.DEBUG):
        while exists("debugOutput/scrapper/{ind}1invert.jpg".format(ind=debug_index)):
            debug_index += 1
        cv2.imwrite(
            "debugOutput/scrapper/{ind}1invert.jpg".format(ind=debug_index), invert)
    #######################################
    # Defining kernels for line detection #
    #######################################
    kernel_length = np.array(image).shape[1]//80
    verticle_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, kernel_length))  # kernel for finding all verticle lines
    # kernel for finding all horizontal lines
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 3x3 kernel

    # Collecting Verticle Lines
    verticle_lines = cv2.erode(invert, verticle_kernel, iterations=3)
    verticle_lines = cv2.dilate(verticle_lines, verticle_kernel, iterations=3)
    verticle_lines = cv2.threshold(
        verticle_lines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    if (logging.getLogger().level <= logging.DEBUG):
        cv2.imwrite(
            "debugOutput/scrapper/{ind}2verticleLines.jpg".format(ind=debug_index), verticle_lines)

    # Collecting Horizontal Lines
    horizontal_lines = cv2.erode(invert, hori_kernel, iterations=3)
    horizontal_lines = cv2.dilate(horizontal_lines, hori_kernel, iterations=3)
    horizontal_lines = cv2.threshold(
        horizontal_lines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    if (logging.getLogger().level <= logging.DEBUG):
        cv2.imwrite(
            "debugOutput/scrapper/{ind}3horizontalLines.jpg".format(
                ind=debug_index), horizontal_lines)

    # Weighting parameters, this will decide the quantity of an image to be added
    # to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha

    # combining verticle and horizontal lines. This gives us an empty table so that
    # letters dont become boxes
    blank_table = cv2.addWeighted(
        verticle_lines, alpha, horizontal_lines, beta, 0.0)
    blank_table = cv2.erode(~blank_table, kernel, iterations=2)
    blank_table = cv2.threshold(blank_table, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[
        1]  # sharpening new table

    if (logging.getLogger().level <= logging.DEBUG):
        cv2.imwrite(
            "debugOutput/scrapper/{ind}4blankTable.jpg".format(ind=debug_index), blank_table)
    # Detecting all contours, which gives me all box positions
    contours = cv2.findContours(
        blank_table, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

    # Organizing contours
    # we got our boxes, but its mostly to sort the contours
    bboxes = [cv2.boundingRect(c) for c in contours]
    # Sort all the contours in ascending order
    contours, bboxes = zip(
        *sorted(zip(contours, bboxes), key=lambda b: b[1][1], reverse=False))
    return contours

# Generator
# PHASE 1: manipulate image to clearly show tabs


def image_scraper(file, output_array=None):
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
    debug_index = 0
    if not (file.split(".")[1] in ["jpg", "jpeg", "png", "pdf"]):
        return
    elif not exists(file):
        raise FileNotFoundError("File given does not exist.")
    if file.split(".")[1] == "pdf":
        for image in convert_from_path(file):
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            images.append(image)
    else:
        # , cv2.IMREAD_GRAYSCALE)
        images.append(cv2.imread(file, cv2.COLOR_RGB2BGR))

    for image in images:
        contours = collect_contours(image)
        # // This is to tell which boxes correlate to the date
        # Phase 1: Finding Main Boxes ##    // and which big box is the signin table
        #################################
        main_boxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if ((h, w, 3) == image.shape):
                continue
            for m in main_boxes:
                if (x > m[0] and w < m[2]) or (y > m[1] and h < m[3]):
                    break
                elif(x <= m[0] and w >= m[2] and y <= m[1] and h >= m[3]):
                    main_boxes.remove(m)
                    main_boxes.append([x, y, w, h])
            else:
                main_boxes.append([x, y, w, h])

        table = main_boxes[0]  # img that contains whole table

        for x, y, w, h in main_boxes:
            if((w - x > table[2] - table[0]) or (h - y > table[3] - table[1])):
                table = [x, y, w, h]
        main_boxes.remove(table)

        # making images for date and day
        sheets.append([[], []])
        for x, y, w, h in main_boxes:
            sheets[-1][0].append(image[y:y+h, x:x+w])

        # Checking if dates are text and not random images
        for i in range(len(sheets[-1][0]) - 1, -1, -1):
            date = sheets[-1][0][i]
            temp_date = cv2.cvtColor(date, cv2.COLOR_BGR2GRAY)
            temp_date = cv2.threshold(
                temp_date, 230, 255, cv2.THRESH_BINARY_INV)[1]
            black_pixel = cv2.countNonZero(temp_date)
            total_pixel = temp_date.shape[0] * temp_date.shape[1]
            # if the space filled is not between 1%-20%, then its a dud
            if(black_pixel/total_pixel <= 0.01 or black_pixel/total_pixel >= 0.20):
                sheets[-1][0].pop(i)

        #########################################
        # Phase 2: Collecting pairs for mapping #
        #########################################

        # Collecting contours collected from table
        table = image[table[1]-5:table[1]+table[3] +
                      5, table[0]-5:table[0]+table[2]+5]

        if (logging.getLogger().level <= logging.DEBUG):
            cv2.imwrite(
                "debugOutput/scrapper/mainTable{image}.jpg".format(image=debug_index), table)
            debug_index += 1

        # Grabbing verticle and horizontal images of table for better scraping
        table_compute = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
        table_compute = cv2.threshold(
            table_compute, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        table_invert = 255 - table_compute
        t_kernel_length = np.array(table_compute).shape[1]//80
        t_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        #############################
        # Collecting Verticle Pairs #
        #############################
        verticle_points = []
        verticle_pairs = []
        # Creating verticle kernel lines
        t_kernel_verticle = cv2.getStructuringElement(
            cv2.MORPH_RECT, (1, t_kernel_length))
        t_verticle_lines = cv2.erode(
            table_invert, t_kernel_verticle, iterations=3)
        t_verticle_lines = cv2.dilate(
            t_verticle_lines, t_kernel_verticle, iterations=3)
        t_verticle_lines = cv2.threshold(
            t_verticle_lines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if (logging.getLogger().level <= logging.DEBUG):
            cv2.imwrite(
                "debugOutput/scrapper/table{}VertLines.jpg".format(debug_index), t_verticle_lines)
        # Collecting verticle contours
        contours = cv2.findContours(
            t_verticle_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        # Figuring out the length that relates to the majority of the table,
        # (aka, longer lengths relates to length of table rather than random lines)
        max_length = 0
        table_height_pair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if(h >= table.shape[0] * 0.9):  # (y, h) == tableHeightPair):
                verticle_points.append(x)
                verticle_points.append(x + w)
        verticle_points.sort()

        # this is the gap before the table from the left side
        verticle_points.pop(0)
        # this is the gap after the table from the right side
        verticle_points.pop(-1)

        # taking points and making pairs
        for i in range(0, len(verticle_points), 2):
            verticle_pairs.append((verticle_points[i], verticle_points[i + 1]))
        logging.debug("VerticlePairs: %s", verticle_pairs)

        if (logging.getLogger().level <= logging.DEBUG):
            debug_img = cv2.cvtColor(t_verticle_lines, cv2.COLOR_GRAY2BGR)
            for v in verticle_pairs:
                cv2.line(debug_img, (v[0], 0),
                         (v[0], debug_img.shape[0]), (0, 0, 255))
                cv2.line(debug_img, (v[1], 0),
                         (v[1], debug_img.shape[0]), (0, 0, 255))
            cv2.imwrite(
                "debugOutput/scrapper/table{}VertContours.jpg".format(debug_index), debug_img)

        ###############################
        # Collecting Horizontal Pairs #
        ###############################
        horizontal_pairs = []
        horizontal_points = []
        # Creating horizontal kernel lines
        t_kernel_horizontal = cv2.getStructuringElement(
            cv2.MORPH_RECT, (t_kernel_length, 1))
        t_horizontal_lines = cv2.erode(
            table_invert, t_kernel_horizontal, iterations=3)
        t_horizontal_lines = cv2.dilate(
            t_horizontal_lines, t_kernel_horizontal, iterations=3)
        t_horizontal_lines = cv2.threshold(
            t_horizontal_lines, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        if (logging.getLogger().level <= logging.DEBUG):
            cv2.imwrite(
                "debugOutput/scrapper/table{}HorLines.jpg".format(debug_index), t_horizontal_lines)
        # Collecting Horizontal contours
        contours = cv2.findContours(
            t_horizontal_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Figuring out the length that relates to the majority of the table,
        # (aka, longer lengths relates to length of table rather than random lines)
        max_length = 0
        table_width_pair = ()  # empty tuple for checking later
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # (x, w) == tableWidthPair or w >= tHorizontalLines.shape[1] * 0.9):
            if(w >= t_horizontal_lines.shape[1] * 0.9):
                horizontal_points.append(y)
                horizontal_points.append(y + h)
        horizontal_points.sort()
        logging.debug("HorizontalPoints: %s", horizontal_points)

        # this is the gap before the table from the top
        horizontal_points.pop(0)
        # this is the gap after the table from the bottom
        horizontal_points.pop(-1)

        # Building pairs from points
        for i in range(0, len(horizontal_points), 2):
            horizontal_pairs.append(
                (horizontal_points[i], horizontal_points[i + 1]))
        logging.debug("HorizontalPairs: %s", horizontal_pairs)

        if (logging.getLogger().level <= logging.DEBUG):
            debug_img = cv2.cvtColor(t_horizontal_lines, cv2.COLOR_GRAY2BGR)
            for h in horizontal_pairs:
                cv2.line(debug_img, (0, h[0]),
                         (debug_img.shape[1], h[0]), (0, 0, 255))
                cv2.line(debug_img, (0, h[1]),
                         (debug_img.shape[1], h[1]), (0, 0, 255))
            cv2.imwrite(
                "debugOutput/scrapper/table{}HorContours.jpg".format(debug_index), debug_img)

        #####################################
        # Phase 3: Time for actual Scraping #
        #####################################

        # the dictionary thatll hold all our information
        dict_row = 0
        for row in horizontal_pairs:
            sheets[-1][1].append([])
            for col in verticle_pairs:
                sheets[-1][1][dict_row].append(table[row[0]:row[1], col[0]:col[1]])
                if (logging.getLogger().level <= logging.DEBUG):
                    cv2.imwrite(
                        "debugOutput/dictionary/raw/table{}{}.jpg".format(
                            dict_row, col[1]-col[0]), table[row[0]:row[1], col[0]:col[1]])
            dict_row += 1

    if(output_array == None):
        return sheets
    else:
        globals()["output_array"] = sheets.copy()
        return
