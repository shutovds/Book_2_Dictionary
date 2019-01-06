# This Python file uses the following encoding: utf-8

"""
This module includes the following classes to generate main menu of program:
classes:
 * Database
 * Books
 * Dictionaries
 * Words
 * Misc
 * Help
"""

import gettext
import webbrowser
import sys

from libraries import db_lib as db
from settings.setting import BASEPATH

DB_PATH = 'settings/objects.sqlite'
ANKI_FILE = 'Anki/FromAnki.txt'
LANG = 'en'
CONF_LIST = ('Y', 'y', 'yes')


def chang_lang(lg_name):
    """
    The function set up language for main menu
    """
    global LANG
    global _
    LANG = [lg_name]
    language = gettext.translation('main', languages=LANG, localedir='./locale')
    _ = language.gettext
    language.install()
    return LANG


_ = gettext.gettext

MAIN_INSTRUCTION = '''
\n:
    Settings:
        lang - You can choose the language for interface (English or Russian)
        h - help
        q - quit
        format - to format database (all data will be deleted)
    Anki:
        aw    - import words from Anki
    Books:
        imbook - import book to database
        lbook  - print list of books
        rbook  - rename book
        dbook  - delete book
        abook  - analyze the words in the book (change the word, add word to dictionary,
                 add word to ignore, mark word as studied, delete word from database)
    Dictionaries:
        cdic  - create dictionary
        ldic  - print the list of dictionaries
        rdic  - rename dictionary
        ddic  - delete dictionary
        wdic  - print the list of words from dictionaries
        dwd   - delete word from dictionary
    Word:
        fword  - find the word in database (return info (in what books and how many times, 
                in what dictionaries))
        chword - change the word (front, transcription, back, examples, comment)
        a2dic  - add word to dictionary     
        '''


def choose_from_menu(choice):
    """
    main menu function
    """
    result = Misc.submenu(choice)

    if result is False:
        result = Dictionaries.submenu(choice)

    if result is False:
        result = Books.submenu(choice)

    if result is False:
        result = Words.submenu(choice)

    if result is False:
        result = Help.submenu(choice)

    if result is False:
        Misc.wrong_choice()


class Database:
    """
    This class provides methods for work with database
    """
    @staticmethod
    def format():
        """
        The function formats the database (remove all data and create new tables)
        """
        confirm = input(_('Are you sure you want to format database ?'
                          '(all data will be lost) y/n:'))
        if confirm in CONF_LIST:
            db.create_new_tables()
            print(_('Database was formatted. All data was deleted'))
        else:
            print(_('Formatting was canceled'))

    @staticmethod
    def import_f_anki():
        """
        import words from Anki export file
        """
        file = open(ANKI_FILE, 'r')
        rows = [line.rstrip().split('\t', 6) for line in file]
        file.close()
        result = db.anki_t_db(rows)
        if result:
            print(_("Words from AnkiFile were successfully imported into DB"))
        else:
            print(_("Words from AnkiFile weren't imported into DB"))


# ---------------------- Book


