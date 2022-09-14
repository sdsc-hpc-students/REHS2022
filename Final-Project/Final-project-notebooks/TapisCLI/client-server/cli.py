import socket
import argparse
import sys
import json
import pyfiglet
from getpass import getpass
import threading


class CLI:
    def __init__(self):
        self.username, self.password = None, None
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.connect()

        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser")
        self.parser.add_argument('command_group')
        self.parser.add_argument('-c', '--command')
        self.parser.add_argument('-i', '--id')
        self.parser.add_argument('-t', '--template')
        self.parser.add_argument('-u', '--username')
        self.parser.add_argument('-L', '--level')
        self.parser.add_argument('-v', '--version')
        self.parser.add_argument('-F', '--file')
        self.parser.add_argument('-n', '--name')
        self.parser.add_argument('--uuid')
        self.parser.add_argument('-d', '--destination')
        self.parser.add_argument('-p', '--password')

    def json_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(bytes((json_data), ('utf-8')))

    def json_receive(self):
        json_data = ""
        while True:
            try: #to handle long files, so that it continues to receive data and create a complete file
                json_data = json_data + self.connection.recv(1024).decode('utf-8') #formulate a full file. Combine sequential data streams to unpack
                return json.loads(json_data) #this is necessary whenever transporting any large amount of data over TCP streams
            except ValueError:
                continue

    def connect(self):
        self.connection.connect(('127.0.0.1', 3003))
        connection_type = self.json_receive()
        if connection_type['type'] == 'initial':
            self.username = str(input('enter your TACC username: '))
            self.password = getpass('enter your TACC password: ')
            self.json_send({
            "username":self.username,
            "password":self.password
            })
            start_data = self.json_receive()
            self.url = start_data['url']
        
    def process_command(self, command):
        command = command.split(' ')

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided
            try:
                kwargs = parser.parse_args()
            except e:
                print(e)
                sys.exit(1)
            self.json_send({"end_state":"exit", "message":kwargs})
            results = self.json_receive()
            print(results)
            sys.exit(0)

        title = pyfiglet.figlet_format("Tapiconsole", font="slant")
        print(title)
        
        while True:
            command_input = self.process_command(str(input(f"[{self.username}@{self.url}] ")))
            self.json_send(command_input)
            results = self.json_receive()
            print(results)


if __name__ == "__main__":
    try:
        client = CLI()
    except Exception as e:
        print(e)
        print('Invalid login, try again')
        sys.exit(1)
    client.main()