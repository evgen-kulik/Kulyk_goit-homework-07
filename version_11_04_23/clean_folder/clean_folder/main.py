import os
from os.path import basename
from pathlib import Path
import re
import shutil
import sys

lst_known = []
lst_files_addresses = []
lst_folders_addresses = []

dict_extensions = {
    'folders': [],
    'images': [],
    'videos': [],
    'documents': [],
    'music': [],
    'archives': [],
    'unknown': [],
}


def files_addresses(path):
    """Повертає список всіх файлів та папок зі шляхами"""

    items = path.glob('**/*')   # рекурсивно проходить по всіх папках і повертає список шляхів з файлами
    # print(items)      # цей список має додаткові системні дописи, тому його необхідно перетворити в str
    for item in items:
        if not item.is_dir():  # якщо елемент не є папкою, то:
            lst_files_addresses.append(str(item))
    return lst_files_addresses


def folders_addresses(path):
    """Повертає список всіх папок зі шляхами"""

    items = path.glob('**/*')   # рекурсивно проходить по всіх папках і повертає список шляхів з файлами
    # print(items)      # цей список має додаткові системні дописи, тому його необхідно перетворити в str
    for item in items:
        if item.is_dir():  # якщо елемент не є папкою, то:
            lst_folders_addresses.append(str(item))
    return lst_folders_addresses


def folders_addresses_in_dict():
    """Повертає словник зі списком папок зі шляхами"""

    for i in lst_folders_addresses:
        dict_extensions['folders'].append(i)
    return dict_extensions


def sort_extensions():
    """Повертає словник з груповими списками файлів зі шляхами"""

    for i in lst_files_addresses:

        images_result = re.findall(r"([^/]+[/.](jpeg|png|jpg|svg|bmp))", str(i))
        if len(images_result) > 0:
            for i in images_result:
                dict_extensions['images'].append(i[0])
                lst_known.append(i[0])

        videos_result = re.findall(r"([^/]+[/.](avi|mp4|mov|mkv))", str(i))
        if len(videos_result) > 0:
            for i in videos_result:
                dict_extensions['videos'].append(i[0])
                lst_known.append(i[0])

        documents_result = re.findall(r"([^/]+[/.](doc|docx|txt|pdf|xlsx|pptx))", str(i))
        # присутня системна помилка щодо розширення ".docx" (чомусь у список "lst_known" воно потрапляє без "x")
        if len(documents_result) > 0:
            for i in documents_result:
                dict_extensions['documents'].append(i[0])
                lst_known.append(i[0])

        music_result = re.findall(r"([^/]+[/.](mp3|ogg|wav|amr))", str(i))
        if len(music_result) > 0:
            for i in music_result:
                dict_extensions['music'].append(i[0])
                lst_known.append(i[0])

        archives_result = re.findall(r"([^/]+[/.](zip|gz|rar|tar))", str(i))
        if len(archives_result) > 0:
            for i in archives_result:
                dict_extensions['archives'].append(i[0])
                lst_known.append(i[0])

    lst_unknown = list(set(lst_files_addresses) - set(lst_known))  # визначаємо через множини невідомі розширення
    for i in lst_unknown:
        dict_extensions['unknown'].append(i)
    print(dict_extensions)
    return dict_extensions


def known_or_not_extensions():
    """Виводить на екран списки відомих та невідомих розширень у цільовій папці"""

    lst_unknown_extensions_clear = []
    lst_known_extensions_clear = []
    for key, value in dict_extensions.items():
        if key == 'unknown':
            lst_unknown_extensions = re.findall(r"([ /.][\w]+['])", str(value))
            # для пошуку розширень через регулярний вираз, прийшлося залишити апостроф в кінці,
            # тепер приберемо його, при цьому буде наповнено новий список
            for i in lst_unknown_extensions:
                lst_unknown_extensions_clear.append(i[:-1])
        elif key == 'folders':
            pass
        else:
            lst_known_extensions = re.findall(r"([ /.][\w]+['])", str(value))
            # для пошуку розширень через регулярний вираз, прийшлося залишити апостроф в кінці,
            # тепер приберемо його, при цьому буде наповнено новий список
            for i in lst_known_extensions:
                lst_known_extensions_clear.append(i[:-1])

    # за допомогою множин позбавимося повторень в списках розширень
    lst_unknown_extensions_clear = list(set(lst_unknown_extensions_clear))
    lst_known_extensions_clear = list(set(lst_known_extensions_clear))
    print(f'Список невідомих розширень: {lst_unknown_extensions_clear}')
    print(f'Список відомих розширень: {lst_known_extensions_clear}')


