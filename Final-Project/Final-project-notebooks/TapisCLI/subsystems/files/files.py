from tapipy.tapis import Tapis
import sys
import argparse

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


class Files(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\files\files.json')

    def list_files(self, **kwargs): # lists files available on a tapis account
        try:
            file_list = self.t.files.listFiles(systemId=kwargs['id'], path=kwargs['file'])
            return file_list
        except Exception as e:
            return e

    def upload(self, **kwargs): # upload a file from local to remote using tapis. Takes source and destination paths
        try:
            source = kwargs["file"].split(",")[0]
            destination = kwargs["file"].split(",")[1]
            self.t.upload(system_id=kwargs['id'],
                    source_file_path=source,
                    dest_file_path=destination)
            return f'successfully uploaded {source} to {destination}'
        except:
            return f'failed to upload {source} to {dstination}'
            
    def download(self, **kwargs): # download a remote file using tapis, operates basically the same as upload
        try:
            source = kwargs["file"].split(",")[0]
            destination = kwargs["file"].split(",")[1]
            file_info = self.t.files.getContents(systemId=kwargs['id'],
                                path=source)

            file_info = file_info.decode('utf-8')
            with open(destination, 'w') as f:
                f.write(file_info)
            return f'successfully downloaded {source} to {destination}'
        except:
            return f'failed to download {source} to {destination}'

    def files_cli(self, **kwargs): # function to manage all the file commands
        try:
            if kwargs['command'] == 'list_files':
                return self.list_files(**kwargs)
            elif kwargs['command'] == 'upload':
                return self.upload(**kwargs)
            elif kwargs['command'] == 'download':
                return self.download(**kwargs)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e