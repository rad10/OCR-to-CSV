def sanity_name(results: list):
    """ This function checks the databases names captured. It checks
    if the name exists multiple times. If it does, it maintains the validity
    of the most accurate name and sets the rest to incorrect to be either
    scanned again or get a request from the user.\n
    @param results: The entire database to be checked for duplicate names\n
    @return the database itself if it isnt modified by reference
    """
    dupe_names = []
    best_choice = 0  # The index of the best choice amongst the duplicate names
    best_prob = 0  # the probability of the best choice
    for page in range(len(results)):
        for i in range(len(results[page])):
            if results[page][i][0][2] and results[page][i][0][0] != "":
                best_choice = i
                best_prob = results[page][i][0][1]
                dupe_names.clear()
                dupe_names.append(i)

                # Looking for same names
                for j in range(i + 1, len(results[page])):
                    if not results[page][j][0][2] or (
                            results[page][i][0][0] != results[page][j][0][0]):
                        continue  # if names dont match, or already isnt expected to be correct
                    if (results[page][j][0][1] > best_prob):
                        best_prob = results[page][j][0][1]
                        best_choice = j
                        # checking for highest probability as it
                        # is most likely to be actual person
                    dupe_names.append(j)

                # removing best candidate from dupe list
                dupe_names.remove(best_choice)
                for d in dupe_names:
                    results[page][d][0] = (  # all other dupes are considered failure
                        results[page][d][0][0], results[page][d][0][1], False)
                dupe_names.clear()

    # setting it equal
    try:
        globals()["results"] = results
    except:
        pass
    return results


def sanity_time(person_pow: list):
    pass


def check_sanity(results: list):
    pass


def check_blank_row(person_row: list):
    """ This function takes a name row and sees if theres enough information
    to determine if the row has no information in it.\n
    @param personRow the row to be determined whether or not its blank.\n
    @return True if the row is blank and can be removed, False otherwise.
    """
    count_confirms = 1
    count_blanks = 1
    for i in person_row[:4]:
        # and every one. any false will 0 the entire thing
        count_confirms *= i[2]
        count_blanks *= (i[0] == '')
    return count_confirms and count_blanks
