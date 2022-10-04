import socket
import argparse
import sys
import json
import pyfiglet
from getpass import getpass
import threading
import os
import time
from pprint import pprint


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

    def initialize_server(self):
        if 'win' in sys.platform:
            os.system(r"pythonw C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\server.py")
        else:
            os.system(r"python C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\server.py &")

    def connection_initialization(self):
        flag = False
        while True:
            try:
                print("Attempting to connect")
                self.connection.connect((self.ip, self.port))
                print("Initial connection success!")
                break
            except Exception as e:
                print(e)
                if not flag:
                    print("Starting server...")
                    startup = threading.Thread(target=self.initialize_server)
                    startup.start()
                    print("Server startup initialized")
                    flag = True
                    continue
                else:
                    print("Connection failed...")
                    continue
        print("Moving on")

    def connect(self):
        self.connection_initialization()
        #self.connection.connect((self.ip, self.port))
        print("Connected")
        connection_type = self.json_receive() # receive information about the connection type. Initial or continuing?
        print(connection_type)
        if connection_type == "initial": # if the server is receiving its first connection for the session\
            while True:
                username = str(input("Username: ")) # take the username
                password = getpass("Password: ") # take the password
                self.json_send({"username":username, "password":password}) # send the username and password to the server to be used
                verification = self.json_receive()
                if verification[0]:
                    print("verification success")
                    break
                else:
                    print("verification failure")
                    print(verification)
                    if verification[1] == 3:
                        sys.exit(0)
                    continue

            url = self.json_receive() # receive the url
            return username, url # return the username and url

        elif connection_type == "continuing": # if it is not the first connection to the session
            connection_info = self.json_receive() # receive connection info. No need to send password and username
            username, url = connection_info['username'], connection_info['url'] # receive username and URL
            return username, url # return username and url

    def process_command(self, command):
        command = command.split(' ')
        return command

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided
            try:
                kwargs = vars(self.parser.parse_args())
                self.json_send({'kwargs':kwargs, 'exit':True})
                result = self.json_receive()
                print(result)
            except e:
                print(e)
                sys.exit(1)
            sys.exit(0)

        title = pyfiglet.figlet_format("Tapiconsole", font="slant")
        print(title)
        
        while True:
            try:
                command_input = self.process_command(str(input(f"[{self.username}@{self.url}] ")))
                command_input = vars(self.parser.parse_args(command_input))
                print(command_input)
                print(type(command_input))
                self.json_send({'kwargs':command_input, 'exit':False})
                results = self.json_receive()
                if results == 'exiting' or results == 'shutting down':
                    os._exit(0)
                pprint(results)
            except KeyboardInterrupt:
                pass
            except WindowsError:
                os._exit(0)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    try:
        client = CLI('127.0.0.1', 3000)
    except Exception as e:
        print(e)
        print('Invalid login, try again')
        sys.exit(1)
    client.main()