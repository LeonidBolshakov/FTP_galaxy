import sys
from pathlib import Path
from dataclasses import dataclass
import re

from constant import const as c


@dataclass
class Jira:
    """Дата-класс для хранения информации о задаче ERP.
    Поля:
        descr_files (list[str]): Список имён файлов с описанием.
        brief_description (str): Краткое описание задачи.
        what_changed (str): Что было изменено.
        how_changed (str): Как было изменено.
    """

    descr_files: list[str]
    brief_description: str
    what_changed: str
    how_changed: str


class NewDescriptions:
    """Класс для обработки файлов из директории NEW и формирования структурированных данных."""

    def __init__(self, vars_: str) -> None:
        self.vars_ = vars_  # Путь к директории с файлами
        self.buffer = ""  # Буфер для накопления текста
        self.topics: dict[str, Jira] = (
            {}
        )  # Словарь описаний задач (ключ: номер проблемы в JIRA)
        # Временные переменные для текущей задачи
        self.topic_key = ""
        self.topic_value = Jira([], "", "", "")
        self.file = ""  # Имя файла с описанием задачи
        self.partition = ""  # Текущий раздел (например: описание, изменения)

    def processing_descriptions(self) -> None:
        """Основной метод: обрабатывает все .txt файлы в директории NEW."""
        sub_dir_new = Path(self.vars_)
        # Проверка доступности директории
        if sub_dir_new.is_dir():
            description_files = sub_dir_new.glob(c.EXT_DESCRIPTIONS)
        else:
            sys.tracebacklimit = 0
            raise PermissionError(f"{c.TEXT_NO_DIR_NEW} {sub_dir_new}")
        # Обработка каждого отфильтрованного файла
        for file_path in description_files:
            self.file = file_path.stem  # Имя файла
            self._descriptions_into_dictionary(file_path)

    def _descriptions_into_dictionary(self, file: Path) -> None:
        """Читает файл, выделяет секции (темы), структурирует и сохраняет их в словарь."""
        try:
            with file.open("r", encoding="ANSI") as file_input:
                fill_topic = False  # Флаг для отслеживания секции
                for line in file_input:
                    if self._is_begin_topic(line):
                        fill_topic = True
                        topic = []  # Новая секция
                    if fill_topic:
                        topic.append(line)
                    if self._is_end_topic(line) and fill_topic:
                        # Если начались топики без пометки NEW - завершаем обработку файла
                        if not self._do_topic(topic):
                            return
                        fill_topic = False
        except PermissionError:
            sys.tracebacklimit = 0
            raise PermissionError(f"{c.TEXT_PERMISSION_FILE} {file.name}")

    @staticmethod
    def _is_begin_topic(line: str) -> bool:
        """Определяет начало секции (темы) задачи JIRA.
        Проверяет, начинается ли строка с маркера начала задачи (например, '* ЗАДАЧА В JIRA:').
        """
        if line.startswith(c.JIRA_START_S + c.JIRA_TASK):
            return True
        return False

    @staticmethod
    def _is_end_topic(line: str) -> bool:
        """Определяет конец секции (темы) задачи JIRA.
        Проверяет, начинается ли строка с маркера конца секции (например, '* * *')."""
        if line.startswith(c.JIRA_START_S + c.JIRA_END):
            return True
        return False

    def _do_topic(self, topic: list[str]) -> bool:
        """Обрабатывает секцию (тему): распределяет строки по соответствующим полям задачи Jira.
        Использует паттерн-сравнение для определения типа данных в строке."""
        for line in topic:
            match line[:2], line[
                2:
            ]:  # Первые два символа - признаки начала служебной строки
                # Обработка начала задачи
                case c.JIRA_START_S, txt if txt.startswith(c.JIRA_TASK):
                    self._jira_task(line)
                # Проверка наличия маркера NEW
                case c.JIRA_START_S, txt if txt.startswith(c.JIRA_FIRST_SOLUTION):
                    if not self._jira_first_solution_new(line):
                        return False
                # Парсинг краткого описания
                case c.JIRA_START_S, txt if txt.startswith(c.JIRA_BRIEF_DESCRIPTION):
                    self._jira_brief_description(line)
                # Парсинг раздела "Что изменено"
                case c.JIRA_START_G, txt if txt.startswith(c.JIRA_WHAT_CHANGED):
                    self._jira_what_changed(line)
                # Парсинг раздела "Как изменено"
                case c.JIRA_START_G, txt if txt.startswith(c.JIRA_HOW_CHANGED):
                    self._jira_how_changed(line)
                # Обработка конца секции
                case c.JIRA_START_S, txt if txt.startswith(c.JIRA_END):
                    self._jira_end()
                # Все остальные строки (данные для текущего раздела)
                case _:
                    self._jira_default(line)
        return True

    def _jira_task(self, line: str):
        """Извлекает ключ задачи Jira из строки (например, 'TASK_123').
        В случае ошибки формирует ключ с маркером '?????'."""
        # noinspection PyBroadException
        try:
            key = c.RE_ERP.match(line)[
                "ERP"
            ]  # Использует регулярное выражение из модуля констант
        except Exception:
            self.topic_key = f"????? - {line}"  # Запасной ключ при ошибке парсинга
        else:
            self.topic_key = str(key)
        self.partition = ""  # Сброс текущего раздела

    def _jira_first_solution_new(self, line: str) -> bool:
        """Проверяет наличие маркера NEW в строке.
        Возвращает False, если маркер отсутствует (секция игнорируется)."""
        self.partition = ""
        return False if line.find(c.NEW) == -1 else True

    def _jira_brief_description(self, line: str):
        """Активирует раздел для сбора краткого описания задачи.
        - Сохраняет предыдущие данные из буфера.
        - Устанавливает тип текущего раздела в 'JIRA_BRIEF_DESCRIPTION'.
        - Инициализирует буфер текстом после маркера краткого описания.
        """
        self.jira_formation()  # Сохранение данных из предыдущего раздела
        self.partition = c.JIRA_BRIEF_DESCRIPTION  # Установка типа текущего раздела
        self.buffer = line.partition(c.JIRA_BRIEF_DESCRIPTION)[2]  # Текст после маркера

    def _jira_what_changed(self, line: str):
        """Активирует раздел для сбора информации о том, *что* было изменено.
        - Сохраняет предыдущие данные из буфера.
        - Устанавливает тип раздела в 'JIRA_WHAT_CHANGED'.
        - Инициализирует буфер текстом после маркера *что* изменено.
        """
        self.jira_formation()
        self.partition = c.JIRA_WHAT_CHANGED
        self.buffer = line.partition(c.JIRA_WHAT_CHANGED)[2]

    def _jira_how_changed(self, line: str):
        """Активирует раздел для сбора информации о том, *как* было изменено.
        - Сохраняет предыдущие данные из буфера.
        - Устанавливает тип раздела в 'JIRA_HOW_CHANGED'.
        - Запускает накопление текста после маркера *как* было изменено.
        """
        self.jira_formation()
        self.partition = c.JIRA_HOW_CHANGED
        self.buffer = line.partition(c.JIRA_HOW_CHANGED)[2]

    def _jira_end(self):
        """Завершает обработку секции: сохраняет информацию о задаче в словарь topics."""
        self.jira_formation()
        if self.topic_key in self.topics:
            # Если описание существующей задачи уже есть в словаре,
            # то в список файлов с описанием добавляем имя текущего файла.
            # Остальные поля элемента словаря не трогаем.
            topic_from_dict: Jira = self.topics[self.topic_key]
            topic_from_dict.descr_files.append(self.file)
        else:
            # Создание новой записи
            self.topic_value.descr_files = [
                self.file
            ]  # Преобразуем имя файла в список из одного элемента
            self.topics[self.topic_key] = self.topic_value
        # Сброс переменных информации о разделе (задаче).
        self.topic_value = Jira([], "", "", "")
        self.partition = ""

    def _jira_default(self, line: str):
        """Обрабатывает строки, не являющиеся маркерами (данные для текущего раздела).
        Накапливает данные в buffer, если описание задачи активно."""
        if self.partition:
            self.buffer += line  # Накопление данных

    def jira_formation(self):
        """Переносит данные из buffer в соответствующие поля Jira при смене раздела."""
        match self.partition:
            case c.JIRA_BRIEF_DESCRIPTION:
                self.topic_value.brief_description = self.format_buffer(self.buffer)
            case c.JIRA_WHAT_CHANGED:
                self.topic_value.what_changed = self.format_buffer(self.buffer)
            case c.JIRA_HOW_CHANGED:
                self.topic_value.how_changed = self.format_buffer(self.buffer)
        self.partition = ""  # Сброс раздела

    @staticmethod
    def format_buffer(buffer: str) -> str:
        """Форматирует текст: удаляет лишние переносы строк, добавляет их после завершения предложений."""
        text = buffer.strip().replace("\n", " ")
        # Регулярное выражение для вставки переносов после точек (кроме последнего предложения)
        return re.sub(r"(\.)(\s)([\dA-ZА-ЯЁ])", r"\1\\n\3", text).replace(r"\n", "\n")
