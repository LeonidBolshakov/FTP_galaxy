from re import match
from constant import const as C


def is_eq_name(tuple1: tuple, tuple2: tuple) -> bool:
    """Функция is_eq_name(tuple1: tuple, tuple2: tuple) -> bool
        сравнивает равны ли постоянные части имён компонентов
        (имя компонента и расширение). Номера версий не сравниваются.

    Аргументы:
         tuple1 (tuple): кортеж имени компонента (имя, версия, расширение файла),
         tuple2 (tuple): кортеж имени компонента (имя, версия, расширение файла).

    Возвращает:
         bool: True если постоянные части имён совпадают, иначе - False.
    """

    return tuple1[0] == tuple2[0] and tuple1[2] == tuple2[2]


def name_to_tuple(name: str) -> tuple[str, str, str] | None:
    """Функция name_to_tuple(name: str) -> tuple[str, str, str]
        разбивает имя файла компонента на 3 части:
        (имя компонента, номер версии, расширение файла)
    :param name: str - имя файла компонента
    :return: (имя компонента, номер версии, расширение файла).
    Если имя файла компонента не соответствует структуре имени компонента, то None
    """

    res_match = match(C.RE_PATTERN_NAME_COMPONENT, name)
    if not res_match:
        return None
    if not res_match.group(1):
        return None
    if not res_match.group(2):
        return None
    if not res_match.group(3):
        return None
    return res_match.group(1), res_match.group(2), res_match.group(3)


def reset_component_version(name_file: str) -> str:
    name_tuple = name_to_tuple(name_file)
    if name_tuple:
        name = name_tuple[0] + C.ZERO_VERSION + name_tuple[2]
    else:
        name = name_file
    return name
