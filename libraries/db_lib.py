# This Python file uses the following encoding: utf-8

"""
This module includes all classes for processing database requests:
"""

import re
import sqlite3
import time

from functools import wraps


# decorator for connection to DB
def connection_to_db(func):
    """
    This decorator provides connection to database for all functions and close connection after
    function made requests
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper
        """
        db_name = './settings/objects.sqlite'
        conn = sqlite3.connect(database=str(db_name))
        cur = conn.cursor()

        result = func(cur, *args, **kwargs)

        cur.close()
        conn.commit()
        conn.close()
        return result

    return wrapper


@connection_to_db
def create_new_tables(cur):
    """Create next tables:
     * Anki - contain words imported from Anki
     * Book - contain imported book: text and name
     * BookToWord - set connection for book name, word and frequency, provide many to many
     relation for tables Book и Words
     * Words - contain imported words from all books
     """
    try:
        cur.executescript('''
        DROP TABLE IF EXISTS Anki;
        DROP TABLE IF EXISTS Book;
        DROP TABLE IF EXISTS BookToWord;
        DROP TABLE IF EXISTS StopWords;
        DROP TABLE IF EXISTS Words;
        DROP TABLE IF EXISTS Dictionaries;
        DROP TABLE IF EXISTS DictionariesToWord
        ''')

        cur.executescript('''
        CREATE TABLE Anki(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                front TEXT NOT NULL,
                transcription TEXT,
                translation TEXT,
                sound TEXT,
                example TEXT,
                synonim TEXT
            );
        CREATE TABLE Book(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                book_name TEXT UNIQUE NOT NULL,
                import_date_time TEXT,
                author TEXT,
                text TEXT,
                comment TEXT
            );
        
        CREATE TABLE BookToWord(
                book_id INTEGER NOT NULL,
                word_id INTEGER NOT NULL,
                quantity INTEGER, /* TEXT */ 
                PRIMARY KEY(book_id, word_id)
            );
            
        /* в таблицу Words было добавлено поле condition  */      
        /* CREATE TABLE StopWords(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                front TEXT UNIQUE NOT NULL,
                comment TEXT 
            ); */
        
        CREATE TABLE Words(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                front TEXT UNIQUE NOT NULL,
                transcription TEXT,
                translation TEXT,
                comments TEXT,
                condition TEXT, /* Already studed, studing, ignore, etc */
                part_of_speech_tag TEXT
            );
        
        CREATE TABLE Dictionaries(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                dic_name TEXT UNIQUE NOT NULL,
                creation_date_time TEXT,
                comment TEXT
            );
        
        /* Dictionaries connected to Words and to Books */
        CREATE TABLE DictionariesToWord(
                dictionary_id INTEGER NOT NULL,
                word_id INTEGER NOT NULL,
                orders TEXT, /* порядковый номер слова в словаре */
                PRIMARY KEY(dictionary_id, word_id)
            );
        ''')

        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def anki_t_db(cur, *args):
    """
    Import data from Anki dictionary to table Anki DB
    """

    rows = args[0]

    try:
        cur.executescript('delete from Anki')  # очищаем таблицу
        i = 0
        for rec in rows:
            i += 1
            rec = [str(i)] + rec
            if len(rec) < 7:
                rec = rec + list(' ' * (7 - len(rec)))
            elif len(rec) > 7:
                rec = rec[:7]

            cur.execute('''INSERT OR IGNORE INTO Anki VALUES (?,?,?,?,?,?,?)''', rec)
        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def book_t_db(cur, *args):
    """
    Import book from txt file to table Book DB
    """

    path = args[0]
    book_name = args[1]

    try:
        file = open(path, 'r')
        text = file.read()
        file.close()
    except FileNotFoundError:
        return False

    try:
        cur.execute('''INSERT OR IGNORE INTO Book (book_name, text)
                       VALUES (?,?)''', (book_name, text))
        return True
    except sqlite3.DatabaseError:
        return False


class Words:
    """
    Create the dictionary of words for import words to DB
    """
    def __init__(self, word):
        self.word = word
        self.frequency = 1

    def set_to_dictionary(self, dictionary):
        """
        Create the dictionary
        """
        if self.word in dictionary:
            self.frequency = dictionary[self.word][0] + 1

        dictionary[self.word] = [self.frequency, ]

    def length_of_dictionary(self):
        """
        Count length of the word
        """
        result = self.word
        return len(result)


