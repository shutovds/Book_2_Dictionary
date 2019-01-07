# This Python file uses the following encoding: utf-8

"""
Main
"""

import gettext
from libraries import menue_lib as menue

CHOICE = ""


def choose_language():
    """
    function for choosing language
    """
    global LANG
    global _
    print("""Now you can choose_from_menu your language:
    Chinese    - zh  中文
    English    - en
    Japanese   - ja  日本語
    Panjabi    - pa  ਪੰਜਾਬੀ
    Persian    - pe  فارسی
    Russian    - ru  Русский
    Spanish    - es  Español
    Urdu       - ur  اُردو
(for example if you want English - type: en)
    """)

    chosen_lang = input('Please type: ')

    if chosen_lang == 'zh':
        LANG = 'zh'
    elif chosen_lang == 'en':
        LANG = 'en'
    elif chosen_lang == 'ja':
        LANG = 'ja'
    elif chosen_lang == 'pa':
        LANG = 'pa'
    elif chosen_lang == 'pe':
        LANG = 'pe'
    elif chosen_lang == 'ru':
        LANG = 'ru'
    elif chosen_lang == 'es':
        LANG = 'es'
    elif chosen_lang == 'ur':
        LANG = 'ur'
    else:
        LANG = 'en'
        print("Language {lang} doesn't exist in the system! "
              "\nEnglish has been set up for interface."
              "\nIf you want to change language use 'lang' command ".format(lang=chosen_lang))

    menue.chang_lang(LANG)
    language = gettext.translation('main', languages=[LANG], localedir='./locale')
    _ = language.gettext
    language.install()


print("Hello! We are glad to work with you!")
choose_language()
print(_(menue.MAIN_INSTRUCTION))

while CHOICE != 'q':
    CHOICE = input(_('\nAction =  '))
    # menue.chang_lang(LANG)
    menue.choose_from_menu(choice=CHOICE)

    if CHOICE == 'q':
        print(_('Thank you for being with us!'))
    elif CHOICE == 'lang':
        choose_language()
    print('-' * 20)


if __name__ == '__main__':
    pass