def normalize():
    """Перейменовує файли та папки"""

    for key, value in dict_extensions.items():
        if key == 'unknown':
            pass
        if key == 'images' or key == 'videos' or key == 'documents' or key == 'music' or key == 'archives':
            lst = value
            for i in lst:
                way = i
                # Виділимо ім'я файла зі шляху (from os.path import basename)
                file_name = basename(way)  # os.basename
                len_file_name = len(file_name)
                new_file_name = translate(file_name)  # add 'file_name'

                way_without_file_name = way[:-len_file_name]
                file_oldname = os.path.join(way_without_file_name, file_name)
                file_newname = os.path.join(way_without_file_name, new_file_name)
                os.rename(file_oldname, file_newname)

    # Для того, щоб не було конфлікту, виносимо перейменування папок в окремий цикл
    for key, value in dict_extensions.items():
        if key == 'folders':  # Перейменування папок
            lst = value
            for i in lst:
                name_re = re.findall(r"[^\\]+$", str(i))
                # витягнемо їм'я зі списку
                name = name_re[0]
                new_name = translate(name)
                # Рекурсивний пошук директорій
                items = list(Path('.').rglob(name))
                # Якщо теку знайдено
                if items:
                    path = items[0]
                    path.rename(path.parent / new_name)


def translate(name):
    """Виконує транслітерацію назв папок та файлів"""

    wrong_simbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ!@#$%^&*() -=+'"
    trans_map = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_')
    trans = {}
    for c, l in zip(wrong_simbols, trans_map):
        trans[ord(c)] = l
        trans[ord(c.upper())] = l.upper()
    new_name = name.translate(trans)
    return (new_name)