@connection_to_db
def words_from_book_2db(cur, *args):
    """
    Function provides export from book to database

    #. download text from table Book dictionary for processing
    #. calculation the frequency for words in the book
    #. deletion words repetitions
    #. saving words to table Words and set relation in table BookToWord

    """

    book_name = args[0]

    try:
        # obtaining text from DB
        # creating the dictionary based on the text
        cur.execute('''SELECT text FROM Book WHERE book_name = ?''', (book_name,))
        text = cur.fetchall()[0][0]
        words = re.split(r'\W+|\d+', text.lower())
        worddic = {}
        for word in words:
            if word != "":
                inst = Words(word)
                inst.set_to_dictionary(worddic)

        # downloading words from DB Words, creating the list of words
        cur.execute('''SELECT front FROM Words''')
        allwords = cur.fetchall()
        list_allwords = []
        for word in allwords:
            list_allwords.append(word[0])

        # obtaining Book ID
        cur.execute('SELECT id FROM Book WHERE book_name = ? ', (book_name,))
        book_id = cur.fetchone()[0]

        # comparing list from Book with list words from DB and changing data in DB
        for key in worddic:

            if key in list_allwords:
                #  word already in DB table Words
                cur.execute('SELECT id FROM Words WHERE front = ? ', (key,))
                word_id = cur.fetchone()[0]
                cur.execute('INSERT OR IGNORE INTO BookToWord (book_id, word_id, quantity) '
                            'VALUES (?,?,?)',
                            (book_id, word_id, worddic[key][0]))
            else:
                # word not yet in DB table Words
                cur.execute('INSERT OR IGNORE INTO Words (front) VALUES (?)', (key,))
                cur.execute('SELECT id FROM Words WHERE front = ? ', (key,))
                word_id = cur.fetchone()[0]
                cur.execute('INSERT OR IGNORE INTO BookToWord (book_id, word_id, quantity) '
                            'VALUES (?,?,?)',
                            (book_id, word_id, worddic[key][0]))

        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def create_dictionary(cur, *args):
    """
    Create new user dictionary
    """

    dictionary = args[0]
    comment = args[1]

    creation_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    try:
        cur.execute('INSERT OR IGNORE INTO  Dictionaries (dic_name, creation_date_time, comment) '
                    'VALUES(?,?,?)', (dictionary, creation_date, comment))
        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def addword_2_dictionary(cur, *args):
    """
    Add new word to dictionary
    """

    dictionary = args[0]
    word = args[1]

    try:
        cur.execute('SELECT id FROM Dictionaries WHERE dic_name = ?', (dictionary,))
        dictionary_id = cur.fetchone()[0]

        cur.execute('SELECT id FROM Words WHERE front = ?', (word,))
        word_id = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM DictionariesToWord')
        orders = cur.fetchone()[0]

        cur.execute('INSERT OR IGNORE INTO DictionariesToWord (dictionary_id, word_id, orders) '
                    'VALUES (?,?,?)', (dictionary_id, word_id, orders))

        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def check_word_exist(cur, *args):
    """
    Select that word exist
    word = args[0]
    """

    try:
        cur.execute('SELECT id FROM Words WHERE front = ?', (args[0],))
        return cur.fetchone()[0]

    except (sqlite3.DatabaseError, TypeError):
        return None


@connection_to_db
def check_book_exist(cur, *args):
    """
    Select that book exist
    book = args[0]
    """

    try:
        cur.execute('SELECT id FROM Book WHERE book_name = ?', (args[0],))
        return cur.fetchone()[0]

    except (sqlite3.DatabaseError, TypeError):
        return None


@connection_to_db
def check_dictionary_exist(cur, *args):
    """
    Select that dictionary exist
    dictionary = args[0]
    """

    try:
        cur.execute('SELECT id FROM Dictionaries WHERE dic_name = ?', (args[0],))
        return cur.fetchone()[0]

    except (sqlite3.DatabaseError, TypeError):
        return None


@connection_to_db
def dell_word_from_dictionary(cur, *args):
    """
    Delete word from dictionary
    """

    dictionary_id = args[0]
    word_id = args[1]

    try:
        cur.execute('DELETE FROM DictionariesToWord '
                    'WHERE word_id=? '
                    'AND dictionary_id=?', (word_id, dictionary_id))
        return word_id

    except sqlite3.DatabaseError:
        return None


# ------------------------------------------------------------------ Редактирование:
@connection_to_db
def change_word(cur, *args, **kwargs):
    """
    Function provides changing the word
    Fields that are possible to add

    * front
    * transcription
    * translation
    * comments
    * condition

    """

    word = args[0]

    cur.execute('SELECT id, front, transcription, translation, comments, condition '
                'FROM Words '
                'WHERE front = ?', (word,))
    value = cur.fetchone()
    word_id = value[0]
    value = value[1:]
    key = ('front', 'transcription', 'translation', 'comments', 'condition')
    data = dict(zip(key, value))

    for k in key:
        try:
            data[k] = kwargs[k]
        except IndexError:
            pass
        try:
            cur.execute('UPDATE Words '
                        'SET front = ?, transcription = ?, translation = ?, comments = ?, '
                        'condition = ? '
                        'WHERE id = ?',
                        (data['front'], data['transcription'], data['translation'],
                         data['comments'], data['condition'], word_id,))
            return True
        except sqlite3.DatabaseError:
            return False


