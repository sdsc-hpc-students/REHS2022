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
import os
import logging

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from pods import Pods, Neo4jCLI
from systems import Systems
from files import Files
from apps import Apps


class Server:
    def __init__(self, IP, PORT):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        file_handler = logging.FileHandler(r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\logs\logs.log', mode='w')
        stream_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

        # set formats
        stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler.setFormatter(stream_format)
        file_handler.setFormatter(file_format)

        # add the handlers
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

        self.logger.disabled = False

        self.ip, self.port = IP, PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.connection = None
        self.end_time = time.time() + 300
        
        self.logger.info("Awaiting connection")
        self.username, self.password, self.t, self.url, self.access_token = self.accept(initial=True)

        self.pods = Pods(self.t, self.username, self.password)
        self.systems = Systems(self.t, self.username, self.password)
        self.files = Files(self.t, self.username, self.password)
        self.apps = Apps(self.t, self.username, self.password)
        self.neo4j = Neo4jCLI(self.t, self.username, self.password)
        self.logger.info('initialization complee')

    def tapis_init(self, username, password):
        start = time.time()
        base_url = "https://icicle.tapis.io"
        t = Tapis(base_url = base_url,
                username = username,
                password = password)
        t.get_tokens()

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
        self.connection, ip_port = self.sock.accept()
        self.logger.info("Received connection request")
        if initial:
            self.json_send({'connection_type':"initial"})
            for attempt in range(1,4):
                credentials = self.json_receive()
                self.logger.info("Received credentials")
                username, password = credentials['username'], credentials['password']
                try:
                    t, url, access_token = self.tapis_init(username, password)
                    self.json_send([True, attempt])
                    self.logger.info("Verification success")
                    break
                except:
                    self.json_send([False, attempt])
                    self.logger.warning("Verification failure")
                    if attempt == 3:
                        self.logger.error("Attempted verification too many times. Exiting")
                        os._exit(0)
                    continue
            self.json_send(url)
            self.logger.info("Connection success")
            return username, password, t, url, access_token
        else:
            self.json_send({'connection_type':'continuing', "username":self.username, "url":self.url})
            self.logger.info("Connection success")

    def shutdown_handler(self, result, exit_status):
        if result == '[+] Shutting down':
            self.logger.info("Shutdown initiated")
            sys.exit(0)
        elif result == '[+] Exiting' or exit_status:
            self.logger.info("user exit initiated")
            self.connection.close()
            self.accept()
    
    def timeout_handler(self):
        if time.time() > self.end_time:
            self.logger.error("timeout. Shutting down")
            self.json_send("shutting down")
            self.connection.close()
            os._exit(0)

    def run_command(self, **kwargs):
        command_group = kwargs['command_group']
        try:
            if command_group == 'pods':
                return self.pods.pods_cli(**kwargs)
            elif command_group == 'systems':
                return self.systems.systems_cli(**kwargs)
            elif command_group == 'files':
                return self.files.files_cli(**kwargs)
            elif command_group == 'apps':
                return self.apps.apps_cli(**kwargs)
            elif command_group == 'help':
                with open(r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems\help.json', 'r') as f:
                    return json.load(f)
            elif command_group == 'whoami':
                return self.pods.whoami()
            elif command_group == 'exit':
                return "[+] Exiting"
            elif command_group == 'shutdown':
                return "[+] Shutting down"
            elif command_group == 'neo4j':
                result = self.neo4j.submit_query(**kwargs)
                return result
            else:
                raise Exception(f"Command {command_group} not found. See help")
        except Exception as e:
            self.logger.error(str(e))
            return str(e)

    def main(self):
        while True: # checks if any command line arguments were provided
            try:
                message = self.json_receive()
                self.timeout_handler()
                kwargs, exit_status = message['kwargs'], message['exit']
                result = self.run_command(**kwargs)
                self.end_time = time.time() + 300
                self.json_send(result)
                self.shutdown_handler(result, exit_status)
            except (ConnectionResetError, ConnectionAbortedError, ConnectionError, OSError, WindowsError, socket.error) as e:
                self.logger.error(str(e))
                os._exit(0)
            except Exception as e:
                self.logger.error(str(e))
                os._exit(0)


if __name__ == '__main__':
    server = Server('127.0.0.1', 3000)
    server.main()