from tapipy.tapis import Tapis
import sys
import argparse

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


class Files(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)

    def return_formatter(self, info):
        return f"name: {info.name}\ngroup: {info.group}\npath: {info.path}\n"

    def list_files(self, **kwargs): # lists files available on a tapis account
        try:
            file_list = self.t.files.listFiles(systemId=kwargs['id'], path=kwargs['file'])
            if kwargs['verbose']:
                return str(file_list)
            file_list = [self.return_formatter(f) for f in file_list]
        except Exception as e:
            raise e

    def upload(self, **kwargs): # upload a file from local to remote using tapis. Takes source and destination paths
        try:
            source = kwargs["file"].split(",")[0]
            destination = kwargs["file"].split(",")[1]
            self.t.upload(system_id=kwargs['id'],
                    source_file_path=source,
                    dest_file_path=destination)
            return f'successfully uploaded {source} to {destination}'
        except:
            raise Exception(f'failed to upload {source} to {dstination}')
            
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
            raise Exception(f'failed to download {source} to {destination}')

    def files_cli(self, **kwargs): # function to manage all the file commands
        command = kwargs['command']
        try:
            match command:
                case'list_files':
                    return self.list_files(**kwargs)
                case 'upload':
                    return self.upload(**kwargs)
                case 'download':
                    return self.download(**kwargs)
                case "help":
                    return self.help['files']
                case _:
                    raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")
        except Exception as e:
            raise e