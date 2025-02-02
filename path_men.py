import logging
from pathlib import Path
from sys import argv, exit

import component_functions as f
from constant import const as C  # Константы


def main_() -> None:
    """Функция main() -> None
    Обрабатывает прерывания сгенерированные в функции main_
    """

    file_log = logging.FileHandler("Log_path.log")
    console_log = logging.StreamHandler()

    logging.basicConfig(
        level=logging.INFO,
        handlers=(file_log, console_log),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    try:
        main()
    except f.MyException as e:
        logging.error(e.text_err)
        exit(e.ret_code)
    except Exception as e:
        logging.critical(f"Непредвиденная ошибка\n{e}")


def main() -> None:
    """Функция main_() -> None
    Для всех компонентов, имеющих одинаковые имена компонента и расширения файла,
    перемещает в директорию OLD компоненты с более ранней версией.
    В результате в директории компонент остаются только самые "свежие" компоненты.
    Версия компонента определяется из кортежа, формируемого из имени файла компонента
    (имя, версия, расширение файла)
    """

    dir_components, sub_dir_oldest, components = get_components()
    components = sorted(components)
    count_outdated = 0
    name_tuple_previous = ("", "", "")

    for component in components:
        name_tuple = f.name_to_tuple(component.parts[-1])
        if name_tuple:
            if f.is_eq_name(name_tuple, name_tuple_previous):
                remove_oldest_file(
                    dir_components,
                    sub_dir_oldest,
                    get_oldest_component(name_tuple, name_tuple_previous),
                )
                count_outdated += 1
        else:
            name_tuple = ("", "", "")
        name_tuple_previous = name_tuple

    logging.info(
        f"Обнаружено и перенесено в поддиректорию {C.SUB_DIR_OLD}: "
        f"устаревших компонент - {count_outdated}"
    )
    return None


def get_components() -> tuple[Path, Path, list]:
    """Функция get_components() -> (Path, Path, list):

    Возвращает
        Выбранную из параметров программы директорию компонент.
        Поддиректорию для устаревших файлов.
        Список файлов (компонент) выбранной директории.
    """

    if not 2 <= len(argv) <= 3:
        raise f.MyException(
            "Программе передано неверное количество параметров.\n"
            "Программа принимает 1 параметр:\n"
            "   Имя директории с дистрибутивом обновлений, например,\n"
            "   c:\\Дистрибутив\\PREPARE').\n"
            "   Допускается второй, необрабатываемый, параметр",
            1000,
        )

    dir_components = Path(argv[1])
    try:
        list_components = [file for file in dir_components.iterdir() if file.is_file()]
    except Exception as e:
        raise f.MyException(
            f"Нет доступа к каталогу {dir_components}\n"
            f"{e}\n"
            f"Обратитесь к системному администратору.",
            1000,
        )

    sub_dir_oldest = Path(dir_components, C.SUB_DIR_OLD)

    try:
        sub_dir_oldest.mkdir(exist_ok=True)
    except Exception as e:
        raise f.MyException(
            f"Нет доступа к каталогу {sub_dir_oldest}\n"
            f"{e}\n"
            f"Обратитесь к системному администратору.",
            1000,
        )

    if is_dir_no_empty(sub_dir_oldest):
        if f.dialog(C.TEXT_3, ["н", "п"]) == "н":
            f.delete_all(sub_dir_oldest)
        else:
            raise f.MyException(
                f"Старые версии компонент находятся в папке {sub_dir_oldest}\n", 1000
            )

    return dir_components, sub_dir_oldest, list_components


def get_oldest_component(tuple1, tuple2) -> tuple:
    """Функция get_oldest_component(tuple1, tuple2) -> tuple.
        Сравнивает номера версий компонентов.

    Аргументы:
        tuple1 (tuple): кортеж имени компонента (имя, версия, расширение файла).
        tuple2 (tuple): кортеж имени компонента (имя, версия, расширение файла).

    Результат
        Картеж имени компонента с более ранней версией.
    """

    # Выравниваем длины версий файлов
    version_1 = tuple1[1]
    version_2 = tuple2[1]
    delta_len = len(version_1) - len(version_2)
    if delta_len < 0:
        version_1 += '0'*(-delta_len)
    elif delta_len > 0:
        version_2 += '0'*delta_len

    return tuple1 if int(version_1) < int(version_2) else tuple2


def remove_oldest_file(
    dir_components: Path, sub_dir_oldest: Path, tuple_: tuple
) -> None:
    """Функция remove_oldest_file(dir_components: Path, tuple_: tuple) -> None
        перемещает файл компонента в поддиректорию SUB_DIR_OLD.

    Аргументы
        1. dir_components: Path.    Директория с компонентами.
        2. sub_dir_oldest: Path.    Директория со старыми версиями компонент
        3. tuple_:         tuple.   Картеж имени перемещаемого файла компонента
                                    (имя, версия, расширение файла).
    """

    file_name = tuple_[0] + tuple_[1] + tuple_[2]
    file_from = Path(dir_components, file_name)
    file_to = Path(sub_dir_oldest, file_name)
    try:
        file_from.rename(file_to)
    except Exception as e:
        raise f.MyException(
            f"Не могу копировать файл {file_to}\n"
            f"{e}\n"
            f"Обратитесь к системному администратору.",
            1000,
        )


def is_dir_no_empty(dir_: Path) -> bool:
    return any(dir_.iterdir())


if __name__ == "__main__":
    main_()
