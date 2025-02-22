import re
from dataclasses import dataclass

from docx.shared import Cm, Inches, Pt
from docx.enum.section import WD_ORIENTATION


@dataclass
class ColumnProperties:
    head_text: str
    head_width: Cm | Inches
    font_name: str | None = None
    font_size: Pt | None = None
    font_bold: bool | None = None


@dataclass(frozen=True, slots=True)
class Const:
    Size = Cm | Inches
    FTP_SITE = "ftp.galaktika.ru"  # FTP сервер "Галактика".
    USER = "anonymous"  # имя пользователя FTP сервера.
    PASSWORD = ""  # пароль пользователя FTP сервера.
    SUB_DIR_NEW = "NEW"  # Имя поддиректории для скопированных с FTP сервера компонент.
    SUB_DIR_OLD = "OLD"  # Имя поддиректории для перемещённых устаревших компонент.
    TIME_OUT_SEC = 5  # Количество секунд на ожидания отклика с FTP сервера.
    PRINTING_RATIO = 10  # Через сколько операций вывода 'FTP -> компьютер' надо делать сообщение в консоль.
    FILE_STOP_LIST = "stop_list.txt"  # Файл с именами файлов, не подлежащих скачиванию с FTP сервера.
    ZERO_VERSION = "00000"  # Версия компонента = 0.
    WORD_FONT_NAME = "Tahoma"  # Имя шрифта текста, формируемого, для MS WORD.
    WORD_FONT_SIZE = Pt(11)  # Размер шрифта текста, формируемого, для MS WORD.
    WORD_NAME = "Рассылка.docx"  # Имя формируемого WORD файла.
    TEXT_MAIL = "текст письма.txt"  # Файл с шаблоном текста письма.
    FILE_SAVE_DESCRIPTIONS = "Описания новых изменений.docx"
    END_PRINT_LIST_COMPONENTS = ".\n"
    COMPONENT_SEPARATOR = (
        ", "  # Разделитель имён компонент в списке информационного письма.
    )
    TEXT_ERROR_SAVE = "Доступ к файлу сохранения документа запрещён"
    TEXT_1 = (
        "\nЕсли вы начинаете новое скачивание файлов - нажмите клавиши 'н' и Enter.\n"
        "Если Вы продолжаете скачивание после сбоя - 'п' и Enter.\n"
    )
    TEXT_3 = (
        "\nПапка старых версий компонент не пуста.\n"
        "Если Вам не нужны эти файлы нажмите 'н' и Enter.\n"
        "и программа удалит старые версии компонент.\n"
        "Если Вам нужны старые версии компонент - нажмите 'п' и Enter.\n"
        " и программа прекратит свою работу\n"
    )
    RE_PATTERN_NAME_COMPONENT = r"(.*_)(\d+)(\.?\w*$)"
    # Шаблон для выделения 3 частей имени компонента.
    # 1 - собственно имя компонента.
    # 2 - версия компонента.
    # 3 - расширение компонента.
    # Например, имя файла компонента: F_GETAN_RES_911010.acd.
    # Имя компонента - F_GETAN_RES_, версия - 911010, расширение - .acd.

    JIRA_TASK = "ЗАДАЧА В JIRA:"
    JIRA_FIRST_SOLUTION = "ПЕРВОЕ РЕШЕНИЕ:"
    JIRA_BRIEF_DESCRIPTION = "КРАТКОЕ ОПИСАНИЕ:"
    JIRA_WHAT_CHANGED = "ЧТО ИЗМЕНЕНО:"
    JIRA_HOW_CHANGED = "КАК ИЗМЕНЕНО:"
    JIRA_END = "* *"
    JIRA_START_S = "* "
    JIRA_START_G = "# "

    NEW = "NEW"

    RE_ERP = re.compile(
        r""".*(?P<ERP>ERP\s*-\s*\d+)""",
        re.VERBOSE,
    )
    COLUMN_PROPERTIES = [
        ColumnProperties("ERP", Cm(2), "Arial", Pt(10)),
        ColumnProperties("Компоненты", Cm(4.04), "Arial", Pt(9)),
        ColumnProperties("Описание", Cm(3), "Arial", Pt(10)),
        ColumnProperties("Что изменено", Cm(8.46), "Arial", Pt(9)),
        ColumnProperties("Как изменено", Cm(8.46), "Arial", Pt(9)),
    ]
    TABLE_STYLE = "Light Grid Accent 1"
    TEXT_ERROR_PARAMETER = (
        "Программе передано неверное количество параметров.\n"
        "Программа принимает 1 параметр:\n"
        "   Имя директории с описаниями обновлений, например,\n"
        "   'c:\\Дистрибутив\\DESCRIPTIONS'."
    )
    PAGE_FIELDS = Cm(1), Cm(1), Cm(1), Cm(1)
    WORD_DESCRIPTIONS_ORIENTATION = WD_ORIENTATION.LANDSCAPE
    EXT_DESCRIPTIONS = "*.txt"
    TEXT_NO_DIR_NEW = "Нет доступа к каталогу."
    TEXT_PERMISSION_FILE = "Запрещён доступ к файлу"


const = Const()
