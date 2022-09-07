from tapipy import tapis
import sys
import argparse

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\tapis-object.py')
from tapisobject import tapisObject


class Files(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\files\files.json')

    def list_files(self, kwargs: dict, args: list): # lists files available on a tapis account
        try:
            file_list = self.t.files.listFiles(systemId=args[0], path=kwargs['F'])
            return file_list
        except Exception as e:
            return e

    def upload(self, kwargs: dict, args: list): # upload a file from local to remote using tapis. Takes source and destination paths
        try:
            self.t.upload(system_id=args[0],
                    source_file_path=kwargs['sf'],
                    dest_file_path=kwargs['df'])
            return f'successfully uploaded {kwargs["sf"]} to {kwargs["df"]}'
        except:
            return f'failed to upload {kwargs["sf"]} to {kwargs["df"]}'
            
    def download(self, kwargs: dict, args: list): # download a remote file using tapis, operates basically the same as upload
        try:
            file_info = self.t.files.getContents(systemId=args[0],
                                path=kwargs['sf'])

            file_info = file_info.decode('utf-8')
            with open(kwargs['df'], 'w') as f:
                f.write(file_info)
            return f'successfully downloaded {kwargs["sf"]} to {kwargs["df"]}'
        except:
            return f'failed to download {kwargs["sf"]} to {kwargs["df"]}'

    def files_cli(self, kwargs: dict, args: list): # function to manage all the file commands
        try:
            if kwargs['r'] == 'list_files':
                return self.list_files(kwargs, args)
            elif kwargs['r'] == 'upload':
                return self.upload(kwargs, args)
            elif kwargs['r'] == 'download':
                return self.download(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e