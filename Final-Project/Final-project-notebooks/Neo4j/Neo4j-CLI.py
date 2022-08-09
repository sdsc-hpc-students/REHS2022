import os
import time
import json
import pprint as pp
import datetime
from getpass import getpass
import pytz

import pandas
import neo4jupyter
import py2neo
from py2neo import Graph, Node, Relationship, GraphService

from tapipy.tapis import Tapis

def show(res):
    try:
        pp.pprint(res.json())
    except:
        pp.pprint(res.text)

neo4jupyter.init_notebook_mode()

class Neo4jCLI:
    def __init__(self, username, password):
        self.username, self.password = username, password

        base_url = "https://icicle.develop.tapis.io"
        # Get Tapis object if it isn't already created.
        try:
            if t.base_url == base_url and t.username == username and t.access_token:
                print("Tapis object already exists.")
                if t.access_token.expires_at < datetime.datetime.now(pytz.utc):
                    print("Existing Tapis token expired, getting new token.")
                    raise
            else:
                print("Creating new Tapis object.")
                raise
        except:
            try:
                self.t = Tapis(base_url = base_url,
                        username = self.username,
                        password = self.password)
                t.get_tokens()
            except Exception as e:
                print(f"\nBROKEN! timeout: {time.time() - start}\n")
                raise

        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                    "Content-Type": "application/json"}

        # Service URL
        self.url = f"{base_url}/v3"

        print(time.time() - start)
        print(f"base_url: {base_url}")
        print(f"serv_url: {url}")

        print("#" * 500 + "\nWelcome to the Neo4j CLI Application\nEnter 'Help' for a list of commands")

    def get_pods(self):
        pods_list = self.t.get_pods()
        return pods_list

    def create_pod(self, kwargs: dict, args: list):
        pod_description = str(input("Enter your pod description below:\n"))
        pod_information = self.t.pods.create_pod(pod_id=args[0], pod_template=kwargs['t'], description=pod_description)
        return pod_information
    
    def set_pod_perms(self, kwargs: dict, args: list):
        return_information = self.t.pods.set_pod_permission(pod_id=args[0], user=kwargs['u'], level=kwargs['L'])
        return return_information

    def get_pod_information(self, kwargs: dict, args: list):
        username, password = t.pods.get_pod_credentials(pod_id=args[0]).user_username, t.pods.get_pod_credentials(pod_id=args[0]).user_password
        link = f"bolt+ssc://{args[0]}.pods.icicle.develop.tapis.io:443"
        return username, password, link
    
    def submit_queries(self, graph, expression):
        return_value = graph.run(expression)
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
                    print(self.submit_queries(self, graph, expression))
                except Exception as e:
                    print(e)
        
    def command_parser(self, command_input):
        command_input = command_input.split(' -')
        command_input = list(map(lambda x: tuple(x.split(' ')), command_input))
        command = command_input[0]
        args = [element[0] for element in command_input[1:] if len(element) == 1]
        kwargs = {element[0]:element[1] for element in command_input[1:] if len(element) > 1}

        return command, args, kwargs

    def main(self):
        while True:
            command_request = str(input(f'[NEO4J TAPIS CLI {self.username}]:'))
            command, args, kwargs = self.command_parser(command_request)
            if not command_request:
                print('')
                continue
            elif command == 'help':
                pass
            elif command == 'get_pods':
                print(self.get_pods())
            elif command == 'create_pod':
                print(self.create_pod(kwargs, args))
            elif command == "set_pod_perms":
                print(self.set_pod_perms(kwargs, args))
            elif command == "get_pod_info":
                print(self.get_pod_information(kwargs, args))
            elif command == 'query':
                print(self.kg_query_cli(kwargs, args))
                
        