@connection_to_db
def rename_book(cur, *args):
    """
    Rename the book
    """

    book_name = args[0]
    new_name = args[1]

    try:
        cur.execute('UPDATE Book SET book_name = ? '
                    'WHERE book_name = ?', (new_name, book_name,))
        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def rename_dictionary(cur, *args):
    """
    Rename the dictionary
    """

    dictionary = args[0]
    new_name = args[1]

    try:
        cur.execute('UPDATE Dictionaries SET dic_name = ? '
                    'WHERE dic_name = ?', (new_name, dictionary,))
        return False
    except sqlite3.DatabaseError:
        return True


@connection_to_db
def list_dictionary(cur=None):
    """
    Return list of existed dictionaries
    """
    try:
        cur.execute('SELECT dic_name FROM Dictionaries')
        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def list_books(cur=None):
    """
    Function return the list of books in database
    """
    try:
        cur.execute('SELECT book_name, id, SUM(quantity) '
                    'FROM Book, BookToWord '
                    'WHERE BookToWord.book_id = Book.id '
                    'GROUP BY BookToWord.book_id')

        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def del_word_from_words(cur, *args):
    """
    Remove word from table Words and connected tables
    """

    word_id = args[0]

    try:
        cur.execute('DELETE FROM Words '
                    'WHERE id = ?', (word_id,))
        cur.execute('DELETE FROM DictionariesToWord '
                    'WHERE word_id=?', (word_id,))
        cur.execute('DELETE FROM BookToWord '
                    'WHERE word_id=?', (word_id,))
        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def del_book(cur, *args):
    """
    Delete book from Database the table Book and connected tables
    (also delete the text of the book)
    """
    # /todo add words delete from the table Words if they are not in existing books

    book_id = args[0]

    try:
        cur.execute('DELETE '
                    'FROM Book '
                    'WHERE id = ?', (book_id,))
        cur.execute('DELETE '
                    'FROM BookToWord '
                    'WHERE book_id=?', (book_id,))
        return True
    except sqlite3.DatabaseError:
        return False


@connection_to_db
def del_dictionary(cur, *args):
    """
    Remove the dictionary from table Dictionaries and connected tables
    (слова входившие в dictionary остаются в таблице Words до тех пор пока не будет удалена книга
    либо они не будут удалены индивидуально)
    """

    dictionary_id = args[0]

    try:
        cur.execute('DELETE '
                    'FROM Dictionaries '
                    'WHERE id = ?', (dictionary_id,))
        cur.execute('DELETE '
                    'FROM DictionariesToWord '
                    'WHERE dictionary_id=?', (dictionary_id,))
        return True
    except sqlite3.DatabaseError:
        return False


# Отображение:


