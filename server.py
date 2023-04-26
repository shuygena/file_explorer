import asyncio
import json
import hashlib
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from utils import find_file, validate


hostname = "127.0.0.1"
port = 8000
server_address = hostname, port


# Создаем класс для обработки запросов
class RequestHandler(BaseHTTPRequestHandler):
    # Статический словарь для хранения результатов поиска
    search_results = {}

    def send_good_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def send_bad_response(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_POST(self):
        # Обрабатываем запрос на поиск
        if self.path == "/search":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            search_query = json.loads(post_data)
            # Валидация параметров поиска
            if validate(search_query) is True:
                self.send_good_response()
                search_id = self.create_new_id()
                self.search_results[search_id] = {'finished': False}
                asyncio.run(self.create_new_search(search_id, search_query))
                response_data = {'search_id': search_id}
                self.wfile.write(json.dumps(response_data).encode())
            else:
                self.send_bad_response()
                self.wfile.write(b'Invalid parametrs in search query')
        else:
            self.send_bad_response()
            self.wfile.write(b'Invalid request')

    # Cоздание нового search_id
    def create_new_id(self):
        search_counter = len(self.search_results) + 1
        hm = str(search_counter).encode('utf-8')
        m = hashlib.md5(hm)
        search_id = str(m.hexdigest())
        return search_id

    # Поиск файла
    async def create_new_search(self, search_id, search_query):
        file_mask = search_query['file_mask']
        directory = ''
        if len(sys.argv) == 2:
            directory += sys.argv[1]
        text = None
        if 'text' in search_query:
            text = search_query['text']
        size = None
        if 'size' in search_query:
            size = search_query['size']
        creation_time = None
        if 'creation_time' in search_query:
            creation_time = search_query['creation_time']
        files = find_file(file_mask, directory, text, size, creation_time)
        self.search_results[search_id] = {'finished': True, 'paths': files}

    def do_GET(self):
        # Обрабатываем запрос на выдачу результата поиска
        if self.path[:8] == '/search/':
            search_id = self.path[8:]
            if search_id not in self.search_results:
                self.send_bad_response()
                self.wfile.write(b'Invalid search ID')
            else:
                # Если search_id существует, то отправляем результат поиска
                response = self.search_results[search_id]
                self.send_good_response()
                self.wfile.write(json.dumps(response).encode())
        elif self.path == '/favicon.ico':
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')
        else:
            self.send_bad_response()
            self.wfile.write(b'Invalid request')


if __name__ == "__main__":
    server = HTTPServer(server_address, RequestHandler)
    print()
    print(f"Сервер запущен http://{hostname}:{port}")
    server.serve_forever()
