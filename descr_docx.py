"""
Программа просматривает описания загруженных с FTP сервера компонент (файлы из DESCRIPTIONS/NEW)
Выбирает только описания с пометкой NEW и раскидывает их по столбцам таблицы.
Удаляет концы строк, поставленные разработчиками и устанавливает свои концы строк.
Описания одних и тех же решений могут быть в различных файлах описаний.
Из всех одинаковых описаний, программа оставляет только одно описание,
а в столбце таблицы "Файлы" указывается список на все файлы(компоненты)
"""

import sys
import os
from pathlib import Path

from newdescriptions import NewDescriptions
from table import OneSectionWordDocument, TableDocWord
from constant import const as c


def main():
    """Создает Word-документ с таблицей на основе данных из описаний компонент."""
    # Настройка документа
    document = OneSectionWordDocument()
    document.set_orientation(
        c.WORD_DESCRIPTIONS_ORIENTATION
    )  # Ориентация документа WORD
    document.set_margins(*c.PAGE_FIELDS)  # Поля страницы
    # Создание таблицы с заданными свойствами столбцов
    table = TableDocWord(document.doc, c.COLUMN_PROPERTIES)
    table.set_table_style(c.TABLE_STYLE)  # Стиль таблицы

    # Получение данных
    new_descriptions = NewDescriptions(str(Path(check_options(), c.NEW)))
    new_descriptions.processing_descriptions()
    dict_descr = new_descriptions.topics  # Словарь с описаниями задачам

    # Заполнение таблицы файла MS WORD данными из файлов описаний компонент
    for item_key, item_value in dict_descr.items():
        table.add_line(
            [
                item_key,
                ", ".join(item_value.descr_files),
                item_value.brief_description,
                item_value.what_changed,
                item_value.how_changed,
            ]
        )
    # Сохранение и открытие файла
    document.save(c.FILE_SAVE_DESCRIPTIONS)
    os.startfile(c.FILE_SAVE_DESCRIPTIONS)


def check_options() -> str:
    """Проверяет корректность переданных аргументов командной строки и
    возвращает единственный аргумент - путь на директорию с описаниями обновлений"""
    if len(sys.argv) != 2:
        sys.tracebacklimit = 0
        raise ValueError(c.TEXT_ERROR_PARAMETER, 1000)
    return sys.argv[1]


if __name__ == "__main__":
    main()
