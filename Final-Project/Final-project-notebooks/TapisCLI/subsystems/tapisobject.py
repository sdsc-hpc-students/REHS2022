import os
import time
import json
import pprint as pp
import datetime
from getpass import getpass
import pytz
import sys
import re
import pyperclip
import argparse

import pandas
import py2neo
from py2neo import Graph, Node, Relationship, GraphService


class tapisObject:
    def __init__(self, tapis_instance, username, password):
        self.t = tapis_instance
        self.username = username
        self.password = password
        self.help_path = r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems\help.json'

        with open(help_path, 'r') as h:
            json_help = h.read()
            self.help = json.loads(json_help)
