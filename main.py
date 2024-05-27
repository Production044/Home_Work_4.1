from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import threading


def send_to_socket_server(data):
    # Отправка данных на Socket сервер с использованием UDP
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.gethostname()
        server_address = (ip, 5000)

        # Отправка данных на сервер
        client_socket.sendto(data, server_address)
        print(f'Отправил {data} на {server_address}')
        client_socket.close()
    except Exception as e:
        print(f"Ошибка отправки данных на socket сервер: {e}")


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Розбираємо URL запиту
        pr_url = urllib.parse.urlparse(self.path)
        # Якщо URL - кореневий, відправляємо сторінку index.html
        if pr_url.path == '/':
            self.send_html_file('index.html')
        # Якщо URL - '/message', відправляємо сторінку message.html
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            # Якщо URL не співпадає з жодним із визначених, перевіряємо чи існує відповідний статичний файл
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            # Якщо файл не знайдено, відправляємо сторінку error.html зі статусом 404
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        # Обробляємо POST запити, які надійшли від форми на сторінці message.html
        # Отримуємо дані з POST запиту
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Відправляємо відповідь на POST запит
        self.send_response(302)
        self.send_header('Location', 'message')
        self.end_headers()
        # Відправляємо дані на Socket сервер
        send_to_socket_server(post_data)

    def send_html_file(self, filename, status=200):
        # Відправляємо HTML файл з вказаним ім'ям
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        # Відправляємо статичний файл, якщо він існує
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    # Запускаємо HTTP сервер
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    print(f"Starting HTTP server at {server_address}")
    try:
        http.serve_forever() # Прослуховуємо на запити безкінечно
    except KeyboardInterrupt:
        http.server_close()
        print("\nHTTP server stopped.")


if __name__ == '__main__':
    # Запускаємо HTTP сервер у окремому потоці
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()