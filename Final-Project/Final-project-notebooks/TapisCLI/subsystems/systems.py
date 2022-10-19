from tapipy.tapis import Tapis
import sys
import json

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject

class Systems(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)

    def return_formatter(self, info):
        return f"id: {info.id}\nhost: {info.host}\n"

    def get_system_list(self, **kwargs): # return a list of systems active on the account
        try:
            systems = self.t.systems.getSystems()
            if systems and kwargs['verbose']:
                return str(systems)
            elif systems and not kwargs['verbose']:
                systems = [self.return_formatter(system) for system in systems]
                systems_string = ''
                for system in systems:
                    systems_string += system
                return systems_string

            return "[-] No systems registered"
        except Exception as e:
            raise e

    def get_system_info(self, **kwargs): # get information about a system given its ID
        try:
            system_info = self.t.systems.getSystem(systemId=kwargs["id"])
            if kwargs['verbose']:
                return str(system_info)
            return self.return_formatter(system_info)
        except Exception as e:
            raise e
        
    def create_system(self, **kwargs): # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        try:
            with open(kwargs['file'], 'r') as f:
                system = json.loads(f.read())
            system_id = system['id']
            self.t.systems.createSystem(**system)
            return str(system_id)
        except Exception as e:
            raise e

    def system_credential_upload(self, **kwargs): # upload key credentials for the system
        try:
            with open(kwargs['file'].split(",")[0], 'r') as f:
                private_key = f.read()

            with open(kwargs['file'].split(",")[1], 'r') as f:
                public_key = f.read()

            cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'],
                                userName=self.username,
                                privateKey=private_key,
                                publicKey=public_key)

            return str(cred_return_value)
        except Exception as e:
            raise e

    def system_password_set(self, **kwargs): # set the password for a system
        try:
            password_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'], # will put this in a getpass later
                                userName=self.username,
                                password=kwargs['password'])
            return str(password_return_value)
        except Exception as e:
            raise e

    def delete_system(self, **kwargs):
        try:
            return_value = self.t.systems.deleteSystem(systemId=kwargs['id'])
            return return_value
        except Exception as e:
            raise e

    def systems_cli(self, **kwargs): # function for managing all of the system commands, makes life easier later
        command = kwargs['command']
        try:
            match command:
                case 'get_systems':
                    return self.get_system_list(**kwargs)
                case 'get_system_info':
                    return self.get_system_info(**kwargs)
                case 'create_system':
                    return self.create_system(**kwargs)
                case "set_credentials":
                    return self.system_credential_upload(**kwargs)
                case "set_password":
                    return self.system_password_set(**kwargs)
                case "delete_system":
                    return self.delete_system(**kwargs)
                case "help":
                    return self.help['systems']
                case _:
                    raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")