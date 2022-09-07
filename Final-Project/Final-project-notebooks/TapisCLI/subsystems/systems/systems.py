from tapipy import tapis
import sys

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\tapis-object.py')
from tapisobject import tapisObject

class Systems(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\systems\systems.json')

    def get_system_list(self): # return a list of systems active on the account
        try:
            systems = self.t.systems.getSystems()
            return systems
        except Exception as e:
            return e

    def get_system_info(self, kwargs: dict, args: list): # get information about a system given its ID
        try:
            system_info = self.t.systems.getSystem(systemId=args[0])
            return system_info
        except Exception as e:
            return e
        
    def create_system(self, kwargs: dict, args: list): # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        try:
            with open(kwargs['F'], 'r') as f:
                system = json.loads(f.read())
            system_id = system['id']
            self.t.systems.createSystem(**system)
            return system_id
        except Exception as e:
            return e


    def system_credential_upload(self, kwargs: dict, args: list): # upload key credentials for the system
        try:
            with open(kwargs['pvk'], 'r') as f:
                private_key = f.read()

            with open(kwargs['pbk'], 'r') as f:
                public_key = f.read()

            cred_return_value = self.t.systems.createUserCredential(systemId=args[0],
                                userName=self.username,
                                privateKey=private_key,
                                publicKey=public_key)

            return cred_return_value
        except Exception as e:
            return e

    def system_password_set(self, kwargs: dict, args: list): # set the password for a system
        try:
            password_return_value = self.t.systems.createUserCredential(systemId=args[0], # will put this in a getpass later
                                userName=self.username,
                                password=kwargs['p'])
            return password_return_value
        except Exception as e:
            return e

    def systems_cli(self, kwargs: dict, args: list): # function for managing all of the system commands, makes life easier later
        try:
            if kwargs['r'] == 'get_systems':
                return self.get_system_list()
            elif kwargs['r'] == 'get_system_info':
                return self.get_system_info(kwargs, args)
            elif kwargs['r'] == 'create_system':
                return self.create_system(kwargs, args)
            elif kwargs['r'] == "set_credentials":
                return self.system_credential_upload(kwargs, args)
            elif kwargs['r'] == "set_password":
                return self.system_password_set(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e