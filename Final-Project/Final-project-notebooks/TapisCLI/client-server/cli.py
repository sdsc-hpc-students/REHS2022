import socket
import argparse
from argparse import SUPPRESS
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

        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=SUPPRESS)
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
        self.parser.add_argument('-d', '--description')
        self.parser.add_argument('-p', '--password')
        self.parser.add_argument('-e', '--expression')

        self.password_commands = ['system_password_set']
        self.confirmation_commands = ['restart_pod', 'delete_pod']
        self.subclients = ['neo4j']

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
        count = 1
        timeout_time = time.time() + 30
        while True:
            if time.time() > timeout_time:
                sys.stdout.write("\r[-] Connection timeout")
                os._exit(0)
            try:
                self.connection.connect((self.ip, self.port))
                break
            except Exception as e:
                if not flag:
                    startup = threading.Thread(target=self.initialize_server)
                    startup.start()
                    flag = True
                    continue
                else:
                    sys.stdout.write(f'\r[+] Starting Server{"."*count}')
                    sys.stdout.flush()
                    if count == 3:
                        count = 1
                    else:
                        count += 1
                    continue

    def connect(self):
        self.connection_initialization()
        #self.connection.connect((self.ip, self.port)) # enable me for debugging
        connection_info = self.json_receive()
        if connection_info['connection_type'] == "initial": # if the server is receiving its first connection for the session\
            while True:
                username = str(input("\nUsername: ")) # take the username
                password = getpass("Password: ") # take the password
                self.json_send({"username":username, "password":password}) # send the username and password to the server to be used
                verification = self.json_receive()
                if verification[0]:
                    print("[+] verification success")
                    break
                else:
                    print("[-] verification failure")
                    if verification[1] == 3:
                        sys.exit(0)
                    continue

            url = self.json_receive() # receive the url
            return username, url # return the username and url

        elif connection_info['connection_type'] == 'continuing': # if it is not the first connection to the session
            username, url = connection_info['username'], connection_info['url'] # receive username and URL
            return username, url # return username and url

    def process_command(self, command):
        command = command.split(' ')
        return command

    def expression_input(self):
        print("Enter 'exit' to submit")
        expression = ''
        while True:
            line = str(input("> "))
            if line == 'exit':
                break
            expression += line
        return expression

    def check_command(self, **kwargs):
        command = kwargs['command']
        if command in self.password_commands:
            kwargs['password'] = getpass(f"{command} password: ")
        elif command in self.confirmation_commands:
            decision = str(input("Are you sure? y/n\n"))
            if decision != 'y':
                return False
        elif kwargs['command_group'] in self.subclients and not kwargs['file']:
            kwargs['expression'] = self.expression_input()
            
        return kwargs

    def command_operator(self, kwargs, exit_=False):
        if isinstance(kwargs, list):
            try:
                kwargs = vars(self.parser.parse_args(kwargs))
            except:
                raise Exception("[-] Invalid Arguments")
        if not kwargs['command_group']:
            return False
        
        kwargs = self.check_command(**kwargs)
        if not kwargs:
            raise Exception("[-] Confirmation not given. Command not executed")
        self.json_send({'kwargs':kwargs, 'exit':exit_})
        
        result = self.json_receive()
        return result

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided
            try:
                kwargs = self.parser.parse_args()
                kwargs = vars(kwargs)
                result = self.command_operator(kwargs, exit_=True)
                if isinstance(result, dict):
                    pprint(result)
                else:
                    print(result)
            except Exception as e:
                print(e)
            sys.exit(0)

        title = pyfiglet.figlet_format("Tapiconsole", font="slant")
        print(title)
        
        while True:
            try:
                kwargs = self.process_command(str(input(f"[{self.username}@{self.url}] ")))
                result = self.command_operator(kwargs)
                if not result:
                    continue
                if result == '[+] Exiting' or result == '[+] Shutting down':
                    print(result)
                    os._exit(0)
                if isinstance(result, dict):
                    pprint(result)
                    continue
                print(result)
            except KeyboardInterrupt:
                pass
            except WindowsError:
                raise ConnectionError("[-] Connection was dropped. Exiting")
            except Exception as e:
                 print(e)


if __name__ == "__main__":
    try:
        client = CLI('127.0.0.1', 3000)
    except Exception as e:
        print(e)
        print('[-] Invalid login, try again')
        sys.exit(1)
    client.main()