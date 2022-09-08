import socket
sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\encryption')
from SSL import SSLSystem
from AES import AESSystem
sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\client-server-classes')
from clientserverclasses import ConnectionClientSide

class CLI:
    def __init__(self, username, password):
        self.ip, self.port, self.username, self.password = '127.0.0.1', 70412, username, password
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        self.connection = ConnectionClientSide(connection=self.sock, 
                                               ip_port=(self.ip, self.port), 
                                               username=self.username, 
                                               password=self.password)
        self.connection.key_exchange()

    def main(self):
        