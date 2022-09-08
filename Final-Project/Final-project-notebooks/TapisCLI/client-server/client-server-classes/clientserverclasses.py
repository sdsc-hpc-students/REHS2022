import socket
import json
import asyncio
import datetime
import sys
sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\encryption')
from SSL import SSLSystem
from AES import AESSystem

class Connection:
    def __init__(self, connection=None, ip_port=None):
        self.connection = connection
        self.ip, self.port = ip_port
        self.username = None
        self.ssl_system = SSLSystem()
        self.aes_system = None

    def receive_and_unpack(self, encrypted=False):
        json_package = ""
        while True:
            if not encrypted:
                try:
                    json_package = json_package + \
                        self.connection.recv(32768).decode('utf-8')
                    return json.loads(json_package)
                except ValueError:
                    continue
            else:
                try:
                    json_package = json_package + \
                        self.aes_system.decrypt(self.connection.recv(32768).decode('utf-8'))
                    return json.loads(json_package)
                except ValueError:
                    continue

    def pack_and_send(self, data, encrypted=False):
        if not encrypted:
            json_package = json.dumps(data)
            self.connection.send(json_package.encode('utf-8'))
        else:
            json_package = json.dumps(data)
            json_package = self.aes_system.encrypt(json_package)
            self.connection.send(json_package)

    def create_message(self, ip, username, message_type, content, server_name='default'):
        return {
                "ip":ip, 
                "username":username, 
                "time":str(datetime.datetime.now()), 
                "server_name":server_name,
                "message_type":message_type,
                "content":content
               }

class ConnectionServerSide(Connection):
    def __init__(self, connection=None, ip_port=None):
        super().__init__(connection, ip_port)

    def key_exchange(self):
        private_key, public_key = self.ssl_system.create_keys()
        print(f'Public Key: {public_key}')
        self.pack_and_send(public_key)
        print("key sent")
        cipher_key_encrypted = self.receive_and_unpack()
        print('received key')
        cipher_key = self.ssl_system.decrypt_message(
            cipher_key_encrypted, public_key, private_key)
        self.aes_system = AESSystem(cipher_key)

    def kill_connection(self, send_thread, receive_thread):
        self.connection.close()
        send_thread.kill()
        receive_thread.kill()

    def ping_connection(self, send_thread, receive_thread):
        ping_message = self.create_message(self.ip, self.username, 'ping', 'checking_activity')
        while True:
            try:
                self.pack_and_send(ping_message, encrypted=True)
            except:
                self.kill_connection(send_thread, receive_thread)
                break

class ConnectionClientSide(Connection):
    def __init__(self, connection=None, ip_port=None, username=None, password=None):
        super().__init__(connection, ip_port)
        self.username, self.password = username, password
        self.ip, self.port = ip_port
    
    def key_exchange(self):
        public_key = self.receive_and_unpack()
        print('received')
        aes_key, encrypted_aes = self.ssl_system.generate_message(public_key)
        self.aes_system = AESSystem(int(aes_key))
        self.pack_and_send(encrypted_aes)

    def connect(self, t='login'):
        self.key_exchange()


