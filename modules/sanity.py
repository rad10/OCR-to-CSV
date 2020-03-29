def sanityName(results: list):
    dupeNames = []
    bestChoice = 0  # The index of the best choice amongst the duplicate names
    bestProb = 0  # the probability of the best choice
    for page in range(len(results)):
        for i in range(len(results[page])):
            if results[page][i][0][2]:
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
        globals["results"] = results
    except:
        pass
    return results


def sanityTime(personRow: list):
    pass


def checkSanity(results: list):
    pass


def checkBlankRow(personRow: list):
    pass
