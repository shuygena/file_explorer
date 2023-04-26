import glob
from os import path
from dateutil.parser import parse


def validate_dict(size_time):
    operators = ['eq', 'lt', 'gt', 'le', 'ge']
    if len(size_time) != 2:
        return False
    if 'value' not in size_time or 'operator' not in size_time:
        return False
    if (isinstance(size_time['value'], str) and
            isinstance(size_time['operator'], str)) is False:
        return False
    if len(size_time['value']) == 0:
        return False
    if size_time['operator'] not in operators:
        return False
    return True


def validate(search_query):
    if 'file_mask' not in search_query:
        return False
    if isinstance(search_query['file_mask'], str) is False:
        return False
    if len(search_query['file_mask']) == 0:
        return False
    if 'size' in search_query:
        if validate_dict(search_query['size']) is False:
            return False
        if search_query['size']['value'].isdigit() is False:
            return False
    if 'creation_time' in search_query:
        if validate_dict(search_query['creation_time']) is False:
            return False
        try:
            parse(search_query['creation_time']['value'])
        except Exception:
            return False
    if 'text' in search_query:
        if isinstance(search_query['text'], str) is False:
            return False
    search_params = set(search_query.keys())
    valid_params = {'file_mask', 'text', 'size', 'creation_time'}
    if len(search_params - valid_params) > 0:
        return False
    return True


def find_file(file_mask, directory, text, size, creation_time):
    """
    Функция для поиска файла в указанном каталоге по заданным фильтрам.
    :param file_mask: маска имени файла в формате glob
    :param directory: путь к каталогу
    :param text: строка для поиска в содержимом файла (опционально)
    :param size: словарь с ключами 'value' и 'operator' для фильтрации по
        размеру файла (опционально)
    :param creation_time: словарь с ключами 'value', 'operator' и 'timezone'
        для фильтрации по времени создания файла (опционально)
    :return: список найденных файлов
    """
    # Собираем путь к файлу с учетом маски имени файла
    file_path = path.join(directory, file_mask)
    # Ищем все файлы, соответствующие маске имени файла
    files = glob.glob(file_path)

    # Фильтруем файлы по содержимому
    if text:
        new_files = list()
        for f in files:
            with open(f, 'r+', encoding='utf-8', errors='ignore') as content:
                if text in content.read():
                    new_files.append(f)
        files = new_files

    # Фильтруем файлы по размеру
    if size:
        operator = size['operator']
        value = int(size['value'])
        if operator == 'eq':
            files = [f for f in files if path.getsize(f) == value]
        elif operator == 'gt':
            files = [f for f in files if path.getsize(f) > value]
        elif operator == 'lt':
            files = [f for f in files if path.getsize(f) < value]
        elif operator == 'ge':
            files = [f for f in files if path.getsize(f) >= value]
        elif operator == 'le':
            files = [f for f in files if path.getsize(f) <= value]

    # Фильтруем файлы по времени создания
    if creation_time:
        operator = creation_time['operator']
        value = parse(creation_time['value'])
        timezone = creation_time.get('timezone', None)
        if timezone:
            value = value.astimezone(timezone)
        cmp_val = value.timestamp()
        if operator == 'eq':
            files = [f for f in files if path.getctime(f) == cmp_val]
        elif operator == 'gt':
            files = [f for f in files if path.getctime(f) > cmp_val]
        elif operator == 'lt':
            files = [f for f in files if path.getctime(f) < cmp_val]
        elif operator == 'ge':
            files = [f for f in files if path.getctime(f) >= cmp_val]
        elif operator == 'le':
            files = [f for f in files if path.getctime(f) <= cmp_val]

    return files