class Books:  # list_books
    """
    This class provides methods for books handling
    """
    @staticmethod
    def submenu(choice_name):
        """
        Submenu for Books
        """

        if choice_name == "lbook":  # print list of books
            return Books.list_books()

        if choice_name == "imbook":  # import book to database
            return Books.import_book()

        if choice_name == "rbook":  # rename dictionary
            return Books.rename_book()

        if choice_name == "dbook":  # delete book
            return Books.dell_book()

        return False

    @staticmethod
    def list_books():
        """
        Print the list of downloaded books
        """
        if db.list_books():
            print(_('\nBooks that were downloaded: '))
            for name in db.list_books():
                print(' '*4, name[0], '#words = ', name[2])
        else:
            print(' '*4, "DB doesn't contain any books")

    @staticmethod
    def import_book():
        """
        Download book to database
        """
        print(_("Import book to database for analysis"))
        next_step = None
        while next_step != 'y' or next_step != 'n':
            print(_("Copy the book_name.txt file to the Books folder"))
            separator4()
            book_name = input(_('Type the name of the book (without .txt): '))
            if db.check_book_exist(book_name):
                print(_("This book is already in database. "
                        "Please choose another book_name!"))
            else:
                path = BASEPATH + '/Books/' + book_name + '.txt'
                print(_("Download '{path}'?".format(path=path)))
                next_step = input('y/n: ')
                separator4()

                if next_step == 'y':

                    result = db.book_t_db(path, book_name)
                    if result:
                        print(_("Book was downloaded to database."))
                        print(_("Please, wait for a minute while program is analysing the words."))

                        result = db.words_from_book_2db(book_name)
                        if result:
                            print(_("Words from book were imported to database"))
                            break
                        else:
                            print(_("Words import Error"))

                    else:
                        print(_("Book wasn't downloaded! Please, check the book_name!"))
                        separator4()
                        next_step = input(_('Do you want to download a book? y/n: '))

                elif next_step == 'n':
                    print(_("Book download was cancelled!"))
                    break
                else:
                    next_step = input(_('\nDo you want to download a book? y/n: '))

    # /todo check (how dell_book remove all words from the word table if they not in existing book
    @staticmethod
    def dell_book():
        """
        Remove book from dictionary
        """
        book = input(_("Choose the book: "))
        book_id = db.check_book_exist(book)
        if book_id:
            confirm = input(_('Are you sure you want to delete the book? y/n:'))
            if confirm in CONF_LIST:
                if db.del_book(book_id):
                    print(_("Book '{name}' was deleted".format(name=book)))
                else:
                    print(_("Book '{name}' wasn't deleted".format(name=book)))
            else:
                print(_('Deletion canceled'))
        else:
            print(_("Book '{name}' doesn't exist".format(name=book)))

    @staticmethod
    def rename_book():
        """
        Rename book
        """
        book = input(_('Choose the book:  '))
        if db.check_book_exist(book):
            new = input(_('Choose new name for book: '))
            if not db.check_book_exist(new):
                confirm = input(_('Are you sure you want to rename the book? y/n: '))
                if confirm in CONF_LIST:
                    result = db.rename_book(book, new)
                    if result:
                        print(_('Book \'{old}\' renamed to \'{new}\''.format(old=book, new=new)))
                    else:
                        print(_('Rename canceled, choose another bookname!'))
                else:
                    print(_('Rename canceled'))
            else:
                print(_('This book is already in DB, use another book name'))
                Books.list_books()
        else:
            print(_('This book does not exist'))
            Books.list_books()


# ---------------------- Dictionary

class Dictionaries:
    """
    This class provides methods for dictionaries handling
    """

    @staticmethod
    def submenu(choice_name):
        """
        Submenu for Dictionaries
        """

        if choice_name == "ldic":
            return Dictionaries.list_dictionaries()

        if choice_name == "wdic":
            return Words.list_word_from_dic()

        if choice_name == "cdic":
            return Dictionaries.create_dictionary()

        if choice_name == "rdic":
            return Dictionaries.rename_dictionary()

        if choice_name == "ddic":
            return Dictionaries.dell_dictionary()

        return False

    @staticmethod
    def list_dictionaries():
        """
        Print the list of dictionaries
        """
        print(_('\nDictionaries:'))
        for name in db.list_dictionary():
            print('     ', name[0])

    @staticmethod
    def create_dictionary():
        """
        Create new dictionary
        """
        dictionary = input(_('Choose the name for the dictionary: '))
        if not db.check_dictionary_exist(dictionary):
            comment = input(_('Comments: '))
            result = db.create_dictionary(dictionary, comment)
            if result:
                print("Dictionary \'{name}\' has been created!".format(name=dictionary))
            else:
                print("Dictionary \'{name}\' wasn't created!".format(name=dictionary))
        else:
            print('Dictionary \'{name}\' already exists! Please, choose another name '
                  'for dictionary.'.format(name=dictionary))

    @staticmethod
    def dell_dictionary():
        """
        Delete dictionary
        """
        dictionary = input(_('choose the dictionary: '))
        dictionary_id = db.check_dictionary_exist(dictionary)
        if dictionary_id:
            confirm = input(_('Are you sure you want to delete the dictionary? y/n: '))
            if confirm in CONF_LIST:
                result = db.del_dictionary(dictionary_id)
                if result:
                    print(_("Dictionary '{dictionary}' was deleted".format(dictionary=dictionary)))
                else:
                    print(_("Dictionary '{dictionary}' wasn't "
                            "deleted".format(dictionary=dictionary)))
            else:
                print(_('Delete canceled'))
        else:
            print(_("Dictionary '{dictionary}' doesn't exist".format(dictionary=dictionary)))

    @staticmethod
    def rename_dictionary():
        """
        Rename dictionary
        """
        dictionary = input(_('Choose the dictionary:  '))

        if db.check_dictionary_exist(dictionary):
            new = input(_('Choose new name for dictionary:  '))
            if not db.check_dictionary_exist(new):
                confirm = input(_('Are you sure you want to rename the dictionary? y/n:'))
                if confirm in CONF_LIST:
                    result = db.rename_dictionary(dictionary, new)
                    if result:
                        print(_("Dictionary '{old}' renamed "
                                "to '{new}'".format(old=dictionary, new=new)))
                    else:
                        print(_('Rename was canceled, choose another dictionary name!'))
                else:
                    print(_('Rename canceled'))
            else:
                print(_('This dictionary is already in DB, use another dictionary name'))
                Dictionaries.list_dictionaries()
        else:
            print(_('This dictionary doesn\'t exists'))
            Dictionaries.list_dictionaries()


