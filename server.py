import socket
from datetime import datetime
import json
import logging
import urllib.parse


def run_socket_server():
    ip = socket.gethostname()
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))

    while True:
        msg, address = server_socket.recvfrom(1024)
        msg = msg.decode()
        save_message_to_json(msg)


def save_message_to_json(message):
    message = urllib.parse.unquote_plus(message)
    try:
        parse_dict = {
            key: value for key, value in [el.split('=') for el in message.split('&')]
        }
        timestamp = datetime.now().isoformat()
        message_dict = {timestamp: parse_dict}
        with open('storage/data.json', 'a+', encoding='utf-8') as file:
            file.seek(0)
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

            data.update(message_dict)
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write('\n')

    except ValueError as err:
        logging.error(err)
    except OSError as err:
        logging.error(err)


if __name__ == '__main__':
    run_socket_server()