# ----------------------------------------------
def removing_files(path):
    """
    Переміщає файли по папках, розпаковує архіви.
    У випадку натрапляння на дублікат, він пропускається
    """

    # 1. Оновимо список всіх файлів зі шляхами після перейменування
    lst_ranamed_files = files_addresses(path)
    # print(lst_ranamed_files)
    # Розділемо файли на списки по розширенням
    lst_images = []
    lst_videos = []
    lst_documents = []
    lst_music = []
    lst_archives = []
    lst_unknown = []

    for i in lst_files_addresses:

        images_result = re.findall(r"([^/]+[/.](jpeg|png|jpg|svg|bmp))", str(i))
        if len(images_result) > 0:
            for i in images_result:
                lst_images.append(i[0])
        lst_images = list(set(lst_images))

        videos_result = re.findall(r"([^/]+[/.](avi|mp4|mov|mkv))", str(i))
        if len(videos_result) > 0:
            for i in videos_result:
                lst_videos.append(i[0])
        lst_videos = list(set(lst_videos))

        documents_result = re.findall(r"([^/]+[/.](doc|docx|txt|pdf|xlsx|pptx))", str(i))
        # присутня системна помилка щодо розширення ".docx" (чомусь у список "lst_known" воно потрапляє без "x")
        if len(documents_result) > 0:
            for i in documents_result:
                lst_documents.append(i[0])
            lst_documents = list(set(lst_documents))

        music_result = re.findall(r"([^/]+[/.](mp3|ogg|wav|amr))", str(i))
        if len(music_result) > 0:
            for i in music_result:
                lst_music.append(i[0])
            lst_music = list(set(lst_music))

        archives_result = re.findall(r"([^/]+[/.](zip|gz|rar|tar))", str(i))
        if len(archives_result) > 0:
            for i in archives_result:
                lst_archives.append(i[0])
            lst_archives = list(set(lst_archives))

    lst_unknown = list(set(lst_files_addresses)
                       - set(lst_images)
                       - set(lst_videos)
                       - set(lst_documents)
                       - set(lst_music)
                       - set(lst_archives))  # визначаємо через множини невідомі розширення

    # print(lst_images)
    # print(lst_videos)
    # print(lst_documents)
    # print(lst_music)
    # print(lst_archives)
    # print(lst_unknown)

    # Створимо необхідні папки в цільовій папці
    # print(str(path))
    if len(lst_images) > 0:
        new_folder = str(path) + '\\images'
        try:  # Якщо папка вже існує, завдяки try, не буде помилки
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    if len(lst_videos) > 0:
        new_folder = str(path) + '\\video'
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    if len(lst_documents) > 0:
        new_folder = str(path) + '\\documents'
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    if len(lst_music) > 0:
        new_folder = str(path) + '\\audio'
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    if len(lst_archives) > 0:
        new_folder = str(path) + '\\archives'
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    if len(lst_unknown) > 0:
        new_folder = str(path) + '\\unknown'
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

    # 2. Перемістимо файли та розпакуємо архіви у теку archives

    if len(lst_images) > 0:
        for way in lst_images:
            # Виділимо ім'я файла зі шляху (from os.path import basename)
            file_name = basename(way)  # os.basename
            # Виділимо шлях до файлу
            len_file_name = len(file_name)
            way_without_file_name = way[:-len_file_name]
            new_way = str(path) + '\\images'
            file_old_place = os.path.join(way_without_file_name, file_name)
            file_new_place = os.path.join(new_way, file_name)
            try:  # Якщо такий файл вже існує, його дублікат не переноситься, а залишається на старому місці
                os.rename(file_old_place, file_new_place)
            except FileExistsError:
                pass
    print('Images removed!')

    if len(lst_videos) > 0:
        for way in lst_videos:
            # Виділимо ім'я файла зі шляху (from os.path import basename)
            file_name = basename(way)  # os.basename
            # Виділимо шлях до файлу
            len_file_name = len(file_name)
            way_without_file_name = way[:-len_file_name]
            new_way = str(path) + '\\video'
            file_old_place = os.path.join(way_without_file_name, file_name)
            file_new_place = os.path.join(new_way, file_name)
            try:  # Якщо такий файл вже існує, його дублікат не переноситься, а залишається на старому місці
                os.rename(file_old_place, file_new_place)
            except FileExistsError:
                pass
    print('Video removed!')

    if len(lst_documents) > 0:
        for way in lst_documents:
            # Виділимо ім'я файла зі шляху (from os.path import basename)
            file_name = basename(way)  # os.basename
            # Виділимо шлях до файлу
            len_file_name = len(file_name)
            way_without_file_name = way[:-len_file_name]
            new_way = str(path) + '\\documents'
            file_old_place = os.path.join(way_without_file_name, file_name)
            file_new_place = os.path.join(new_way, file_name)
            try:  # Якщо такий файл вже існує, його дублікат не переноситься, а залишається на старому місці
                os.rename(file_old_place, file_new_place)
            except FileExistsError:
                pass
    print('Documents removed!')

    if len(lst_music) > 0:
        for way in lst_music:
            # Виділимо ім'я файла зі шляху (from os.path import basename)
            file_name = basename(way)  # os.basename
            # Виділимо шлях до файлу
            len_file_name = len(file_name)
            way_without_file_name = way[:-len_file_name]
            new_way = str(path) + '\\audio'
            file_old_place = os.path.join(way_without_file_name, file_name)
            file_new_place = os.path.join(new_way, file_name)
            try:  # Якщо такий файл вже існує, його дублікат не переноситься, а залишається на старому місці
                os.rename(file_old_place, file_new_place)
            except FileExistsError:
                pass
    print('Audio removed!')

    if len(lst_archives) > 0:
        # print(lst_archives)
        for way in lst_archives:
            new_way = str(path) + '\\archives'
            shutil.unpack_archive(way, new_way)
            os.remove(way)
    print('Archives unpacked and removed!')

    if len(lst_unknown) > 0:
        for way in lst_unknown:
            # Виділимо ім'я файла зі шляху (from os.path import basename)
            file_name = basename(way)  # os.basename
            # Виділимо шлях до файлу
            len_file_name = len(file_name)
            way_without_file_name = way[:-len_file_name]
            new_way = str(path) + '\\unknown'
            file_old_place = os.path.join(way_without_file_name, file_name)
            file_new_place = os.path.join(new_way, file_name)
            try:  # Якщо такий файл вже існує, його дублікат не переноситься, а залишається на старому місці
                os.rename(file_old_place, file_new_place)
            except FileExistsError:
                pass
    print('Unknown removed!')


def del_empty_folders(path):
    """Видаляє порожні теки"""

    for d in os.listdir(path):  # os.listdir(path) надає список тек у цільовій теці
        if d != 'images' and d != 'video' and d != 'documents' and d != 'audio' and d != 'archives' and d != 'unknown':
            a = os.path.join(path, d)  # Створює шлях до теки, поєднуючи назву теки з назвою цільової теки
            if os.path.isdir(a):  # Метод перевіряє, чи існує такий каталог
                del_empty_folders(a)
                if not os.listdir(a):  # Надає список файлів та папок в теці 'a'
                    os.rmdir(a)  # Видаляє об'єкт 'a'
                    print(a, 'deleted!')

# __________________________________________
def main():
    """.................................."""

    path = Path(sys.argv[1])   # дає можливість запуску з терміналу "python clean.py Test"
    if path.exists():
        files_addresses(path)
        folders_addresses(path)
        folders_addresses_in_dict()
        sort_extensions()
        known_or_not_extensions()
        normalize()
        removing_files(path)
        del_empty_folders(path)
    else:
        print(f'{path.absolute()} is not exists!')


if __name__ == '__main__':
    main()
