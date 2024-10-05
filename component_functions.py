from re import match
from constant import const as C
from pathlib import Path
import logging


class MyException(Exception):
    def __init__(self, text_err, ret_code):
        self.text_err = text_err
        self.ret_code = ret_code


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
    for i in range(1, 4):
        if not res_match.group(i):
            return None
    return res_match.group(1), res_match.group(2), res_match.group(3)


def reset_component_version(name_file: str) -> str:
    """Функция reset_component_version(name_file: str) -> str:
        устанавливает у имени компонента нулевую версию

    :param name_file: Str - имя файла компонента
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


def rename_subdir(subdir: Path) -> None:
    """
    Функция rename_subdir(subdir: Path) -> None:
        Переименовывает входную директорию (subdir) в директорию с именем subdir_N,
        где N - номер версии директории.
    :param subdir: Path
    :return: None
    """
    if not subdir.exists(follow_symlinks=False):
        return

    num_subdir = 0
    while True:
        num_subdir += 1
        if 9 < num_subdir:
            logging.warning(f"Накопилось более 9 версий поддиректории {subdir}")
        dir_new = Path(str(subdir.parent), subdir.name + "_" + str(num_subdir))

        if not dir_new.exists():
            break
    try:
        subdir.rename(dir_new)
    except Exception as err:
        raise MyException(
            f"Не могу переименовать директорию: {subdir}, \n" f"Ошибка {err}", 777
        )


rename_subdir(Path(r"C:\Дистрибутив\DESCRIPTIONS\NEW"))
