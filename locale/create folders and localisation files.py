import os, sys
from settings.setting import BASEPATH, LANGUAGES

def create_dir():
    for language in LANGUAGES:
        path = BASEPATH +'/locale/'+language+'/LC_MESSAGES'

        try:
            os.makedirs(path)
            print(path, ' --> created')
        except:
            print("Directory ", path, " -- already exist! \n")


def create_pop_files(lang_list):
    for language in LANGUAGES:
        if language in lang_list:
            os.chdir(BASEPATH)
            command = 'xgettext -j -o ./locale/' + language + '/LC_MESSAGES/main.pot main.py' # for Book_vocabularry_to_Anki
            os.system(command)

            os.chdir(BASEPATH + '/libraries')
            #print(os.getcwd())
            command = 'xgettext -j -o ../locale/'+ language +'/LC_MESSAGES/main.pot menue_lib.py' # for menue_lib
            os.system(command)

            command = 'xgettext -j -o ../locale/'+ language +'/LC_MESSAGES/main.pot db_lib.py' # for db_lib
            os.system(command)

            print(language, ' - has been created')
        else: print('{language} - already exist'.format(language=language))


def create_mo_files():
    for language in LANGUAGES:
        if language != '':
            path = BASEPATH + '/locale/' + language + '/LC_MESSAGES'
            os.chdir(path)
            print(os.getcwd())
            command = 'msgfmt -o main.mo main'
            os.system(command)

            print(language, ' - has been created')




if __name__ == '__main__':
    # create_dir()
    # create_pop_files(['ru',])
    create_mo_files()