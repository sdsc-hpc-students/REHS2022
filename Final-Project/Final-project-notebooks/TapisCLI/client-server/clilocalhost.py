import pyfiglet
import argparse
import sys
import time
import re
import multiprocessing


def import_pyfiglet():
    global pyfiglet
    import pyfiglet
def import_tapis():
    global Tapis
    from tapipy.tapis import Tapis
sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
def import_pods():
    global Pods
    from pods import Pods
def import_systems():
    global Systems
    from systems import Systems
def import_files():
    global Files
    from files import Files
def import_apps():
    global Apps
    from apps import Apps
def import_getpass():
    global getpass
    from getpass import getpass

processes = [
    multiprocessing.Process(target=import_pyfiglet),
    multiprocessing.Process(target=import_tapis),
    multiprocessing.Process(target=import_pods),
    multiprocessing.Process(target=import_systems),
    multiprocessing.Process(target=import_apps),
    multiprocessing.Process(target=import_files),
    multiprocessing.Process(target=import_getpass),
]

for p in processes:
    p.start()

# with Pool(7) as p:
#     p.map(lambda x: x.)


class CLI:
    def __init__(self, username, password):
        self.username, self.password = username, password

        start = time.time()
        base_url = "https://icicle.develop.tapis.io"
        try:
            self.t = Tapis(base_url = base_url,
                    username = self.username,
                    password = self.password)
            self.t.get_tokens()
        except Exception as e:
            print(f"\nBROKEN! timeout: {time.time() - start}\n")
            raise

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

        title = pyfiglet.figlet_format("Tapiconsole", font="slant")
        print(title)

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

        self.pods = Pods(self.t, self.username, self.password)
        self.systems = Systems(self.t, self.username, self.password)
        self.files = Files(self.t, self.username, self.password)
        self.apps = Apps(self.t, self.username, self.password)

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
            else:
                return "Failed"
        except Exception as e:
            return e

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided
            try:
                kwargs = parser.parse_args()
            except e:
                print(e)
                sys.exit(1)
            print(self.run_command(**kwargs))
            sys.exit(0)
        
        while True:
            command_input = self.process_command(str(input(f"[{self.username}@{self.url}] ")))
            self.run_command(**command_input)


if __name__ == '__main__':
    username = str(input('enter your TACC username: '))
    password = getpass('enter your TACC password: ')
    try:
        client = CLI(username, password)
    except Exception as e:
        print(e)
        print('Invalid login, try again')
        sys.exit(1)
    client.main()