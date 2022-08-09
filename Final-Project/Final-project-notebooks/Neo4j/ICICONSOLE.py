import py2neo
import pandas
from py2neo import Graph, Node, Relationship
from py2neo import GraphService
from py2neo import wiring
import time
from getpass import getpass
from tapipy.tapis import Tapis
import requests
import io

start = time.time()

# Base URL for Tapis
base_url = "https://icicle.develop.tapis.io"
username = str(input("Enter Your TACC Username: "))

# Get Tapis object if it isn't already created.
try:
    t
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
        t = Tapis(base_url = base_url,
                  username = username,
                  password = getpass('Enter Your TACC Password: '))
        t.get_tokens()
    except Exception as e:
        print(f"\nBROKEN! timeout: {time.time() - start}\n")
        raise

# V3 Headers
header_dat = {"X-Tapis-token": t.access_token.access_token,
              "Content-Type": "application/json"}

# Service URL
url = f"{base_url}/v3"                   # remote

print(time.time() - start)
print(f"base_url: {base_url}")
print(f"serv_url: {url}")

print("*" * 50)
print("Here are your available TAPIS Pods: ")
print("*" * 50)
time.sleep(3)

print(t.pods.get_pods())

pod_id = str(input("Enter the pod_id of the pod you want to access: ")).lower()
username, password = t.pods.get_pod_credentials(pod_id=pod_id).user_username, t.pods.get_pod_credentials(pod_id=pod_id).user_password

graph_link = f"bolt+ssc://{pod_id}.pods.icicle.develop.tapis.io:443"
graph = Graph(graph_link, auth=(username, password), secure=True, verify=True)