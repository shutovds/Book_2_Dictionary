import os, sys

BASEPATH = os.path.dirname(os.path.dirname(__file__))
LANGUAGES = ['en',
             'zh',
             'ja',
             'pa',
             'pe',
             'ru',
             'es',
             'ur']

LANG = ['en']

DbName = '../settings/objects.sqlite'
AnkiFile = '../Anki/FromAnki.txt'
BookFile = '../Books/book_textfile.txt'


if __name__ == '__main__':
    print('basepath is: ', BASEPATH)