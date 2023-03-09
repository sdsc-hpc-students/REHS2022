import neo4jupyter
import py2neo
from py2neo import Graph, Node, Relationship, GraphService
import IPython

neo4jupyter.init_notebook_mode()

graph = Graph(f"bolt+ssc://testingneo4jupyter.pods.icicle.tapis.io:443", auth=("testingneo4jupyter", "OWLDzASEUetNBIDezBGhVUppOupXZg"), secure=True, verify=True)
obj = neo4jupyter.draw(graph, {"Organization" : "alias"}).data
print(obj)
with open(r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\Neo4j-Visualization\html_file.html', 'w') as f:
    f.write(str(obj))