class Words:
    """
    This class provides methods for words handling
    """
    list_length = 5
    list_order = 'quantity'
    name_of_list_order = _('by frequency')
    order_rul = 'DESC'
    dictionary = ''

    instruction = _("""instruction:
Words that were listed above will be listed one by one. You should choose the action: 
        i - add word to 'Ignore'-dictionary (words, you don't want to see next time 
            in processing. 
            Some words that contain mistakes, or you know them, or by any other reasons)
        e - edit the word (add translation, transcription or comments)
        a - add word to dictionary (it will offer to choose the dictionary)
        d - delete the word
        p - skip the word
        q - quit from processing
        h - help \n""")

    @staticmethod
    def submenu(choice_name):
        """
        Submenu for Words
        """
        if choice_name == 'dwd':
            return Words.del_word_from_dic()

        if choice_name == "abook":
            return Words.analyze_book_words()

        if choice_name == "fword":
            return Words.find_word()

        if choice_name == "chword":
            return Words.change_word()

        if choice_name == "a2dic":
            return Words.add_word_2dic()

        return False

    @staticmethod
    def list_word_from_dic():
        """
        Print the list of words in dictionary
        """
        dictionary = ''
        while dictionary == '':
            # Default Dictionary wasn't chosen
            if Words.dictionary == '':
                dictionary = input(_('Type the name of the dictionary: '))
                if db.check_dictionary_exist(dictionary):
                    Words.dictionary = dictionary
                else:
                    print(_("Dictionary '{dictionary}' doesn't exist. Please, choose the "
                            "dictionary".format(dictionary=dictionary)))
                    print(_('List of dictionaries:'))
                    for name in db.list_dictionary():
                        print('     ', name[0])
                    separator4()
                    dictionary = ''
            # Default Dictionary exist
            else:
                print(_("'{default_dictionary}' - dictionary "
                        "by default".format(default_dictionary=Words.dictionary)))
                dictionary = input(_('Inter new name of the dictionary/or leave the field empty: '))
                if dictionary == '':
                    dictionary = Words.dictionary
                else:
                    if db.check_dictionary_exist(dictionary):
                        Words.dictionary = dictionary
                    else:
                        print(_("Dictionary '{dictionary}' doesn't exist. "
                                "Please, choose the "
                                "dictionary".format(dictionary=dictionary)))
                        print(_('List of dictionaries:'))
                        for name in db.list_dictionary():
                            print('     ', name[0])
                        separator4()
                        dictionary = ''

        # Checking the dictionary
        listword = db.select_from_dictionary(dictionary, Words.list_order, Words.order_rul)
        if listword:
            separator4()
            print(_("Dictionary contains {amount} words".format(amount=len(listword))))
            Words.select_number_of_words()
            Words.select_words_order()
            listword = db.select_from_dictionary(dictionary, Words.list_order, Words.order_rul)
            separator4()
            print_words(listword, length=Words.list_length)
        else:
            print("Dictionary is empty")

    @staticmethod
    def select_words_order():
        """
        Set the order of words representation
            * by quantity
            * in alphabeticall order
        """
        print(_('Sort order selected: '), Words.name_of_list_order)
        order = input(_('Do you like to change the sort order? '
                        '(by frequency - f/alphabetically - a): '))
        if order == 'f':
            Words.list_order = 'quantity'
            Words.name_of_list_order = _('by frequency')
            Words.order_rul = 'DESC'
        elif order == 'a':
            Words.list_order = 'front'
            Words.name_of_list_order = _('alphabetically')
            Words.order_rul = 'ASC'
        else:
            pass

    @staticmethod
    def select_number_of_words():
        """
        Set amount of words for representation
            (5 by default)
        """
        number_words_4_processing = _('Choose the number of words that '
                                      'you want to process ({amount} '
                                      'by default): '.format(amount=str(Words.list_length)))
        number = input(number_words_4_processing)
        if number.isdigit():
            Words.list_length = int(number)

    @staticmethod
    def del_word_from_dic(word='', dictionary=''):
        """
        Delete word from dictionary
        """
        if word == '':
            word = input(_('Type the word that you want to delete from dictionary: '))
        if dictionary == '':
            dictionary = input(_('Choose the dictionary: '))

        if db.check_word_exist(word) and db.check_dictionary_exist(dictionary):
            result = db.dell_word_from_dictionary(db.check_dictionary_exist(dictionary),
                                                  db.check_word_exist(word))
            if result:
                print(_("Word '{word}' was successfully deleted from dictionary"
                        " '{dictionary}'!".format(word=word, dictionary=dictionary)))
            else:
                print("Error! The word wasn't deleted")

        elif not db.check_word_exist(word) and not db.check_dictionary_exist(dictionary):
            print(_("Dictionary '{dictionary}' does not exist".format(dictionary=dictionary)))
            print(_("Word '{word}' not exist".format(word=word)))
        elif not db.check_dictionary_exist(dictionary):
            print(_("Dictionary '{dictionary}' does not exist".format(dictionary=dictionary)))
        elif not db.check_word_exist(word):
            print(_("Word '{word}' was not in the dictionary "
                    "'{dictionary}'".format(word=word, dictionary=dictionary)))

    @staticmethod
    def find_word():
        """
        find the word in database - return info
        (in what books and how many times, in what dictionaries)
        """
        word = input(_('Choose the word: '))
        word_id = db.check_word_exist(word)
        if word_id:
            separator4()
            word, books, dictionaries = db.find_word(word_id)
            word = word[0]
            if bool(word):
                printword(word)
            if bool(books):
                print('\n', 10*' ', _('Book'))
                for book in books:
                    print(book[1], (10-len(str(book[1])))*' ', book[0])

            if bool(dictionaries):
                print(_('\nDictionaries:'))
                for dic in dictionaries:
                    print(dic[0])
            else:
                print(_("The word is not included in any dictionary!"))
        else:
            print(_("The word '{word}' doesn't exist!".format(word=word)))

    @staticmethod
    def change_word(word=''):
        """
        change word
        """
        if word == "":
            word = input(_('Change the word: '))
            word_id = db.check_word_exist(word)
            if word_id:
                word = db.find_word(word_id)[0]
                word = word[0]
                front = change_word_function(word=word)
                if front:
                    print(_("Word '{word}' was changed!".format(word=front)))
                else:
                    print(_("Word '{word}' wasn't changed!".format(word=front)))
            else:
                print(_("Word doesn't exist"))
        else:
            print(_("Please print the words you want to change!"))

    @staticmethod
    def add_word_2dic():
        """
        add words to dictionary
        """
        word = input(_('Choose the word: '))
        word_id = db.check_word_exist(word)
        if word_id:
            word = db.find_word(word_id)[0]
            word = word[0]
            add_word_to_dictionary(word=word)
        else:
            print("Word doesn't exist")

    @staticmethod
    def analyze_book_words():
        """
        This method provides words processing from dictionary.
        It download list of words for chosen book from database to the memory,
        and show it by frequency in descending order. User can process the words:
         * add word to Ignor or to other dictionary
         * remove word
         * change the word
         * pass the word

        It is necessary for making your oun dictionary
        """
        book = input(_('Choose the book for processing:  '))
        if db.check_book_exist(book):
            separator4()
            book_list = db.select_book_words_with_condition(book, 'i', 's', 'quantity')
            print(_('Book contain {amount} words'.format(amount=len(book_list))))
            text = _('Please, Choose the number of words that you want to process '
                     '({list_lang} by default): '.format(list_lang=str(Words.list_length)))
            number = input(text)
            if number.isdigit():
                Words.list_length = int(number)
            separator4()
            print_words(book_list, length=Words.list_length)

            separator4()
            print(Words.instruction)
            separator4()
            confirm = input(_('Do you want to start processing the words? y/n: '))
            separator4()
            if confirm in CONF_LIST:
                Words.word_processing(book_list)  # Words.word_processing()

        if not db.check_book_exist(book):
            print("Book '{book}' doesn't exist! "
                  "Please, choose another book!".format(book=book))
            Books.list_books()

    @staticmethod
    def word_processing(book_list):
        """
        function is used for making menu for analyze method
        """
        for word in book_list[0:Words.list_length]:
            printword(word)
            action = 'wait'
            while action != 'p':
                action = input(_('Choose the action: i/e/a/d/p/q/h: '))

                if action == 'i':  # add word to ignore
                    Words.add_word_to_ignore(word=word)

                if action == 'e':  # edit and add to dictionary
                    Words.edit_and_add2dictionary(word=word)
                    break

                if action == 'a':  # Add to dictionary
                    add_word_to_dictionary(word=word)
                    break

                if action == 'd':  # Delete word from words
                    Words.delete_word_from_words(word=word)
                    break

                if action == 'p':  # pass the word
                    pass

                if action == 'q':  # quit from circle
                    break

                if action == 'h':  # print instruction
                    print(Words.instruction)

                if action not in ('i', 'e', 'a', 'd', 'p', 'q', 'h'):  # wrong action
                    print(Words.instruction)
                    print(_('Pleas Choose the action!'))

            if action == 'q':  # exit from analyze
                break

    @staticmethod
    def edit_and_add2dictionary(word):
        """
        function is used in analyze method
        """
        change_word_function(word=word)
        to_dictionary = input("Would you like to add the word to "
                              "the dictionary? y/n: ")
        if to_dictionary in CONF_LIST:
            add_word_to_dictionary(word=word)

    @staticmethod
    def delete_word_from_words(word):
        """
        function is used in analyze method
        """
        word_id = db.check_word_exist(word[0])
        if db.del_word_from_words(word_id):
            print(_("Word '{word}' was deleted "
                    "successfully!".format(word=word[0])))
        else:
            print(_('Delete was canceled'))

    @staticmethod
    def add_word_to_ignore(word):
        """
        function is used in analyze method
        """
        ignore = False
        for dictionary in db.list_dictionary():
            if dictionary[0] == 'Ignore':
                ignore = True
                break
            else:
                ignore = False

        if ignore:
            print(_('The word was added to the dictionary Ignore!'))
            db.addword_2_dictionary('Ignore', word[0])
            separator4()
        else:
            print(_('The dictionary "Ignore" had been created. '
                    'The word was added to the dictionary!'))
            db.create_dictionary('Ignore', 'You can add all words for IGNORE '
                                           'into this dictionary')
            db.addword_2_dictionary('Ignore', word[0])
            separator4()


