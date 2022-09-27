import socket
import argparse
import sys
import json
import pyfiglet
from getpass import getpass
import threading


class CLI:
    def __init__(self, IP, PORT):
        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.username, self.url = self.connect()

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
        self.connection.connect((self.ip, self.port))
        connection_type = self.json_receive() # receive information about the connection type. Initial or continuing?
        if connection_type == "initial": # if the server is receiving its first connection for the session
            username = str(input("Username: ")) # take the username
            password = getpass("Password: ") # take the password
            self.json_send({"username":username, "password":password}) # send the username and password to the server to be used
            url = self.json_receive() # receive the url
            return username, url # return the username and url

        elif connection_type == "continuing": # if it is not the first connection to the session
            connection_info = self.json.receive() # receive connection info. No need to send password and username
            username, url = connection_info['username'], connection_info['url'] # receive username and URL
            return username, url # return username and url

    def process_command(self, command):
        command = command.split(' ')
        return command

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided
            try:
                kwargs = self.parser.parse_args()
                self.json_send(kwargs)
                result = self.json_receive()
                print(result)
            except e:
                print(e)
                sys.exit(1)
            sys.exit(0)

        title = pyfiglet.figlet_format("Tapiconsole", font="slant")
        print(title)
        
        while True:
            command_input = self.process_command(str(input(f"[{self.username}@{self.url}] ")))
            print(command_input)
            command_input = self.parser.parse_args(command_input)
            self.json_send(command_input)
            results = self.json_receive()
            print(results)


if __name__ == "__main__":
    try:
        client = CLI('127.0.0.1', 3000)
    except Exception as e:
        print(e)
        print('Invalid login, try again')
        sys.exit(1)
    client.main()