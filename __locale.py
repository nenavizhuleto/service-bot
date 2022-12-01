import keyboards
from __struct import Struct
from collections import namedtuple
from types import SimpleNamespace
import json


class Locale:

    

    def Get(language) -> None:

        locale = None
        with open(f'locale/{language.lower()}.json', 'r', encoding='UTF-8') as file:
            locale = json.load(file, object_hook=lambda d: Locale.__parse(d), )

        if locale is None:
            raise Exception('Couldn\'t load locale file!')

        locale.language = language

        

        return locale
        

    def __parse(obj: dict):
        if 'keyboard' in obj.keys():
            v = vars(obj['keyboard'])
            obj['keyboard'] = keyboards.make_kb(v)
        return SimpleNamespace(**obj)