# ------------------------------------------------------ functions


def add_word_to_dictionary(word):
    """
    Function adds words to the dictionary
    this function is used in class Words, methods:
     * analyze_book_words
     * add_word_2dic
    """
    separator4()
    print(_('List of dictionaries: '))
    for name in db.list_dictionary():
        print('     ', name[0])
    dictionary = input(_('Choose the dictionary: '))
    if db.check_dictionary_exist(dictionary):
        db.addword_2_dictionary(dictionary, word[0])
        print(_("The word '{word}' was successfully added to the dictionary!".format(word=word[0])))
        separator4()
    else:
        print(_("Dictionary doesn't exist. Please check spelling!"))


def change_word_function(word):
    """
    Function adds words to the dictionary
    this function is used in class Words, methods:
     * analyze_book_words
     * change_word_function
    """
    separator4()
    printword(word)
    separator4()

    front = input(_('Change spelling: '))
    transcription = input(_('Add/Change transcription: '))
    translation = input(_('Add/Change translation: '))
    comments = input(_('Add/Change the comment: '))
    separator4()

    if front == "":
        front = word[0]
    else:
        pass

    word1 = [front, transcription, translation, word[3], word[4], word[5]]

    print(_('New word: '))
    printword(word1)

    separator4()
    save = input(_('Save word  y/n: '))
    if save in CONF_LIST:
        db.change_word(word[0], front=front, translation=translation,
                       transcription=transcription, comments=comments)
        print(_("The word '{word}' was changed!".format(word=word[0])))
    else:
        print(_("The changing of word '{word}' was canceled!".format(word=word[0])))

    return front


