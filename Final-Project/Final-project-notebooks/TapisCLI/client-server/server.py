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
from killable_thread import k_thread
import os

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from pods import Pods, Neo4jCLI
from systems import Systems
from files import Files
from apps import Apps


class Server:
    def __init__(self, IP, PORT):
        print("[+] Started")
        self.ip, self.port = IP, PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.connection = None
        self.end_time = time.time() + 300
        
        while True:
            try:
                print("waiting for connection")
                self.username, self.password, self.t, self.url, self.access_token = self.accept(initial=True)
                break
            except Exception as e:
                print(e)
                continue

        self.pods = Pods(self.t, self.username, self.password)
        self.systems = Systems(self.t, self.username, self.password)
        self.files = Files(self.t, self.username, self.password)
        self.apps = Apps(self.t, self.username, self.password)
        self.neo4j = Neo4jCLI(self.t, self.username, self.password)
        print("inited")

    def tapis_init(self, username, password):
        while True:
            start = time.time()
            base_url = "https://icicle.develop.tapis.io"
            try:
                t = Tapis(base_url = base_url,
                        username = username,
                        password = password)
                t.get_tokens()
                break
            except Exception as e:
                print(f"\nBROKEN! timeout: {time.time() - start}\n")

        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                    "Content-Type": "application/json"}

        # Service URL
        url = f"{base_url}/v3"

        # create authenticator for tapis systems
        authenticator = t.access_token
        access_token = re.findall(r'(?<=access_token: )(.*)', str(authenticator))[0]

        return t, url, access_token

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
    
    def accept(self, initial=False):
        print("Startin connection startup process")
        self.connection, ip_port = self.sock.accept()
        print("accepted")
        if initial:
            print("initial connection")
            self.json_send("initial")
            print("sent connection type")
            credentials = self.json_receive()
            print("received credentials")
            username, password = credentials['username'], credentials['password']
            t, url, access_token = self.tapis_init(username, password)
            self.json_send(url)
            print("url sent")
            return username, password, t, url, access_token
        else:
            print("continuing connection")
            self.json_send("continuing")
            print("sent connection type")
            self.json_send({"username":self.username, "url":self.url})
            print("sent credentials")

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
                    return json.load(f)
            elif kwargs['command_group'] == 'exit':
                return "exiting"
            elif kwargs['command_group'] == 'shutdown':
                return "shutting down"
            else:
                return "Failed"
        except Exception as e:
            return str(e)

    def timer(self):
        while True:
            if time.time() > self.end_time:
                self.json_send("shutting down")
                self.connection.close()
                os._exit()

    def main(self):
        timer = k_thread(target=self.timer)
        timer.start()
        while True: # checks if any command line arguments were provided
            try:
                message = self.json_receive()
                kwargs, exit_status = message['kwargs'], message['exit']
                result = self.run_command(**kwargs)
                self.end_time = time.time() + 300
                self.json_send(result)
                print(result)
                if result == 'shutting down':
                    timer.kill()
                    sys.exit(0)
                elif result == 'exiting' or exit_status:
                    self.connection.close()
                    self.accept()
            except (ConnectionResetError, ConnectionAbortedError, ConnectionError, OSError, WindowsError, socket.error) as e:
                print(e)
                timer.kill()
                os._exit(0)
            except Exception as e:
                print(e)
                timer.kill()
                os._exit(0)


if __name__ == '__main__':
    server = Server('127.0.0.1', 3000)
    server.main()