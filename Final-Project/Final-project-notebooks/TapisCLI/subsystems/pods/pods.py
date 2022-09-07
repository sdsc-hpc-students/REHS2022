import sys
from tapipy import tapis
import json
import pyperclip
import argparse
import py2neo
from py2neo import Graph

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\tapis-object.py')
from tapisobject import tapisObject

class Pods():
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\pods\pods.json')

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

class Neo4jCLI():
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j\TapisCLI\subsystems\pods\Neo4j.json')
         
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
        
        print(f'Entered the {args[0]}') # enter kwargs['r']s into the neo4j client
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

    def pods_cli(self, kwargs: dict, args: list):
        try:
            if kwargs['r'] == 'get_pods':
                print(self.get_pods())
            elif kwargs['r'] == 'create_pod':
                print(self.create_pod(kwargs, args))
            elif kwargs['r'] == 'restart_pod':
                print(self.restart_pod(kwargs, args))
            elif kwargs['r'] == 'delete_pod':
                print(self.delete_pod(kwargs, args))
            elif kwargs['r'] == "set_pod_perms":
                print(self.set_pod_perms(kwargs, args))
            elif kwargs['r'] == 'delete_pod_perms':
                print(self.delete_pod_perms(kwargs, args))
            elif kwargs['r'] == 'get_perms':
                print(self.get_perms(kwargs, args))
            elif kwargs['r'] == "copy_pod_password":
                print(self.copy_pod_password(kwargs, args))
            elif kwargs['r'] == 'query':
                print(self.kg_query_cli(kwargs, args))
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return e