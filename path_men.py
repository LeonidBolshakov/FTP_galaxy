from sys import exit, argv
from pathlib import Path
import logging
import component_functions as f
import constant as C  # Константы


class MyException(Exception):
    def __init__(self, text_err, return_code):
        self.text_err = text_err
        self.return_code = return_code


def main_() -> None:
    """ Функция main() -> None
            Обрабатывает прерывания сгенерированные в функции main_
    """

    file_log = logging.FileHandler('Log_path.log')
    console_log = logging.StreamHandler()

    logging.basicConfig(level=logging.INFO, handlers=(file_log, console_log),
                        format="%(asctime)s %(levelname)s %(message)s")

    try:
        main()
    except MyException as e:
        logging.error(e.text_err)
        exit(e.return_code)
    except Exception as e:
        logging.critical(f'Непредвиденная ошибка\n{e}')


def main() -> None:
    """ Функция main_() -> None
            Для всех компонентов, имеющих одинаковые имена компонента и расширения файла,
            перемещает в директорию OLD компоненты с более ранней версией.
            В результате в директории компонент остаются только самые "свежие" компоненты.
            Версия компонента определяется из кортежа, формируемого из имени файла компонента
            (имя, версия, расширение файла)
    """

    dir_components, sub_dir_oldest, components = get_components()
    components = sorted(components)
    count_outdated = 0
    name_tuple_previous = ('', '', '')

    for component in components:
        name_tuple = f.name_to_tuple(component.parts[-1])
        if name_tuple:
            if f.is_eq_name(name_tuple, name_tuple_previous):
                remove_oldest_file(dir_components, sub_dir_oldest,
                                   get_oldest_component(name_tuple, name_tuple_previous))
                count_outdated += 1
        else:
            name_tuple = ('', '', '')
        name_tuple_previous = name_tuple

    logging.info(f'Обнаружено и перенесено в поддиректорию {C.SUB_DIR_OLD}: '
                 f'устаревших компонент - {count_outdated}')
    return None


def get_components() -> (Path, Path, list):
    """ Функция get_components() -> (Path, Path, list):

        Возвращает
            Выбранную из параметров программы директорию компонент.
            Поддиректорию для устаревших файлов.
            Список файлов (компонент) выбранной директории.
    """

    if len(argv) != 2:
        raise MyException("Программе передано неверное количество параметров.\n"
                          "Программа принимает 1 параметр:\n"
                          "   Имя директории с дистрибутивом обновлений, например,\n"
                          "   c:\\Дистрибутив\\PREPARE').\n", 1000)

    dir_components = Path(argv[1])
    try:
        list_components = dir_components.glob('*.*')
    except Exception as e:
        raise MyException(f'Нет доступа к каталогу {dir_components}\n'
                          f'{e}\n'
                          f'Обратитесь к системному администратору.', 1000)

    sub_dir_oldest = Path(dir_components, C.SUB_DIR_OLD)
    try:
        sub_dir_oldest.mkdir(exist_ok=True)
    except Exception as e:
        raise MyException(f'Нет доступа к каталогу {sub_dir_oldest}\n'
                          f'{e}\n'
                          f'Обратитесь к системному администратору.', 1000)

    for file in sub_dir_oldest.glob('*.*'):
        raise MyException(f'Директория {sub_dir_oldest} не пуста\n'
                          'Работа программы невозможна', 1000)

    return dir_components, sub_dir_oldest, list_components


def get_oldest_component(tuple1, tuple2) -> tuple:
    """ Функция get_oldest_component(tuple1, tuple2) -> tuple
            Cравнивает номера версий компонентов.

        Аргументы:
            tuple1 (tuple): кортеж имени компонента (имя, версия, расширение файла).
            tuple2 (tuple): кортеж имени компонента (имя, версия, расширение файла).

        Результат
            Картеж имени компонента с более ранней версией.
    """

    return tuple1 if int(tuple1[1]) < int(tuple2[1]) else tuple2


def remove_oldest_file(dir_components: Path, sub_dir_oldest: Path, tuple_: tuple) -> None:
    """ Функция remove_oldest_file(dir_components: Path, tuple_: tuple) -> None
            преремещает файл компонента в поддиректорию SUB_DIR_OLD.

        Аргументы
            1. dir_components: Path.    Полный путь к директории с компонентами.
            2. tuple_:         tuple.   Картеж имени перемещаемого файла компонента (имя, версия, расширение файла).
    """

    file_name = tuple_[0] + tuple_[1] + tuple_[2]
    file_from = Path(dir_components, file_name)
    file_to = Path(sub_dir_oldest, file_name)
    try:
        file_from.rename(file_to)
    except Exception as e:
        raise MyException(f'Не могу копировать файл {file_to}\n'
                          f'{e}\n'
                          f'Обратитесь к системному администратору.', 1000)


if __name__ == '__main__':
    main_()
