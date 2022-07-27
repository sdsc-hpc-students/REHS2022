from py2neo import Graph
from getpass import getpass
import os

pwd = os.path.dirname(os.path.abspath(__file__))
database_file = r'user_database.cypher'

class dbInterface:
    def __init__(self, graph_url, username, password):
        self.cypher_file = os.path.join(pwd, database_file)
        self.graph = Graph(graph_url, user="neo4j", password=password)

    def write_expressions_from_file(self, file_name):
        with open(file_name, 'r') as f:
            for line in f.readlines():
                #print(str(line))
                self.graph.create(str(line)[7:-1])

if __name__ == "__main__":
    graph = 'neo4j+s://0f259034.databases.neo4j.io'
    username = 'neo4j' # str(input("Username:"))
    password = 'viR1xtHsfJXWvx7x2gNWL3mX1deT9ZSFj0IqWcQ9mFU' # getpass("Password:", stream=None)
    interface = dbInterface(graph, username, password)
    interface.write_expressions_from_file(interface.cypher_file)

# viR1xtHsfJXWvx7x2gNWL3mX1deT9ZSFj0IqWcQ9mFU