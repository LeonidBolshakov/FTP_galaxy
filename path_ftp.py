import logging
import socket
from ftplib import FTP
from pathlib import Path
from sys import argv

import component_functions as f
import path_men
from constant import const as c


def main_():
    """Функция:
        main_
    Назначение:
        вызывает функцию main, обрабатывает сгенерированные прерывания
        и завершает работу программы.
    """

    ftp = None
    try:
        (ftp, count_of_files_copied, count_of_files_not_copied) = main()
    except KeyboardInterrupt:
        ret_code = 1000
        logging.critical(
            "Оператор прекратил работу программы\n" f"Код возврата {ret_code}"
        )
        my_exit(ftp, ret_code)
    except f.MyException as e:
        logging.error(
            f"{e.text_err}\n"
            f"Программа завершила работу.\n"
            f"Код возврата {e.ret_code}"
        )
        my_exit(ftp, e.ret_code)
    except Exception as e:
        ret_code = 1000
        tb = traceback.format_exc()
        logging.critical(
            f"{e}\n" f"Программа завершилась аварийно\n{tb}\nКод возврата {ret_code}\n"
        )
        my_exit(ftp, ret_code)
    else:
        if count_of_files_not_copied == 0:
            ret_code = 0
            if count_of_files_copied > 0:
                logging.info(
                    f"Программа закончила свою работу.\n"
                    f"С FTP скопировано файлов: {count_of_files_copied}\n"
                    f"Код возврата {ret_code}"
                )
            else:
                logging.info(
                    f"Программа закончила свою работу.\n"
                    f"Директории на FTP сервере и локальном компьютере синхронны\n"
                    f"Код возврата {ret_code}"
                )

                my_exit(ftp, ret_code)
        else:
            ret_code = 1
            logging.warning(
                f"Программа закончила свою работу.\n"
                f"С FTP скопировано файлов: {count_of_files_copied}\n"
                f"С FTP не скопировано файлов: {count_of_files_not_copied}\n"
                f"Код возврата {ret_code}"
            )
            if not is_VPN_connected():
                logging.info(f"Подключите VPN и повторите вызов программы")
            my_exit(ftp, ret_code)