def printword(word):
    """
    Used for printing Word with Frequency, Transcription and Translation
    """
    if LANG[0] == 'en':
        print('Frequency' + 16 * ' ' + 'Word' + 21 * ' ' + 'Transcription' + 12 * ' '
              + 'Translation')
    elif LANG[0] == 'ru':
        print('Встречается(раз)' + 9 * ' ' + 'Слово' + 20 * ' ' + 'Транскрипция' + 13 * ' '
              + 'Перевод')
    else:
        print('Frequency' + 9 * ' ' + 'Word' + 20 * ' ' + 'Transcription' + 13 * ' '
              + 'Translation')

    print(word[5], (23 - len(str(word[5]))) * ' ', word[0], (23 - len(str(word[0]))) * ' ',
          word[1], (23 - len(str(word[1]))) * ' ', word[2])


def print_words(words_list, length=5):
    """
    Used for printing table of Words with Frequency, Transcription and Translation
    """
    if LANG[0] == 'en':
        print('Frequency' + 16 * ' ' + 'Word' + 21 * ' ' + 'Transcription' + 12 * ' '
              + 'Translation')
    elif LANG[0] == 'ru':
        print('Встречается(раз)' + 9 * ' ' + 'Слово' + 20 * ' ' + 'Транскрипция' + 13 * ' '
              + 'Перевод')
    else:
        print('Frequency' + 9 * ' ' + 'Word' + 20 * ' ' + 'Transcription' + 13 * ' '
              + 'Translation')

    for word in words_list[0:length]:
        print(word[5], (23 - len(str(word[5]))) * ' ', word[0], (23 - len(str(word[0]))) * ' ',
              word[1], (23 - len(str(word[1]))) * ' ', word[2])


