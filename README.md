Работа с FTP сервером компонент Системы "Галактика".

path_FTP.py  - сверяет состав файлов в эталонной директории компонент на FTP сервере и 
в директории компонент на локальном диске. Новые компоненты или компоненты с более "свежими" версиями
переписываются в поддиректорий компонент локального диска.
После успешного копирования новые компоненты переписываются из поддиректории в основной директорий компонент

path_men.py - оставляет в локальной директории компонент только самые "свежие" компоненты.
Устаревшие компоненты переписываются в специальный поддиректорий директории компонент.

prepare_send.py - формирует DOCX файл с информационным письмом о выходе новых компонент.

descr.docx - вытягивает из описаний компонент свежие описания, удаляет дублирующиеся,
                форматирует их и записывает в WORD файл.
