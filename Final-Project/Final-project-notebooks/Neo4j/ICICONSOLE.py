import pandas as pd
from py2neo import Graph, Node, Relationship
from py2neo import GraphService
from py2neo import wiring
import time
import pytz
import datetime
from getpass import getpass
from tapipy.tapis import Tapis
import io
import os
start = time.time()

 
# Base URL for Tapis
base_url = "https://icicle.develop.tapis.io"
pod_id = ""
user = ""

def heavyFormat(message):
    print("*" * len(message))
    print("-" * len(message))
    print(message)
    print("-" * len(message))
    print("*" * len(message))

def lightFormat(message):
    print("-" * len(message))
    print(message)
    print("-" * len(message))

heavyFormat("Welcome to ICICONSOLE. Login to get started. ")

def console(graph, pod_id):
    lightFormat("Type \"new\" to access a different pod, or type \"exit\" to leave ICICONSOLE. Type \"clear\" to clear the screen. ")

    while(True):
        query = str(input("[" + user + "@" + pod_id + "] "))
        if(query == "exit"):
            os._exit(0)
        if(query == "new"):
            choosePod()
            return
        if(query == "clear"):
            os.system('cls' if os.name == 'nt' else 'clear')
            console(graph, pod_id)
        try: 
            df = graph.run(query).to_data_frame()
            with pd.option_context('expand_frame_repr', False, 'display.max_rows', None): 
                print(df)
        except:
            print("Something went wrong")


def choosePod():

    heavyFormat("Here are the IDs for your available TAPIS Pods: ")

    i = 1
    for pod in t.pods.get_pods():
        print(str(i) + ". " + pod.pod_id)
        i += 1
    if (i == 1):
        print("You don't have access to any TAPIS pods. Try again after you have verified access to at least one pod.")
    i = 1

    while(True):
        try: 
            pod_id = str(input("Enter the ID of the pod you want to access: ")).lower()
            if(pod_id == "exit"):
                os._exit(0)
            pod_username, password = t.pods.get_pod_credentials(pod_id=pod_id).user_username, t.pods.get_pod_credentials(pod_id=pod_id).user_password
            break
        except:
            print("Invalid Pod ID. Make sure you have access to this Pod.")

    graph_link = f"bolt+ssc://{pod_id}.pods.icicle.develop.tapis.io:443"
    while(True):
        try:
            graph = Graph(graph_link, auth=(pod_username, password), secure=True, verify=True)
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(0.25)
            heavyFormat(f"Hey there {user}! Welcome to the Neo4j Cypher Console for: " + str(pod_id))
            console(graph, pod_id)
        except:
            print("There was a connection error.")
            
# Get Tapis object if it isn't already created.
while(True):
    try:
        try:
            t
            if t.base_url == base_url and t.username == user and t.access_token:
                print("Tapis object already exists.")
                if t.access_token.expires_at < datetime.datetime.now(pytz.utc):
                    raise
            else:
                raise
        except:
            try:
                user = str(input("Enter Your TACC Username: "))
                t = Tapis(base_url = base_url, username=user,
                        password = getpass('Enter Your TACC Password: '))
                t.get_tokens()
                choosePod()
                break
            except Exception as e:
                raise
    except:
        print("An error occurred, likely due to mistyped login. Try again. ")



