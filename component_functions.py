from pathlib import Path
from re import match

from constant import const as C


class MyException(Exception):
    def __init__(self, text_err, ret_code):
        self.text_err = text_err
        self.ret_code = ret_code


def is_eq_name(tuple1: tuple, tuple2: tuple) -> bool:
    """Функция is_eq_name(tuple1: tuple, tuple2: tuple) -> bool
        сравнивает равны ли постоянные части имён компонентов
        (имя компонента и расширение). Номера версий не сравниваются.

    Аргументы:
         tuple1 (tuple): кортеж имени компонента (имя, версия, расширение файла).
         tuple2 (tuple): кортеж имени компонента (имя, версия, расширение файла).

    Возвращает:
         bool: True если постоянные части имён совпадают, иначе - False.
    """

    return tuple1[0] == tuple2[0] and tuple1[2] == tuple2[2]


def name_to_tuple(name: str) -> tuple[str, str, str] | None:
    """Функция name_to_tuple(name: str) -> tuple[str, str, str]
        разбивает имя файла компонента на 3 части.
        (имя компонента, номер версии, расширение файла).
    :param name: str - имя файла компонента.
    :return: (имя компонента, номер версии, расширение файла).
    Если имя файла компонента не соответствует структуре имени компонента, то None.
    """

    res_match = match(C.RE_PATTERN_NAME_COMPONENT, name)
    if not res_match:
        return None
    for i in range(1, 4):
        if not res_match.group(i):
            return None
    return res_match.group(1), res_match.group(2), res_match.group(3)


def reset_component_version(name_file: str) -> str:
    """Функция reset_component_version(name_file: str) -> str:
        устанавливает у имени компонента нулевую версию.

    :param name_file: Str - имя файла компонента.
    :return: (имя компонента, '00000', расширение файла)
    Если имя файла компонента не соответствует структуре имени компонента,
    то возвращается имя файла в исходном виде.
    """
    name_tuple = name_to_tuple(name_file)
    if name_tuple:
        name = name_tuple[0] + C.ZERO_VERSION + name_tuple[2]
    else:
        name = name_file
    return name


def confirm_if_needed(dir_: Path) -> None:
    """
    :Назначение
        Функция проводит проверку директории и при необходимости устраняет проблему.
    :param dir_:Path. Проверяемая директория.
    :return: Нет.
    """
    if any(dir_.iterdir()):
        answer = dialog(f"{dir_}. {C.TEXT_1}", ["н", "п"])
        if answer == "н":
            delete_all(dir_)
        print("Продолжаем работать")

    return


def dialog(text: str, answers: list[str]) -> str:
    """Функция организует диалог с пользователем.
        Функция не выпустит пользователя,
        пока он не выберет один из допустимых вариантов ответов.
    Параметры:
        text: str - Текст запроса пользователя.
        answers: list[str] - Список допустимых ответов.
    Результат: str - допустимый ответ.
    """
    answer = ""
    while answer not in (element for element in answers):
        answer = input(text).lower()
    return answer


def delete_all(dir_: Path) -> None:
    """Функция удаляет всё содержимое директории.
        delete_all
    Аргумент:
        dir_: Path - Директория, из которой удаляется содержимое.
    """
    try:
        for item in dir_.iterdir():
            if item.is_dir():
                delete_all(item)  # рекурсивно удаляем подкаталоги
                item.rmdir()
            else:
                item.unlink()
    except Exception as e:
        raise MyException(f"\nНе удалось удалить фвайлы из директории {dir_}\n")
