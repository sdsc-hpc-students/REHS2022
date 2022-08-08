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
        