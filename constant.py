from docx.shared import Pt
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Const:
    FTP_SITE = 'ftp.galaktika.ru'       # FTP сервер "Галактика"
    USER = 'anonymous'                  # имя пользователя FTP сервера
    PASSWORD = ''                       # пароль пользователя FTP сервера
    SUB_DIR_NEW = 'NEW'                 # Имя поддиректории для скопированных с FTP сервера компонент
    SUB_DIR_OLD = 'OLD'                 # Имя поддиректории для перемещённых устаревших компонент
    TIME_OUT_SEC = 5                    # Количество секунд на ожидания отклика с FTP сервера
    PRINTING_RATIO = 10                 # Через сколько операций вывода 'FTP -> компьютер' надо делать вывод в консоль
    FILE_STOP_LIST = 'stop_list.txt'    # Имя файла, c именами файлов, не подлежащих скачиванию с FTP сервера
    ZERO_VERSION = '00000'              # Версия компонента = 0
    WORD_FONT_NAME = 'Tahoma'           # Имя шрифта текста, формируемого, для MS WORD
    WORD_FONT_SIZE = Pt(11)             # Размер шрифта текста, формируемого, для MS WORD
    WORD_NAME = 'Рассылка.docx'         # Имя формируемого WORD файла
    TEXT_MAIL = "текст письма.txt"      # Файл с шаблоном текста письма
    COMPONENT_SEPARATOR = ', '          # Разделитель имён компонент в списке информационного письма
    RE_PATTERN_NAME_COMPONENT = r'(.*_)(\d+)(\.?\w*$)'
    """ Шаблон для выделения 3 частей имени компонента -
        1 - собственно имя компонента.
        2 - версия компонента
        3 - расширение компонента
        Например, имя файла компонента:F_GETAN_RES_911010.acd.
        имя компонента - F_GETAN_RES_, версия компонента - 911010, расширение - .acd
    """


const = Const()