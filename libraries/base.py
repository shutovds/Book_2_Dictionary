# read data from txt
def read_from_txt(filename):
    file = open(filename, 'r')
    data = re.split(r'\W+', file.read())
    file.close()
    return data


# -----------------
def rem_from(stopwords, dictionary):
    for sword in stopwords:
        inst = Word(sword)
        inst.rem_from_dict(dictionary)
    return dictionary


# -----------------
def write_to_txt(filename, word):
    file = open(filename, 'a')
    file.write(word + '\n')
    file.close()


# -----------------
def frecWordsFromBook(filename):
    wdict = {}

    # read a book fele
    words = read_from_txt(filename)
    for word in words:
        inst = Word(word)
        inst.set_to_dict(wdict)

    new_words_number = len(wdict)
    # print('Количество слов в тексте ', filename, ' = ', new_words_number)

    stopwords = read_from_txt('stopwords.txt')
    wdict = rem_from(stopwords, wdict)

    stopwords = read_from_txt('for_Anki_words.txt')
    wdict = rem_from(stopwords, wdict)

    ankiwords = read_from_anki_txt('Английский слова.txt')
    wdict = rem_from(ankiwords, wdict)

    # words sorted by friequency
    # frecWords=sorted(wdict.items(), key=lambda item: item[1], reverse = True)

    return wdict  # frecWords
