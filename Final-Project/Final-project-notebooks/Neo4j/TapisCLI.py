print('Initializing...')
import os
import time
import json
import pprint as pp
import datetime
from getpass import getpass
import pytz
import sys
import json
import re
import pyperclip

import pandas
import py2neo
from py2neo import Graph, Node, Relationship, GraphService

from tapipy.tapis import Tapis
import tapipy

def show(res):
    try:
        pp.pprint(res.json())
    except:
        pp.pprint(res.text)

neo4jupyter.init_notebook_mode()
print('Initialization success!')

class TapisCLI:
    def __init__(self, username, password): # initialize tapis connection with icicle, TACC
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

        # help menu stuff to go into a separate file (someday)
        systems_help = '''Format:
            get_systems: systems -r get_systems
            get_system_info: systems <system_id> -r get_system_info
            create_system: systems -r create_system -F <path to system json config file>
            set_credentials: systems <system_id> -r set_credentials -pvk <path to private key> -pbk <path to public key>
            set_password: systems <system_id> -r set_password -p <password>
        '''
        
        files_help = '''Format:
            list_files: files <system_id> -r list_files -F <folder path in remote tapis system>
            download: files <system_id> -r download -sf <path to remote file on tapis system to download from> -df <path to local file to download into>
            upload: files <system_id> -r upload -sf <path of local file to upload> -df <remote destination filename on tapis system>
        '''

        jobs_help = '''Format:
            create_app: jobs -r create_app -F <path to app json config file>
            get_app_info: jobs <app_id> -r get_app_info -v <app_version>
            run_app: jobs <app_id> -r run_app -F <path to json job config file> -n <name to assign job> -v <app_version>
            get_app_status: jobs <job_uuid> -r get_app_status
            download_app_results: jobs <jobs_uuid> -r download_app_results -of <path to local output file>
        '''

        self.commands_list = { # *could* put all of this stuff in a file
            'help':'get list of commands',
            'whoami':'returns active user username',
            'get_pods':'get list of pods available to selected account',
            'create_pod':'create a pod\nFormat: create_pod <pod-id> -t <template>',
            'restart_pod':'restart the pod\nFormat: restart_pod <pod_id>',
            'delete_pod':'delete the pod. Requires user confirmation\nFormat: delete_pod <pod_id>',
            'set_pod_perms':'sets the permissions on a pod\nFormat: set_pod_perms <pod_id> -u <username to give perms> -L <permission level>',
            'delete_pod_perms':'deletes the permissions for the selected user\nFormat: delete_pod_perms <pod_id> -u <user to take perms from>',
            'get_perms':'gets a list of permissions for a pod\nFormat: get_perms <pod_id>',
            'copy_pod_password':'get the password for selected pod ID\nFormat: copy_pod_password <pod_id>',
            'query':'open the Neo4j Query command line\nFormat: query <pod_id>',
            'systems':f'commands to make use of Tapis systems\n{systems_help}',
            'files':f'commands to make use of Tapis file system\n{files_help}',
            'jobs':f'commands to make use of Tapis jobs and apps\n{jobs_help}',
            'exit':'exit the CLI app'
        }
        print("\n" + "#" * 100 + "\nWelcome to the Neo4j CLI Application\nEnter 'help' for a list of commands\n" + "#" * 100 + "\n")

    def help(self): # displays all instructions in help menus
        for command, desc in self.commands_list.items():
            print(f'{command}:::{desc}\n')

    def get_pods(self): # returns a list of pods
        pods_list = self.t.pods.get_pods()
        return pods_list
    
    def whoami(self): # returns user information
        user_info = self.t.authenticator.get_userinfo()
        return user_info

    def create_pod(self, kwargs: dict, args: list): # creates a pod with a pod id, template, and description
        try:
            pod_description = str(input("Enter your pod description below:\n")) 
            pod_information = self.t.pods.create_pod(pod_id=args[0], pod_template=kwargs['t'], description=pod_description)
            return pod_information
        except Exception as e:
            return e

    def restart_pod(self, kwargs: dict, args: list): # restarts a pod if needed
        decision = input(f'Please enter, "Restart pod {args[0]}"\nNote that data may not be persistent on restart') # user confirmation
        if decision == f'Restart pod {args[0]}':
            return 'Restart Aborted'

        try:
            return_information = self.t.pods.restart_pod(pod_id=args[0])
            return return_information
        except Exception as e:
            return e

    def delete_pod(self, kwargs: dict, args: list): # deletes a pod
        decision = input(f'Please enter, "Delete pod {args[0]}"\nNote that all data WILL BE LOST') # user confirmation
        if decision == f'Delete pod {args[0]}':
            return 'Deletion Aborted'

        try:
            return_information = self.t.pods.delete_pod(pod_id=args[0])
            return return_information
        except Exception as e:
            return e

    def set_pod_perms(self, kwargs: dict, args: list): # set pod permissions, given a pod id, user, and permission level
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=args[0], user=kwargs['u'], level=kwargs['L'])
            return return_information
        except tapipy.errors.BaseTapyException:
            return 'Invalid level given'
        except Exception as e:
            return e
    
    def delete_pod_perms(self, kwargs: dict, args: list): # take away someones perms if they are being malicious, or something
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=args[0], user=kwargs['u'])
            return return_information
        except Exception as e:
            return e

    def get_perms(self, kwargs, args): # return a list of permissions on a given pod
        try:
            return_information = self.t.pods.get_pod_permissions(pod_id=args[0])
            return return_information
        except IndexError:
            return 'enter valid pod id, see help'
        except Exception as e:
            return e

    def copy_pod_password(self, kwargs: dict, args: list): # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        try:
            password = self.t.pods.get_pod_credentials(pod_id=args[0]).user_password
            pyperclip.copy(password)
            password = None
            return 'copied to clipboard'
        except Exception as e:
            return e
    
    def submit_queries(self, graph, expression): # function to submit queries to a Neo4j knowledge graph
        try:
            return_value = graph.run(expression)

            if str(return_value) == '(No data)' and 'CREATE' in expression.upper(): # if no data is returned (mostly if something is created) then just say 'success'
                return 'Success'

            return return_value
        except Exception as e:
            return e

    def kg_query_cli(self, kwargs: dict, args: list): # open a terminal connection with a neo4j pod.
        for x in range(5): # give the client 5 tries to connect to the KG. This often fails once or twice, users will not like entering stuff over and over
            try:
                username, password = self.t.pods.get_pod_credentials(pod_id=args[0]).user_username, self.t.pods.get_pod_credentials(pod_id=args[0]).user_password
                graph = Graph(f"bolt+ssc://{args[0]}.pods.icicle.develop.tapis.io:443", auth=(username, password), secure=True, verify=True)
                break
            except Exception as e:
                if x < 5:
                    continue
                else:
                    print('ERROR: KG failed connection after 5 tries to connect')
                    return e
        
        print(f'Entered the {args[0]}') # enter commands into the neo4j client
        while True:
            expression = str(input('> '))
            if expression == 'exit':
                print("Exiting the query CLI now...")
                return "successfully exited the query CLI"
            else:
                try:
                    print(self.submit_queries(graph, expression))
                except Exception as e:
                    print(e)

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
        
    def systems(self, kwargs: dict, args: list): # function for managing all of the system commands, makes life easier later
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

    def files(self, kwargs: dict, args: list): # function to manage all the file commands
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

    def create_app(self, kwargs: dict, args: list): # create a tapis app taking a json descriptor file path
        try:
            with open(kwargs['F'], 'r') as f:
                app_def = json.loads(f.read())
            url = self.t.apps.createAppVersion(**app_def)
            return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}"
        except Exception as e:
            return e

    def get_app(self, kwargs: dict, args: list): # returns app information with an id and version as arguments
        try:
            app = self.t.apps.getApp(appId=args[0], appVersion=kwargs['v'])
            return app
        except Exception as e:
            return e

    def run_job(self, kwargs: dict, args: list): # run a job using an app. Takes a job descriptor json file path
        try:
            with open(kwargs['F'], 'r') as f:
                app_args = json.loads(f.read())

            job = {
                "name": kwargs['n'],
                "appId": args[0], 
                "appVersion": kwargs['v'],
                "parameterSet": {"appArgs": [app_args]        
                                }
            }
            job = self.t.jobs.submitJob(**job)
            return job.uuid
        except Exception as e:
            return e

    def get_job_status(self, kwargs: dict, args: list): # return a job status with its Uuid
        try:
            job_status = self.t.jobs.getJobStatus(jobUuid=args[0])
            return job_status
        except Exception as e:
            return e

    def download_job_output(self, kwargs: dict, args: list): # download the output of a job with its Uuid
        try:
            jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=args[0], outputPath='tapisjob.out')
            with open(kwargs['of'], 'w') as f:
                f.write(jobs_output)
            return f"Successfully downloaded job output to {kwargs['of']}"
        except Exception as e:
            return e

    def jobs(self, kwargs: dict, args: list): # function to manage all jobs
        try:
            if kwargs['r'] == 'create_app':
                return self.create_app(kwargs, args)
            elif kwargs['r'] == 'get_app_info':
                return self.get_app(kwargs, args)
            elif kwargs['r'] == 'run_app':
                return self.run_job(kwargs, args)
            elif kwargs['r'] == 'get_app_status':
                return self.get_job_status(kwargs, args)
            elif kwargs['r'] == 'download_app_results':
                return self.download_job_output(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e

    def command_parser(self, command_input): # parse commands (to some degree of competence) should have just used optparse
        command_input = command_input.split(' -')
        args = command_input[0].split(' ')[1:]
        command_input = list(map(lambda x: tuple(x.split(' ')), command_input))
        command = command_input[0][0]
        kwargs = {element[0]:element[1] for element in command_input[1:] if len(element) > 1}

        return command, args, kwargs

    def main(self): # manage ALL the commands
        while True:
            command_request = str(input(f'[NEO4J TAPIS CLI {self.username}]: '))
            command, args, kwargs = self.command_parser(command_request)
            # try:
            if not command:
                print('Enter a command')
                continue
            elif command == 'help':
                self.help()
            elif command == 'whoami':
                print(self.whoami())
            elif command == 'get_pods':
                print(self.get_pods())
            elif command == 'create_pod':
                print(self.create_pod(kwargs, args))
            elif command == 'restart_pod':
                print(self.restart_pod(kwargs, args))
            elif command == 'delete_pod':
                print(self.delete_pod(kwargs, args))
            elif command == "set_pod_perms":
                print(self.set_pod_perms(kwargs, args))
            elif command == 'delete_pod_perms':
                print(self.delete_pod_perms(kwargs, args))
            elif command == 'get_perms':
                print(self.get_perms(kwargs, args))
            elif command == "copy_pod_password":
                print(self.copy_pod_password(kwargs, args))
            elif command == 'query':
                print(self.kg_query_cli(kwargs, args))
            elif command == 'systems':
                print(self.systems(kwargs, args))
            elif command == 'files':
                print(self.files(kwargs, args))
            elif command == 'jobs':
                print(self.jobs(kwargs, args))
            elif command == 'exit':
                sys.exit(1)
            else:
                print('Command not recognized')
            # except:
            #     print('Error executing command, please see "help" for more details')
                

if __name__ == '__main__':
    while True:
        username = str(input('enter your TACC username: '))
        password = getpass('enter your TACC password: ')
        try:
            client = TapisCLI(username, password)
            break
        except Exception as e:
            print('Invalid login, try again')
            continue
    client.main()