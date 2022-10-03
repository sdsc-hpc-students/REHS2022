import sys
from tapipy.tapis import Tapis
import pyperclip
from py2neo import Graph

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


class Neo4jCLI(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)
         
    def submit_queries(self, graph, expression): # function to submit queries to a Neo4j knowledge graph
        try:
            return_value = graph.run(expression)

            if str(return_value) == '(No data)' and 'CREATE' in expression.upper(): # if no data is returned (mostly if something is created) then just say 'success'
                return 'Success'

            return return_value
        except Exception as e:
            return e

    def kg_query_cli(self, **kwargs): # open a terminal connection with a neo4j pod.
        for x in range(5): # give the client 5 tries to connect to the KG. This often fails once or twice, users will not like entering stuff over and over
            try:
                username, password = self.t.pods.get_pod_credentials(pod_id=kwargs["id"]).user_username, self.t.pods.get_pod_credentials(pod_id=args[0]).user_password
                graph = Graph(f"bolt+ssc://{kwargs['id']}.pods.icicle.develop.tapis.io:443", auth=(username, password), secure=True, verify=True)
                break
            except Exception as e:
                if x < 5:
                    continue
                else:
                    print('ERROR: KG failed connection after 5 tries to connect')
                    return e
        
        print(f'Entered the {kwargs["id"]}') # enter kwargs['command']s into the neo4j client
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


class Pods(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)
        self.neo4j = Neo4jCLI(tapis_object, username, password)

    def get_pods(self): # returns a list of pods
        pods_list = self.t.pods.get_pods()
        return pods_list
    
    def whoami(self): # returns user information
        user_info = self.t.authenticator.get_userinfo()
        return user_info

    def create_pod(self, **kwargs): # creates a pod with a pod id, template, and description
        try:
            pod_description = str(input("Enter your pod description below:\n")) 
            pod_information = self.t.pods.create_pod(pod_id=kwargs['id'], pod_template=kwargs['template'], description=pod_description)
            return pod_information
        except Exception as e:
            return e

    def restart_pod(self, **kwargs): # restarts a pod if needed
        decision = input(f'Please enter, "Restart pod {kwargs["id"]}"\nNote that data may not be persistent on restart') # user confirmation
        if decision == f'Restart pod {kwargs["id"]}':
            return 'Restart Aborted'

        try:
            return_information = self.t.pods.restart_pod(pod_id=kwargs["id"])
            return return_information
        except Exception as e:
            return e

    def delete_pod(self, **kwargs): # deletes a pod
        decision = input(f'Please enter, "Delete pod {kwargs["id"]}"\nNote that all data WILL BE LOST') # user confirmation
        if decision == f'Delete pod {kwargs["id"]}':
            return 'Deletion Aborted'

        try:
            return_information = self.t.pods.delete_pod(pod_id=kwargs["id"])
            return return_information
        except Exception as e:
            return e

    def set_pod_perms(self, **kwargs): # set pod permissions, given a pod id, user, and permission level
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=kwargs["id"], user=kwargs['username'], level=kwargs['level'])
            return return_information
        except tapipy.errors.BaseTapyException:
            return 'Invalid level given'
        except Exception as e:
            return e
    
    def delete_pod_perms(self, **kwargs): # take away someones perms if they are being malicious, or something
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=kwargs["id"], user=kwargs['username'])
            return return_information
        except Exception as e:
            return e

    def get_perms(self, **kwargs): # return a list of permissions on a given pod
        try:
            return_information = self.t.pods.get_pod_permissions(pod_id=kwargs["id"])
            return return_information
        except IndexError:
            return 'enter valid pod id, see help'
        except Exception as e:
            return e

    def copy_pod_password(self, **kwargs): # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        try:
            password = self.t.pods.get_pod_credentials(pod_id=kwargs["id"]).user_password
            pyperclip.copy(password)
            password = None
            return 'copied to clipboard'
        except Exception as e:
            return e

    def pods_cli(self, **kwargs):
        try:
            if kwargs['command'] == 'get_pods':
                print(self.get_pods())
            elif kwargs['command'] == 'create_pod':
                print(self.create_pod(**kwargs))
            elif kwargs['command'] == 'restart_pod':
                print(self.restart_pod(**kwargs))
            elif kwargs['command'] == 'delete_pod':
                print(self.delete_pod(**kwargs))
            elif kwargs['command'] == "set_pod_perms":
                print(self.set_pod_perms(**kwargs))
            elif kwargs['command'] == 'delete_pod_perms':
                print(self.delete_pod_perms(**kwargs))
            elif kwargs['command'] == 'get_perms':
                print(self.get_perms(**kwargs))
            elif kwargs['command'] == "copy_pod_password":
                print(self.copy_pod_password(**kwargs))
            elif kwargs['command'] == 'query':
                print(self.neo4j.kg_query_cli(**kwargs))
            else:
                return 'Command not recognized'
        except IndexError:
            return "must specify subcommand. See 'help'"
        except Exception as e:
            return str(e)