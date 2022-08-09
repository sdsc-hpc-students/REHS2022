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
username = ""


# Get Tapis object if it isn't already created.
while(True):
    try:
        try:
            t
            if t.base_url == base_url and t.username == username and t.access_token:
                print("Tapis object already exists.")
                if t.access_token.expires_at < datetime.datetime.now(pytz.utc):
                    print("Existing Tapis token expired, getting new token.")
                    raise
            else:
                raise
        except:
            try:
                t = Tapis(base_url = base_url,
                        username = str(input("Enter Your TACC Username: ")),
                        password = getpass('Enter Your TACC Password: '))
                t.get_tokens()
                break
            except Exception as e:
                raise
    except:
        print("An error occurred, likely due to mistyped login. Try again. ")

print("*" * 50)
print("-" * 50)
print("Here are the IDs for your available TAPIS Pods: ")
print("-" * 50)
print("*" * 50)

time.sleep(1)

i = 1
for pod in t.pods.get_pods():
    print(str(i) + ". " + pod.pod_id)
    i += 1
i = 1

while(True):
    try: 
        pod_id = str(input("Enter the pod_id of the pod you want to access: ")).lower()
        pod_username, password = t.pods.get_pod_credentials(pod_id=pod_id).user_username, t.pods.get_pod_credentials(pod_id=pod_id).user_password
        break
    except:
        print("Invalid Pod ID. Make sure you have access to this Pod.")

graph_link = f"bolt+ssc://{pod_id}.pods.icicle.develop.tapis.io:443"
while(True):
    try:
        graph = Graph(graph_link, auth=(pod_username, password), secure=True, verify=True)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("*" * 50)
        print("-" * 50)
        print("Welcome to the Neo4j Cypher Console for: " + str(pod_id))
        print("-" * 50)
        print("*" * 50)

        break
    except:
        print("There was a connection error.")

while(True):
    query = str(input("[" + pod_username + "@" + pod_id + "] "))
    if(query == "exit"):
        break
    if(query == "clear"):
        os.system('cls' if os.name == 'nt' else 'clear')
        query = str(input("[" + pod_username + "@" + pod_id + "] "))
    try: 
        df = graph.run(query).to_data_frame()
        with pd.option_context('expand_frame_repr', False, 'display.max_rows', None): 
            print(df)
    except:
        print("Something went wrong")