def main() -> tuple[FTP, int, int]:
    """Функция
        main() -> tuple[FTP, int, int]
    Назначение
        Файлы, существующие на FTP сервере и отсутствующие в директории компьютера,
        записываются в поддиректорию.
    Результат:
        tuple, состоящий из 3 целых чисел:
        1. FTP сервер
        2. Количество скопированных файлов
        3. Количество не скопированных файлов.
    """
    file_log = logging.FileHandler("Log_FTP.log")
    console_out = logging.StreamHandler()

    logging.basicConfig(
        level=logging.INFO,
        handlers=(file_log, console_out),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    count_of_files_copied = 0
    count_of_files_not_copied = 0

    try:
        _, local_dir, ftp_dir = argv
    except ValueError:
        raise f.MyException(
            "Программе передано неверное количество параметров.\n"
            "Программа принимает 2 параметра:\n"
            "1. Имя директории локального диска с дистрибутивом обновлений, например,\n"
            "   c:\\Дистрибутив\\PREPARE\n"
            "2. Имя директории FTP сервера Галактика, например,\n"
            "   /pub/support/galaktika/bug_fix/GAL910/UPDATES/\n",
            777,
        )
    logging.info(Path(ftp_dir).name)
    VPN_connected = is_VPN_connected()
    local_subdir = check_local_subdir(name_local_dir=local_dir)
    already_copied_files = selection_already_copied_files(local_subdir=local_subdir)
    stop_list_files = selection_stop_list_files(VPN_connected=VPN_connected)
    local_files = get_local_files(local_dir=local_dir)

    ftp = connect_to_ftp(
        ftp_site=c.FTP_SITE, ftp_dir=ftp_dir, user=c.USER, password=c.PASSWORD
    )
    ftp_files = ftp.nlst()

    for ftp_file in ftp_files:
        if ftp_file not in local_files and ftp_file not in already_copied_files:
            if not VPN_connected and is_stop_list_file(ftp_file, stop_list_files):
                count_of_files_not_copied += 1
                logging.info(
                    f"Файл {ftp_file} в стоп списке:\nФайл {ftp_file} не скопирован\n"
                )
                continue
            if copy_from_ftp_file(ftp, ftp_file, local_subdir):
                count_of_files_copied += 1
            else:
                count_of_files_not_copied += 1

    if count_of_files_copied != 0 and Path(ftp_dir).name == "UPDATES":
        if copy_from_ftp_file(ftp, "UPDATES.sfv", local_subdir):
            count_of_files_copied += 1

    if count_of_files_not_copied == 0 and count_of_files_copied != 0:
        logging.info(f"Переписано файлов: {count_of_files_copied}")
        count_of_files_copied = -count_of_files_copied
        copy_dir_to_dir(dir_from=local_subdir, dir_to=local_dir)
        path_men.main_()

    if not is_same_directories(ftp, Path(local_dir)):
        raise f.MyException(
            "Состав и/или размеры файлов на FTP сервере и локальном компьютере не совпали",
            777,
        )

    print("\r")
    return ftp, count_of_files_copied, count_of_files_not_copied


def selection_stop_list_files(VPN_connected: bool) -> list:
    """Функция selection_stop_list_files(VPN_connected:bool) -> list:
        Формирует список файлов, которые не надо переписывать с FTP сервера
        (Стоп лист)
    :param
        VPN_connected: Если VPN подключен надо формировать пустой стоп лист
    :return:
        Список файлов, которые не надо переписывать с FTP сервера (стоп лист)
    """
    if not VPN_connected:
        stop_list_files = []
        with open(c.FILE_STOP_LIST) as file_stop_list:
            for line in file_stop_list:
                name = f.reset_component_version(line)
                stop_list_files.append(name)
        logging.info("VPN не подключен\n" "Файлы из STOP листа копироваться не будут")
        return stop_list_files
    return list()


def selection_already_copied_files(local_subdir: Path) -> list:
    """Функция selection_already_copied_files(local_subdir: Path) -> list:
        Формирует список файлов, ранее записанных в поддиректорию NEW.
        Эти файлы с FTP сервера повторно записываться не будут.
    :param
        local_subdir: поддиректория для новых файлов - NEW
    :return:
        Список имён файлов
    """
    existing_files = []
    for file in local_subdir.glob("*.*"):
        if file.is_file():
            existing_files.append(file.name)
    return existing_files


def my_exit(ftp: FTP, ret_code: int):
    """
    Функция my_exit(ret_code):
    Назначение:
        Разрывает соединение с FTP сервером и завершает работу программы
    Аргументы:
        1. ftp: FTP         - FTP сервер
        2. ret_code: int    - код возврата
    Результат:
        None
    """
    try:
        ftp.quit()
    except Exception:
        pass

    try:
        input("Для завершения работы нажмите клавишу Enter\n")
    except KeyboardInterrupt:
        f.MyException("Оператор прервал работу программы", ret_code)
    exit(ret_code)


def connect_to_ftp(ftp_site: str, ftp_dir: str, user: str, password: str) -> FTP:
    """Функция
        connect_to_ftp(ftp_site: str, ftp_dir: str, user: str, password: str) -> FTP
    Аргументы:
        1. ftp_site: str    - адрес FTP сервера
        2. ftp_dir: str     - путь на директорию на FTP сервера
        3. user: str        - login FTP сервера
        4. password:str     - пароль FTP сервера
    Результат:
        ftp                 - FTP сервер
    """

    try:
        ftp = FTP(ftp_site, timeout=c.TIME_OUT_SEC)
        ftp.login(user=user, passwd=password)
        ftp.cwd(ftp_dir)
    except Exception as e:
        raise f.MyException(f"Ошибка при доступе к FTP серверу\n {e}", 777)

    return ftp


def check_local_subdir(name_local_dir: str) -> Path:
    """Функция:
        check_local_subdir(name_local_dir: str) -> Path
    Аргумент:
        name_local_dir: str - имя директории, в которой создаётся поддиректория.
    Результат:
        Проверенная поддиректория.
    """
    local_subdir = Path(name_local_dir, c.SUB_DIR_NEW)
    if local_subdir.exists():
        if local_subdir.is_dir():
            f.confirm_if_needed(local_subdir)
            return local_subdir
        else:
            raise f.MyException(
                f"{local_subdir} существует, но не является папкой", 777
            )
    else:
        try:
            local_subdir.mkdir(parents=False)
        except Exception as err:
            raise f.MyException(
                f"Не могу создать директорию: {local_subdir}, \n" f"Ошибка {err}", 777
            )

    return local_subdir


def get_local_files(local_dir: str) -> set:
    """Функция:
        get_local_files() -> set
    Аргумент:
        local_dir: str - Полный путь на локальную директорию
    Результат:
        Множество имён файлов директории
    """

    try:
        directory_files = Path(local_dir)
        list_files = [file.name for file in directory_files.iterdir() if file.is_file()]
    except Exception as e:
        raise f.MyException(f"Нет доступа к директории {local_dir}\n{e}", 777)

    return set(list_files)


def is_stop_list_file(ftp_file: str, stop_list_files: list[str]) -> bool:
    """Функция is_stop_list_file(ftp_file, stop_list_files) -> bool:
        Проверяет входит ли файл в стоп лист.
    :param
        ftp_file:           Имя файла
        stop_list_files:    Список имён файлов стоп листа
    :return:
        True если файл входит в стоп лист, False - если не входит.
    """
    name = f.reset_component_version(ftp_file)
    return True if name in stop_list_files else False


def copy_from_ftp_file(ftp: FTP, ftp_file: str, local_subdir: Path) -> bool:
    """Функция: copy_from_ftp_file(ftp: FTP, ftp_file: str, local_subdir: Path) -> bool
    Аргументы:
        1. ftp: FTP             - FTP сервер
        2. ftp_file: str        - Имя файла с FTP сервера
        3. local_subdir: Path   - Целевая поддиректория
    Назначение:
        Копирование файла в целевую поддиректорию
    Результат:
        bool:
            True - если файл скопирован успешно.
            False - если файл не скопирован.
    """

    count_call = 0
    i_progress = 0

    def my_write(buffer: bytes):
        nonlocal count_call
        nonlocal i_progress
        progress = ["|", "/", "—", "\\"]
        file.write(buffer)
        if count_call == 0:
            print(f"\r{progress[i_progress]}", end="")
            i_progress = (i_progress + 1) % len(progress)
        count_call = (count_call + 1) % c.PRINTING_RATIO

    print(f"\rкопируем файл {ftp_file}")

    local_file = Path(local_subdir, ftp_file)
    try:
        with open(local_file, "wb") as file:
            ftp.retrbinary("RETR " + ftp_file, my_write)
        return True
    except Exception as err:
        logging.warning(
            f"Произошла ошибка при копировании {err}:\nФайл {ftp_file} не скопирован\n"
        )
        del_local_file(local_file)

        return False
    except KeyboardInterrupt:
        del_local_file(local_file)
        raise f.MyException("Программа прервана оператором", 1000)


def del_local_file(local_file: Path) -> None:
    """Функция del_local_file(local_file: Path) -> None
    Назначение:
        Удаляет файл, заданный в параметре.
        При отсутствии файла исключение не возникает
    Параметр:
        local_file: Path            - Путь на удаляемый файл
    """
    if local_file.exists():
        local_file.unlink()


def is_VPN_connected() -> bool:
    """Функция is_VPN_connected() -> bool:
        Проверяет подключен ли VPN.
    :return: True, если VPN подключен, False - если не подключен
    """

    hostname = socket.gethostname()
    #  socket.getaddrinfo() возвращает список кортежей, следующей структуры:
    #
    # family (info[0]): для IPv4 == 2.
    # type (info[1]): Тип сокета (например, socket.SOCK_STREAM для TCP).
    # proto (info[2]): Протокол (обычно 0, что означает использование протокола по умолчанию для данного типа сокета).
    # canonname (info[3]): Каноническое имя хоста (обычно пустое).
    # sockaddr (info[4]): Сокетный адрес. Для IPv4 это кортеж (ip, port), IPv6 — (ip, port, flowinfo, scopeid).

    addr_info = socket.getaddrinfo(hostname, None)
    for info in addr_info:
        if info[0] == 2:
            if info[4][0][:7] != '192.168':
                return True
    return False


def copy_dir_to_dir(dir_from: Path, dir_to: str) -> None:
    """Функция copy_dir_to_dir(local_subdir: Path, local_dir: str) -> None:
            Копирует файлы из поддиректории в директорию.
        :param
            dir_from: Path      - поддиректория
            dir_to:   str       - Директория
    :return:                    - None
    """
    for file in dir_from.glob("*.*"):
        if file.is_file():
            copy_file(file_from=file, dir_to=dir_to)


def copy_file(file_from: Path, dir_to: str) -> None:
    """Функция copy_file(file_from: Path, dir_from: Path, dir_to: str) -> None:
        Копирует файл из одной директорию в другую.
    :param
        file_from: копируемый файл
    :param
        dir_from: исходная директория
    :param
        dir_to: Целевая директория
    :return:
        None
    """
    image_data: bytes
    with open(file_from, "rb") as f_from:
        image_data = f_from.read()
    file_to = Path(dir_to, file_from.name)
    with open(file_to, "wb") as f_to:
        f_to.write(image_data)


def is_same_directories(ftp: FTP, local_dir: Path) -> bool:
    """Функция is_same_directories(ftp: FTP, local_dir: Path):
        Сравнивает директорию на FTP сервере и локальную директорию.
        Директории сравниваются по составу и размеру файлов.
    :param
        1. ftp: Директория на сервере FTP.
        2. local_dir: Локальная директория.
    :return:
        True если директории совпали по составу и размеру файлов, False если не совпали.
    """
    ftp_file_sizes = dict()
    size = slice(29, 41)
    name = slice(54, None)

    def my_call_back(line):
        nonlocal ftp_file_sizes
        nonlocal size
        nonlocal name

        if line[size].strip() != "0":
            #   ftp_file_sizes - словарь
            #   line[name].strip() - ключ в словаре
            #   int(line[size]) - значение, соответствующее ключу
            ftp_file_sizes[line[name].strip()] = int(line[size])

    ftp.retrlines(cmd="LIST", callback=my_call_back)

    local_file_sizes = dict()
    for file in Path(local_dir).glob("*.*"):
        if file.is_file():
            local_file_sizes[file.name] = file.stat().st_size

    return True if is_equal_dict(ftp_file_sizes, local_file_sizes) else False


def is_equal_dict(dict1: dict, dict2: dict) -> bool:
    """Функция is_equal_dict(dict1: dict, dict2: dict) -> bool:
        Проверяет равны ли словари.
    :param
        dict1: Сравниваемый словарь (FTP файлы)
        dict2: Сравниваемый словарь (локальные файлы)
    :return:
        True - словари равны. False - словари не равны.
    """
    ret_value = True
    for file in dict1.keys() - dict2.keys():
        ret_value = False
        logging.info(
            f"Файл {file} отсутствует в локальной директории.\nПроверьте директорию {c.SUB_DIR_NEW}"
        )

    for file in dict2.keys() - dict1.keys():
        ret_value = False
        logging.info(f"Лишний файл в локальной директории - {file}")

    for file in dict1.keys() & dict2.keys():
        if dict1[file] != dict2[file]:
            ret_value = False
            logging.info(
                f"Файл {file}.\n"
                f"Размер на FTP сервере {dict1[file]} не совпадает с размером локального файла {dict2[file]}"
            )

    return ret_value


if __name__ == "__main__":
    main_()
