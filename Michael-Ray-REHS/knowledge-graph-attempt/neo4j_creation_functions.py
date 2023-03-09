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

class Neo4jcsvWriter:
    def __init__(self, dataset_link=None, graph_id=None, graph_username=None, graph_password=None):
        if not dataset_link:
            raise Exception("Please provide a dataset link or path!")
        if not graph_id:
            raise Exception("Please provide a graph pod id supplied by tapis pod authentication!")
        if not graph_username:
            raise Exception("Please provide a username corresponding to the graph pod id as provided by tapis authentication!")
        if not graph_password:
            raise Exception("Please provide a password corresponding to the graph pod id as provided by tapis authentication!")
        else:
            self.dataset_link = dataset_link
            self.graph = Graph(f"bolt+ssc://{graph_id}.pods.icicle.develop.tapis.io:443", auth=(graph_username, graph_password), secure=True, verify=True)

        # csv_data_raw = requests.get(dataset_link).content       
        # csv_columns = pandas.read_csv(io.StringIO(csv_file.decode('utf-8')))

    @staticmethod
    def make_properties(node):
        properties = ''
        if node['properties']:
            for property_name in node['properties']:
                properties += f'{property_name}:row.{property_name}, '
            return properties[:-2]
        else:
            properties += f'id: row.{node["node_type"]}'
            return properties

    @staticmethod
    def make_relationships(nodes, node):
        relationships = ''
        for relationships_type, related_to in node['relationships'].items():
            relationships += f'\nMERGE (n{nodes.index(node)})-[:{relationships_type}]->(n{nodes.index(related_to)})'

        return relationships
    
    def expression_maker(self, nodes):
        script = f'LOAD CSV WITH HEADERS FROM "{self.dataset_link}" AS row WITH row WHERE row.id IS NOT null'
        for index, node in enumerate(nodes):
            properties = make_properties(node)
            script += f'\nMERGE (n{index}:{node["node_type"]}' + ' {' + properties + '})'

        for node in nodes:
            if node['relationships']:
                relationships = make_relationships(nodes, node)
                script += relationships

        return script


class CommandExecutor:
    def __init__(self, graph_id=None, graph_username=None, graph_password=None):
        if not graph_id:
            raise Exception("Please provide a graph pod id supplied by tapis pod authentication!")
        if not graph_username:
            raise Exception("Please provide a username corresponding to the graph pod id as provided by tapis authentication!")
        if not graph_password:
            raise Exception("Please provide a password corresponding to the graph pod id as provided by tapis authentication!")
        else:
            self.graph = Graph(f"bolt+ssc://{graph_id}.pods.icicle.develop.tapis.io:443", auth=(graph_username, graph_password), secure=True, verify=True)
            print("ready to receive commands")

    @staticmethod
    def execute_command(expressions=None):
        if isinstance(expressions, list):
            for expression in expressions:
                graph.run(expression)
            return "Commands successfully executed"
        else:
            graph.run(expressions)
            return "Command successfully executed"

    def command_executor(self, command):
        flag = True
        while flag:
            try:
                return_message = execute_command(graph=self.graph, expressions=command)
                print(return_message)
                flag = False
            except wiring.BrokenWireError:
                print("Connection failure, attempting to re-establish connection")
                self.graph = Graph(bolt_connection, auth=(username, password), secure=True, verify=True)
                continue