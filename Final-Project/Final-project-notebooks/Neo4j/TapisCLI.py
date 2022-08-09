import os
import time
import json
import pprint as pp
import datetime
from getpass import getpass
import pytz
import sys
import json

import pandas
import neo4jupyter
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

class Neo4jCLI:
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

        self.authenticator = self.t.access_token
        self.access_token = re.findall(r'(?<=access_token: )(.*)', str(authenticator))[0]
        print(self.authenticator)

        self.commands_list = {
            'help':'get list of commands',
            'whoami':'returns active user username',
            'get_pods':'get list of pods available to selected account',
            'create_pod':'create a pod\nFormat: create_pod <pod-id> -t <template>',
            'restart_pod':'restart the pod\nFormat: restart_pod <pod_id>',
            'delete_pod':'delete the pod. Requires user confirmation\nFormat: delete_pod <pod_id>',
            'set_pod_perms':'sets the permissions on a pod\nFormat: set_pod_perms <pod_id> -u <username to give perms> -L <permission level>',
            'delete_pod_perms':'deletes the permissions for the selected user\nFormat: delete_pod_perms <pod_id> -u <user to take perms from>',
            'get_perms':'gets a list of permissions for a pod\nFormat: get_perms <pod_id>',
            'get_pod_info':'get the link and auth information for selected pod ID\nFormat: get_pod_info <pod_id>',
            'query':'open the Neo4j Query command line\nFormat: query -L <graph_link> -u <graph_auth_username> -p <graph_auth_password>',
            'systems':'add here',
            'files':'add here',
            'jobs':'add here',
            'exit':'exit the CLI app'
        }
        print("#" * 100 + "\nWelcome to the Neo4j CLI Application\nEnter 'help' for a list of commands\n" + "#" * 100)

    def help(self):
        for command, desc in self.commands_list.items():
            print(f'{command}:::{desc}\n')

    def get_pods(self):
        pods_list = self.t.pods.get_pods()
        return pods_list
    
    def whoami(self):
        user_info = self.t.authenticator.get_userinfo()
        return user_info

    def create_pod(self, kwargs: dict, args: list):
        pod_description = str(input("Enter your pod description below:\n"))
        pod_information = self.t.pods.create_pod(pod_id=args[0], pod_template=kwargs['t'], description=pod_description)
        return pod_information

    def restart_pod(self, kwargs: dict, args: list):
        decision = input(f'Please enter, "Restart pod {args[0]}"\nNote that data may not be persistent on restart')
        if decision == f'Restart pod {args[0]}':
            return 'Restart Aborted'

        return_information = self.t.pods.restart_pod(pod_id=args[0])
        return return_information

    def delete_pod(self, kwargs: dict, args: list):
        decision = input(f'Please enter, "Delete pod {args[0]}"\nNote that all data WILL BE LOST')
        if decision == f'Delete pod {args[0]}':
            return 'Deletion Aborted'

        return_information = self.t.pods.delete_pod(pod_id=args[0])
        return return_information

    def set_pod_perms(self, kwargs: dict, args: list):
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=args[0], user=kwargs['u'], level=kwargs['L'])
            return return_information
        except tapipy.errors.BaseTapyException:
            return 'Invalid level given'
        except:
            return 'error'
    
    def delete_pod_perms(self, kwargs: dict, args: list):
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=args[0], user=kwargs['u'])
            return return_information
        except:
            return 'error'

    def get_perms(self, kwargs, args):
        return_information = self.t.pods.get_pod_permissions(pod_id=args[0])
        return return_information

    def get_pod_information(self, kwargs: dict, args: list):
        username, password = self.t.pods.get_pod_credentials(pod_id=args[0]).user_username, self.t.pods.get_pod_credentials(pod_id=args[0]).user_password
        link = f"bolt+ssc://{args[0]}.pods.icicle.develop.tapis.io:443"
        return username, password, link
    
    def submit_queries(self, graph, expression):
        return_value = graph.run(expression)

        if return_value == '(No data)':
            return 'Success'

        return return_value

    def kg_query_cli(self, kwargs: dict, args: list):
        for x in range(5):
            try:
                graph = Graph(kwargs['L'], auth=(kwargs['u'], kwargs['p']), secure=True, verify=True)
                break
            except:
                if x < 5:
                    continue
                else:
                    print('ERROR: KG failed connection after 5 tries to connect')
                    return None
        
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

    def get_system_list(self):
        systems = self.t.systems.getSystems()
        return systems

    def get_system_info(self, kwargs: dict, args: list):
        try:
            system_info = self.t.systems.getSystem(systemId=args[1])
            return system_info
        except:
            return "System does not exist"
        
    def create_system(self, kwargs: dict, args: list):
        with open(kwargs['F'], 'r') as f:
            system = json.loads(f.read())
            print(system)
        system_id = system['id']
        try:
            self.t.systems.createSystem(**system)
            return system_id
        except:
            return f"Failed to start {system_id}"

    def system_credential_upload(self, kwargs: dict, args: list):
        with open(kwargs['pvk'], 'r') as f:
            private_key = f.read()

        with open(kwargs['pbk'], 'r') as f:
            public_key = f.read()

        cred_return_value = self.t.systems.createUserCredential(systemId=args[0],
                               userName=self.username,
                               privateKey=private_key,
                               publicKey=public_key)

        return cred_return_value

    def system_password_set(self, kwargs: dict, args: list):
        password_return_value = self.t.systems.createUserCredential(systemId=args[0],
                               userName=self.username,
                               password=kwargs['p'])
        return password_return_value
        
    def systems(self, kwargs: dict, args: list):
        try:
            if kwargs['p'] == 'get_systems':
                return self.get_system_list()
            elif kwargs['p'] == 'get_system_info':
                return self.get_system_info(kwargs, args)
            elif kwargs['p'] == 'create_system':
                return self.create_system(kwargs, args)
            elif kwargs['p'] == "set_credentials":
                return self.system_credential_upload(kwargs, args)
            elif kwargs['p'] == "set_password":
                return self.system_password_set(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"

    def list_files(self, kwargs: dict, args: list):
        try:
            file_list = self.t.files.listFiles(systemId=args[0], path=rkwargs['F'])
            return file_list
        except:
            return 'Error retrieving files'

    def upload(self, kwargs: dict, args: list):
        try:
            self.t.upload(system_id=args[0],
                    source_file_path=kwargs['sf'],
                    dest_file_path=kwargs['df'])
            return f'successfully uploaded {kwargs["sf"]} to {kwargs["df"]}'
        except:
            return f'failed to upload {kwargs["sf"]} to {kwargs["df"]}'
            
    def download(self, kwargs: dict, args: list):
        try:
            file_info = self.t.files.getContents(systemId=args[0],
                                path=kwargs['sf'])

            file_info = file_info.decode('utf-8')
            with open(kwargs['df'], 'w') as f:
                f.write(file_info)
            return f'successfully downloaded {kwargs["sf"]} to {kwargs["df"]}'
        except:
            return f'failed to download {kwargs["sf"]} to {kwargs["df"]}'

    def files(self, kwargs: dict, args: list):
        try:
            if kwargs['p'] == 'list_files':
                return self.list_files(kwargs, args)
            elif kwargs['p'] == 'upload':
                return self.upload(kwargs, args)
            elif kwargs['p'] == 'download':
                return self.download(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"

    def create_app(self, kwargs: dict, args: list):
        try:
            with open(kwargs['F'], 'r') as f:
                app_def = json.loads(f.read())
            url = self.t.apps.createAppVersion(**app_def)
            return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}"
        except:
            return f"Failed to create app"

    def get_app(self, kwargs: dict, args: list):
        try:
            app = self.t.apps.getApp(appId=args[0], appVersion=kwargs['v'])
            return app
        except:
            return 'app not found'

    def run_job(self, kwargs: dict, args: list):
        try:
            with open(kwargs['F'], 'r') as f:
                app_args = json.loads(f.read())

            job = {
                "name": kwargs['n'],
                "appId": kwargs['id'], 
                "appVersion": kwargs['v'],
                "parameterSet": {"appArgs": [app_args]        
                                }
            }
            job = self.t.jobs.submitJob(**job)
            return job.uuid
        except:
            return 'Failed to start job'

    def get_job_status(self, kwargs: dict, args: list):
        job_status = self.t.jobs.getJobStatus(jobUuid=args[0])
        return job_status

    def download_job_output(self, kwargs: dict, args: list):
        try:
            jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=args[0], outputPath='tapisjob.out')
            with open(kwargs['of'], 'w') as f:
                f.write(jobs_output)
            return f"Successfully downloaded job output to {kwargs['of']}"
        except:
            return 'download failed'

    def jobs(self, kwargs: dict, args: list):
        try:
            if kwargs['p'] == 'create_app':
                return self.create_app(kwargs, args)
            elif kwargs['p'] == 'get_app_info':
                return self.get_app(kwargs, args)
            elif kwargs['p'] == 'run_app':
                return self.run_job(kwargs, args)
            elif kwargs['p'] == 'get_app_status':
                return self.get_job_status(kwargs, args)
            elif kwargs['p'] == 'download_app_results':
                return self.download_job_output(kwargs, args)
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"

    def command_parser(self, command_input):
        command_input = command_input.split(' -')
        args = command_input[0].split(' ')[1:]
        command_input = list(map(lambda x: tuple(x.split(' ')), command_input))
        command = command_input[0][0]
        kwargs = {element[0]:element[1] for element in command_input[1:] if len(element) > 1}

        return command, args, kwargs

    def main(self):
        while True:
            command_request = str(input(f'[NEO4J TAPIS CLI {self.username}]: '))
            command, args, kwargs = self.command_parser(command_request)
            try:
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
                elif command == "get_pod_info":
                    pod_username, pod_password, pod_link = self.get_pod_information(kwargs, args)
                    print(f'Pod Username: {pod_username}\nPod Password: {pod_password}\nPod Link: {pod_link}')
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
            except:
                print('Error executing command, please see "help" for more details')
                

if __name__ == '__main__':
    while True:
        username = str(input('enter your TACC username: '))
        password = getpass('enter your TACC password: ')
        try:
            client = Neo4jCLI(username, password)
            break
        except Exception:
            print('Invalid login, try again')
            continue
    client.main()