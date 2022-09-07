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
    def __init__(tapis_instance, username, password, help_path):
        self.t = tapis_instance
        self.username = username
        self.password = password

        with open(help_path, 'r') as h:
            json_help = h.read()
            self.help = json.loads(json_help)
