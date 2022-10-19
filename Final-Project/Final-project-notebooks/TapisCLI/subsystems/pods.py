import sys
from tapipy.tapis import Tapis
import pyperclip
from py2neo import Graph

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


class Neo4jCLI(tapisObject):
    def __init__(self, tapis_object, uname, pword):
        super().__init__(tapis_object, uname, pword)
        self.t = tapis_object
   
    def submit_query(self, **kwargs): # function to submit queries to a Neo4j knowledge graph
        id_ = kwargs['id']
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id_).user_username, self.t.pods.get_pod_credentials(pod_id=id_).user_password
        graph = Graph(f"bolt+ssc://{id_}.pods.icicle.tapis.io:443", auth=(uname, pword), secure=True, verify=True)
        if kwargs['file']:
            with open(kwargs['file'], 'r') as f:
                expression = f.read()
        else:
            expression = kwargs['expression']
        
        try:
            return_value = graph.run(expression)
            print(type(return_value))
            if str(return_value) == '(No data)' and 'create' in expression.lower(): # if no data is returned (mostly if something is created) then just say 'success'
                return f'[+][{id_}@pods.icicle.tapis.io:443] Success'
            elif str(return_value) == '(No data)':
                return f'[-][{id_}@pods.icicle.tapis.io:443] KG is empty'

            return str(f'[+][{id_}] {return_value}')
        except Exception as e:
            return str(e)


class Pods(tapisObject):
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)

    def return_formatter(self, info):
        return f"pod_id: {info.pod_id}\npod_template: {info.pod_template}\nurl: {info.url}\nstatus_requested: {info.status_requested}\n\n"

    def get_pods(self, **kwargs): # returns a list of pods
        pods_list = self.t.pods.get_pods()
        if kwargs['verbose']:
            return str(pods_list)
        pods_list = [self.return_formatter(pod) for pod in pods_list]
        pods_string = ""
        for pod in pods_list:
            pods_string += str(pod)
        return pods_string
        
    def whoami(self, **kwargs): # returns user information
        user_info = self.t.authenticator.get_userinfo()
        if kwargs['verbose']:
            return str(user_info)
        return user_info.username

    def create_pod(self, **kwargs): # creates a pod with a pod id, template, and description
        try:
            pod_description = kwargs['description']#str(input("Enter your pod description below:\n")) 
            pod_information = self.t.pods.create_pod(pod_id=kwargs['id'], pod_template=kwargs['template'], description=pod_description)
            if kwargs['verbose']:
                return str(pod_information)
            return self.return_formatter(pod_information)
        except Exception as e:
            raise e

    def restart_pod(self, **kwargs): # restarts a pod if needed
        try:
            return_information = self.t.pods.restart_pod(pod_id=kwargs["id"])
            if kwargs['verbose']:
                return str(return_information)
            return self.return_formatter(return_information)
        except Exception as e:
            raise e

    def delete_pod(self, **kwargs): # deletes a pod
        try:
            return_information = self.t.pods.delete_pod(pod_id=kwargs["id"])
            if kwargs['verbose']:
                return str(return_information)
            return self.return_formatter(return_information)
        except Exception as e:
            raise e

    def set_pod_perms(self, **kwargs): # set pod permissions, given a pod id, user, and permission level
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=kwargs["id"], user=kwargs['username'], level=kwargs['level'])
            return str(return_information)
        except tapipy.errors.BaseTapyException:
            raise Exception('Invalid level given')
        except Exception as e:
            raise e
    
    def delete_pod_perms(self, **kwargs): # take away someones perms if they are being malicious, or something
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=kwargs["id"], user=kwargs['username'])
            return str(return_information)
        except Exception as e:
            raise e

    def get_perms(self, **kwargs): # return a list of permissions on a given pod
        try:
            return_information = self.t.pods.get_pod_permissions(pod_id=kwargs["id"])
            return str(return_information)
        except IndexError:
            raise Exception('enter valid pod id, see help')
        except Exception as e:
            raise e

    def copy_pod_password(self, **kwargs): # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        try:
            password = self.t.pods.get_pod_credentials(pod_id=kwargs["id"]).user_password
            pyperclip.copy(password)
            password = None
            return 'copied to clipboard'
        except Exception as e:
            raise e

    def pods_cli(self, **kwargs):
        command = kwargs['command']
        try:
            match command:
                case 'get_pods':
                    return self.get_pods(**kwargs)
                case 'create_pod':
                    return self.create_pod(**kwargs)
                case 'restart_pod':
                    return self.restart_pod(**kwargs)
                case 'delete_pod':
                    return self.delete_pod(**kwargs)
                case "set_pod_perms":
                    return self.set_pod_perms(**kwargs)
                case 'delete_pod_perms':
                    return self.delete_pod_perms(**kwargs)
                case 'get_perms':
                    return self.get_perms(**kwargs)
                case "copy_pod_password":
                    return self.copy_pod_password(**kwargs)
                case "help":
                    return self.help['pods']
                case _:
                    raise Exception(f'Command {command} not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")