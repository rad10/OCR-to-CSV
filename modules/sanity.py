def sanityName(results: list):
    """ This function checks the databases names captured. It checks
    if the name exists multiple times. If it does, it maintains the validity
    of the most accurate name and sets the rest to incorrect to be either
    scanned again or get a request from the user.\n
    @param results: The entire database to be checked for duplicate names\n
    @return the database itself if it isnt modified by reference
    """
    dupeNames = []
    bestChoice = 0  # The index of the best choice amongst the duplicate names
    bestProb = 0  # the probability of the best choice
    for page in range(len(results)):
        for i in range(len(results[page])):
            if results[page][i][0][2] and results[page][i][0][0] != "":
                bestChoice = i
                bestProb = results[page][i][0][1]
                dupeNames.clear()
                dupeNames.append(i)

                # Looking for same names
                for j in range(i + 1, len(results[page])):
                    if not results[page][j][0][2] or (
                            results[page][i][0][0] != results[page][j][0][0]):
                        continue  # if names dont match, or already isnt expected to be correct
                    if (results[page][j][0][1] > bestProb):
                        bestProb = results[page][j][0][1]
                        bestChoice = j
                        # checking for highest probability as it
                        # is most likely to be actual person
                    dupeNames.append(j)

                # removing best candidate from dupe list
                dupeNames.remove(bestChoice)
                for d in dupeNames:
                    results[page][d][0] = (  # all other dupes are considered failure
                        results[page][d][0][0], results[page][d][0][1], False)
                dupeNames.clear()

    # setting it equal
    try:
        globals()["results"] = results
    except:
        pass
    return results


def sanityTime(personRow: list):
    pass


def checkSanity(results: list):
    pass


def checkBlankRow(personRow: list):
    """ This function takes a name row and sees if theres enough information
    to determine if the row has no information in it.\n
    @param personRow the row to be determined whether or not its blank.\n
    @return True if the row is blank and can be removed, False otherwise.
    """
    countConfirms = 1
    countBlanks = 1
    for i in personRow[:4]:
        # and every one. any false will 0 the entire thing
        countConfirms *= i[2]
        countBlanks *= (i[0] == '')
    return countConfirms and countBlanks
