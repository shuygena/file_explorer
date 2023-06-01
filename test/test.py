import requests
import json
from subprocess import check_output

CROSS = '❌'
CHECK = '✅'
URL = 'http://localhost:8000'
HEADERS = {'Content-type': 'application/json'}
test_counter = 0


def print_result(result):
    global test_counter
    test_counter += 1
    sign = CHECK if result is True else CROSS
    print('Test {:2d}: {}'.format(test_counter, sign))


def test_params(search_query):
    url = URL + '/search'
    data = json.dumps(search_query)
    response = requests.post(url, data=data, headers=HEADERS)
    if response.status_code == 400:
        if response.text == 'Invalid parametrs in search query':
            return True
    return False


def test_post_path(path):
    url = URL + path
    data = json.dumps({'file_mask': '*'})
    response = requests.post(url, data=data, headers=HEADERS)
    if response.status_code == 400:
        if response.text == 'Invalid request':
            return True
    return False


def test_bad_id(id):
    url = URL + '/search/' + id
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 400:
        if response.text == 'Invalid search ID':
            return True
    return False


def test_get_path(path):
    url = URL + path
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 400:
        if response.text == 'Invalid request':
            return True
    return False


def test_favicon():
    url = URL + '/favicon.ico'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        if response.text == 'Not found':
            return True
    return False


def test_bad_post_request():
    print('==============================')
    print('Test bad POST requests')
    print('==============================')
    # Некорректные параметры для поиска файла
    querys = [{'file_mask': '*', 
               'size': {'value': 'lol', 'operator': 'lt'}},
                {'file_mask': '*', 'size': {}},
                {'file_mask': '*', 'creation_time': {}},
                {'file_mask': '*', 'text': ['121']},
                {'file_mask': ['*']},
                {'file_mask': '*',
                    'creation_time': {'value': '2023-04-23T19:00:54Z'}},
                {'file_mask': '*',
                    'creation_time': {'value': '2023-04-23T19:00:54Z',
                                        'operator': 'kek'}},
                {'creation_time': {'value': '2023-04-23T19:00:54Z',
                                    'operator': 'le'}},
                {'file_mask': '*', 'lorem impsum': '10'},
                {'file_mask': ''}]
    for search_query in querys:
        print_result(test_params(search_query))
    url_paths = ['/search/1', '/get', '/post', '/search/', '/blabla']
    for path in url_paths:
        print_result(test_post_path(path))


def test_bad_get_request():
    print('==============================')
    print('Test bad GET requests')
    print('==============================')
    search_id = ['eccbc8754dasfad243308fd9f2a7baf3', '1', 'lol', '2']
    for id in search_id:
        print_result(test_bad_id(id))
    url_paths = ['/search', '/get', '/post', '/', '/blabla']
    for path in url_paths:
        print_result(test_get_path(path))
    print_result(test_favicon())


def test_size(value):
    url = URL + '/search'
    search_query = {'file_mask': 'l*',
                    'size': {'value': value,
                             'operator': 'lt'}}
    data = json.dumps(search_query)
    response = requests.post(url, data=data, headers=HEADERS)
    result1 = check_output(['find', 'tests/', '-name', 'l*', '-size',
                            '-'+value+'c', '-type', 'f']).decode('utf-8')
    if response.status_code == 200:
        id = response.json().get('search_id')
        response = requests.get(url+'/'+id, headers=HEADERS)
        if response.status_code == 200:
            if response.json().get('finished') is False:
                return True
            if response.json().get('finished') is True:
                if result1 == '':
                    files1 = set()
                else:
                    files1 = set(result1.strip().split('\n'))
                files2 = set(response.json().get('paths'))
                if files1 == files2:
                    return True
    return False


def test_file_mask(file):
    url = URL + '/search'
    search_query = {'file_mask': file}
    data = json.dumps(search_query)
    response = requests.post(url, data=data, headers=HEADERS)
    result1 = check_output(['find', 'tests/', '-name', file, '-type',
                            'f']).decode('utf-8')
    if response.status_code == 200:
        id = response.json().get('search_id')
        response = requests.get(url+'/'+id, headers=HEADERS)
        if response.status_code == 200:
            if response.json().get('finished') is False:
                return True
            if response.json().get('finished') is True:
                if result1 == '':
                    files1 = set()
                else:
                    files1 = set(result1.strip().split('\n'))
                files2 = set(response.json().get('paths'))
                if files1 == files2:
                    return True
    return False


def test_time(time):
    url = URL + '/search'
    search_query = { 'file_mask': '*',
                    'creation_time': {'value': time, 'operator': 'gt'}}
    data = json.dumps(search_query)
    response = requests.post(url, data=data, headers=HEADERS)
    result1 = check_output([
        'find', 'tests/', '-name', '*', '-type', 'f',
        '-newermt', time[:10]]).decode('utf-8')
    if response.status_code == 200:
        id = response.json().get('search_id')
        response = requests.get(url+'/'+id, headers=HEADERS)
        if response.status_code == 200:
            if response.json().get('finished') is False:
                return True
            if response.json().get('finished') is True:
                if result1 == '':
                    files1 = set()
                else:
                    files1 = set(result1.strip().split('\n'))
                files2 = set(response.json().get('paths'))
                if files1 == files2:
                    return True
    return False


def test_text(query):
    url = URL + '/search'
    data = json.dumps(query)
    response = requests.post(url, data=data, headers=HEADERS)
    result1 = check_output([
        'find', 'tests/', '-name', query['file_mask'], '-type', 'f',
        '-exec', 'grep', '-l', query['text'], '{}', '+']).decode('utf-8')
    if response.status_code == 200:
        id = response.json().get('search_id')
        response = requests.get(url+'/'+id, headers=HEADERS)
        if response.status_code == 200:
            if response.json().get('finished') is False:
                return True
            if response.json().get('finished') is True:
                if result1 == '':
                    files1 = set()
                else:
                    files1 = set(result1.strip().split('\n'))
                files2 = set(response.json().get('paths'))
                if files1 == files2:
                    return True
    return False


def test_post_get():
    print('==============================')
    print('Test POST AND GET requests')
    print('==============================')
    file_masks = ['*', 't*' '*t', 'lo*' '*jpeg', '*.*', '*c*',
                  'log*', '*py', '*1*', 'not', '*.py']
    for file in file_masks:
        print_result(test_file_mask(file))
    size = ['50', '100', '500', '1024', '10024']
    for value in size:
        print_result(test_size(value))
    pairs = [{'file_mask': '*lo', 'text': 'main'},
             {'file_mask': '*', 'text': 'text'},
             {'file_mask': '*', 'text': 'Hello'},
             {'file_mask': '*py', 'text': 'main'},
             {'file_mask': '*', 'text': 'lol'}]
    for query in pairs:
        print_result(test_text(query))
    times = ['2023-04-19T00:00:54Z']
    for time in times:
        print_result(test_time(time))


if __name__ == "__main__":
    test_bad_post_request()
    test_bad_get_request()
    test_post_get()
