import os
import time
import json
import pprint as pp
import datetime
from getpass import getpass
import pytz
import sys

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
        print(f"serv_url: {self.url}")

        self.commands_list = {
            'help':'get list of commands',
            'whoami':'returns active user username',
            'get_pods':'get list of pods available to selected account',
            'create_pod':'create a pod\nFormat: create_pod <pod-id> -t <template>',
            'set_pod_perms':'sets the permissions on a pod\nFormat: set_pod_perms <pod_id> -u <username to give perms> -L <permission level>',
            'get_pod_info':'get the link and auth information for selected pod ID\nFormat: get_pod_info <pod_id>',
            'query':'open the Neo4j Query command line\nFormat: query -L <graph_link> -u <graph_auth_username> -p <graph_auth_password>',
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
        return self.username

    def create_pod(self, kwargs: dict, args: list):
        pod_description = str(input("Enter your pod description below:\n"))
        pod_information = self.t.pods.create_pod(pod_id=args[0], pod_template=kwargs['t'], description=pod_description)
        return pod_information
    
    def set_pod_perms(self, kwargs: dict, args: list):
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=args[0], user=kwargs['u'], level=kwargs['L'])
            return return_information
        except tapipy.errors.BaseTapyException:
            return 'Invalid level given'
        except:
            return 'error'

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
            elif command == "set_pod_perms":
                print(self.set_pod_perms(kwargs, args))
            elif command == "get_pod_info":
                pod_username, pod_password, pod_link = self.get_pod_information(kwargs, args)
                print(f'Pod Username: {pod_username}\nPod Password: {pod_password}\nPod Link: {pod_link}')
            elif command == 'query':
                print(self.kg_query_cli(kwargs, args))
            elif command == 'exit':
                sys.exit(1)
            else:
                print('Command not recognized')
                

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