def separator4():
    """
    Used for print ---- separator
    """
    print(4 * '-')

# ---------------------------------------- Exit & Help


class Help:
    """
    Help information
    """
    @staticmethod
    def submenu(choice_name):
        """
        Submenu for Help
        """
        if choice_name == "h":  # format database (remove all data and create new tables)
            return Help.print_help()

        # if choice_name == "i":  # format database (remove all data and create new tables)
        #     return Help.instruction()

        return False

    @staticmethod
    def print_help():
        """
        Print Help information
        """
        if sys.platform == 'linux':
            webbrowser.open_new("file://" + BASEPATH + "/Documentation/build/html"
                                                       "/program_documentation.html")
        elif sys.platform == 'windows':
            print('win32')

        # short_help = "Documentation/source/help.rst"    # "settings/help.txt"
        # description = "Documentation/source/description.rst"
        # next_step = None
        # while next_step != "q":
        #     if next_step == 'i':
        #         data = description
        #     else:
        #         data = short_help
        #
        #     file = open(data, 'r')
        #     file_data = file.read()
        #     print(file_data)
        #     file.close()
        #
        #     next_step = input(_('instructions: i , quit - q '))

    @staticmethod
    def instruction():
        """
        Print the instruction how to use the program
        """
        if sys.platform == 'linux':
            webbrowser.open_new("file://"+BASEPATH + "/Documentation/build/html"
                                                     "/program_documentation.html")
        elif sys.platform == 'windows':
            print('windows')


class Misc:
    """
    Additional methods for menu
    """

    @staticmethod
    def submenu(choice_name):
        """
        Submenu for Misc
        """
        if choice_name == "lang":  # format database (remove all data and create new tables)
            return Misc.language()

        if choice_name == "format":  # format database (remove all data and create new tables)
            return Database.format()

        if choice_name == "aw":  # import words from Anki
            return Database.import_f_anki()

        if choice_name == "q":  # Exit
            return Misc.exit()

        return False

    @staticmethod
    def exit():
        """
        See in the main circle
        """

    @staticmethod
    def wrong_choice():
        """
        Print response in case of wrong choice in menu
        """
        print(_("You entered command that doesn't exist. \nPlease enter h for help"))

    @staticmethod
    def language():
        """
        Method for changing language of user interface
        """
        print(_('Current language: English'))
        separator4()


if __name__ == '__main__':
    print('выполнено')
