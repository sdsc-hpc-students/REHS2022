import pyfiglet
import argparse
import sys
from getpass import getpass
import time
import re
from tapipy.tapis import Tapis
import socket
import json
import threading
import multiprocessing
from killable_thread import ServerThread

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from pods import Pods, Neo4jCLI
from systems import Systems
from files import Files
from apps import Apps


class Server:
    def __init__(self):
        print("[+] Started")
        ip_port = ('127.0.0.1', 3003)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(ip_port)
        self.sock.listen(1)
        self.connection, ip_port = self.sock.accept()
        self.json_send({"type":"initial"})

        creds = self.json_receive()
        self.username, self.password = creds['username'], creds['password']
        while True:
            start = time.time()
            base_url = "https://icicle.develop.tapis.io"
            try:
                self.t = Tapis(base_url = base_url,
                        username = self.username,
                        password = self.password)
                self.t.get_tokens()
                break
            except Exception as e:
                print(f"\nBROKEN! timeout: {time.time() - start}\n")

        # V3 Headers
        header_dat = {"X-Tapis-token": self.t.access_token.access_token,
                    "Content-Type": "application/json"}

        # Service URL
        self.url = f"{base_url}/v3"

        print(time.time() - start)
        print(f"base_url: {base_url}")
        print(f"serv_url: {self.url}\n")

        # create authenticator for tapis systems
        self.authenticator = self.t.access_token
        self.access_token = re.findall(r'(?<=access_token: )(.*)', str(self.authenticator))[0]
        print(self.authenticator)

        self.json_send({"url":self.url
        })

        self.pods = Pods(self.t, self.username, self.password)
        self.systems = Systems(self.t, self.username, self.password)
        self.files = Files(self.t, self.username, self.password)
        self.apps = Apps(self.t, self.username, self.password)
        self.neo4j = Neo4jCLI(self.t, self.username, self.password)
        print("inited")

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

    def post_start_connect(self):
        self.connection.close()
        self.connection, ip_port = self.sock.accept()
        self.json_send({"type":"continuing"})

    def process_command(self, command):
        command = command.split(' ')

    def run_command(self, **kwargs):
        try:
            if kwargs['command_group'] == 'pods':
                return self.pods.pods_cli(**kwargs)
            elif kwargs['command_group'] == 'systems':
                return self.systems.systems_cli(**kwargs)
            elif kwargs['command_group'] == 'files':
                return self.files.files_cli(**kwargs)
            elif kwargs['command_group'] == 'apps':
                return self.apps.apps_cli(**kwargs)
            elif kwargs['command_group'] == 'help':
                with open(r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems\help.json', 'r') as f:
                    return json.loads(f)
            else:
                return "Failed"
        except Exception as e:
            return e

    def main(self):
        while True: # checks if any command line arguments were provided
            try:
                print("waiting on a message")
                kwargs = self.json_receive()
                print(kwargs)
                print("message received")
                self.json_send(self.run_command(**kwargs))
            except (ConnectionResetError, ConnectionAbortedError, ConnectionError, OSError, WindowsError, socket.error) as e:
                print("connection was ass fucked. Trying again")
                self.post_start_connect()
                print(e)
            except Exception as e:
                print("anal fucking avoided, but something else happened. Fix it, asshole")
                self.json_send("Command failed, see help")
                print(e)


if __name__ == '__main__':
    server = Server()
    server.main()