@connection_to_db
def select_from_dictionary(cur, *args):
    """
    Return words from dictionary

    * dictionary="DictionarryName",
    * order_field='quantity',
    * order='DESC'

    """

    dictionary = args[0]
    order_field = args[1]
    order = args[2]

    try:
        sql_expression = 'SELECT front, transcription, translation, comments, condition, ' + \
                         'SUM(quantity) ' + \
                         'FROM Words, Dictionaries, DictionariesToWord, BookToWord ' + \
                         'WHERE Dictionaries.dic_name = ? ' + \
                         'AND DictionariesToWord.dictionary_id = Dictionaries.id ' + \
                         'AND Words.id = DictionariesToWord.word_id ' + \
                         'AND BookToWord.word_id = Words.id ' + \
                         'GROUP BY BookToWord.word_id ' + \
                         'ORDER BY ' + order_field + ' ' + order

        cur.execute(sql_expression, (dictionary,))
        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def select_words_by_condition(cur, *args):
    """
    Return the words with condition mark from Words table
    s - studded   condition='s'
    i - ignore
    """
    condition = args[0]

    try:
        cur.execute('SELECT front, transcription, translation, comments, condition '
                    'FROM Words '
                    'WHERE Words.condition = ?', (condition,))
        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def select_book_words_with_condition(cur, *args):
    """
    Return the list of the words based on the Book (in frequency order, except Ignore)
    """

    book_name = args[0]
    condition1 = args[1]
    condition2 = args[2]
    # order = args[3]

    try:
        cur.execute('SELECT front, transcription, translation, comments, condition, quantity '
                    'FROM Book, Words, BookToWord '
                    'WHERE BookToWord.book_id = Book.id '
                    'AND Words.id = BookToWord.word_id '
                    'AND Words.id NOT IN (SELECT word_id FROM DictionariesToWord) '
                    'AND Book.book_name = ? '
                    'AND (Words.condition IS NULL OR Words.condition <> ?) '
                    'AND (Words.condition IS NULL OR Words.condition <> ?) '
                    'ORDER BY quantity DESC', (book_name, condition1, condition2,))

        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def select_dictionary_words_with_condition(cur, *args):
    """
    Выводим список слов на основе словаря
    отсеиваем слова по:

    * condition1='i'
    * condition2='s'

    упорядочиваем по убыванию:
    * order='quantity'
    """

    dictionary = args[0]  # "DictionarryName"
    condition1 = args[1]  # '',
    condition2 = args[2]  # '', \
    # order = args[3]       # 'quantity'

    try:
        cur.execute('SELECT front, transcription, translation, comments, condition, quantity '
                    'FROM Dictionaries, Words, DictionariesToWord, BookToWord '
                    'WHERE DictionariesToWord.dictionary_id = Dictionaries.id '
                    'AND Words.id = DictionariesToWord.word_id '
                    'AND Dictionaries.dic_name = ? '
                    'AND (Words.condition IS NULL OR Words.condition <> ?)'
                    'AND (Words.condition IS NULL OR Words.condition <> ?)'
                    'AND BookToWord.word_id = Words.id '
                    'ORDER BY quantity DESC', (dictionary, condition1, condition2,))

        return cur.fetchall()
    except sqlite3.DatabaseError:
        return None


@connection_to_db
def select_all_words_with_condition(cur, *args):
    """
    Return the list of words from DB Words table (except Ignore)
    """

    # book_name = args[0]
    condition = args[1]    # 'i'
    order_field = args[2]  # 'quantity',
    order = args[3]        # 'DESC'

    try:
        sql_expression = 'SELECT front, transcription, translation, comments, ' + \
                         'condition, quantity ' + \
                         'FROM Words, BookToWord ' + \
                         'WHERE BookToWord.word_id = Words.id ' + \
                         'AND (Words.condition IS NULL OR Words.condition <> ?) ' + \
                         'ORDER BY ' + order_field + ' ' + order

        cur.execute(sql_expression, (condition,))
        return cur.fetchall()
    except sqlite3.DatabaseError:
        return cur.fetchall()


@connection_to_db
def find_word(cur, *args):
    """
    Return info about word
    """

    word_id = args[0]

    try:
        cur.execute('SELECT front, transcription, translation, comments, condition, SUM(quantity) '
                    'FROM Words, BookToWord '
                    'WHERE Words.id = ? '
                    'AND BookToWord.word_id = Words.id', (word_id,))
        word = cur.fetchall()

        cur.execute('SELECT book_name, quantity FROM BookToWord, Book '
                    'WHERE BookToWord.word_id = ? '
                    'AND Book.id = BookToWord.book_id', (word_id,))
        books = cur.fetchall()

        cur.execute('SELECT dic_name FROM DictionariesToWord, Dictionaries '
                    'WHERE DictionariesToWord.word_id = ? '
                    'AND Dictionaries.id = DictionariesToWord.dictionary_id', (word_id,))
        dictionaries = cur.fetchall()
    except sqlite3.DatabaseError:
        word = []
        books = []
        dictionaries = []

    return word, books, dictionaries


if __name__ == '__main__':
    pass
    # create_new_tables()
    # anki_t_db()
    # book_t_db(book_name="book_textfile1")
    # words_from_book_2db(book_name="book_textfile1")
    # create_dictionary()
    # list_dictionary()
    # addword_2_dictionary(word="a")
    # del_word_from_words(word='rat')
    # rename_dictionary(dictionary='sdfgsef', new_name='MyDictionarry')
    # del_book()
    # del_dictionary()
    # select_from_dictionary()
    # select_words_by_condition(condition = 's')
    # select_book_words_with_condition()
    # select_all_words_with_condition()
    # rename_book(book_name="NewBookName", new_name="BookName")
    # change_word_function(word='door', translation='дверь', transcription='[door]')
    # dell_word_from_dictionary(word='the')
    # select_dictionary_words_with_condition(condition1='i', condition2='s')
    # rename_book(book_name="Harry Harrison", new_name="Harry Harrison")

    # print(check_book_exist('Little_Prince'))
    # print(check_dictionary_exist('New'))
    #
    # if check_word_exist('ands'):
    #     print('exist')
    # else:
    #     print('not exist')
    #
    # dell_word_from_dictionary('and', 'New')
