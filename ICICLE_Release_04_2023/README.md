In this project we developed authenticated connections to kubernetes pods hosted on a TACC server. These clients include:

* Jupyter Notebooks 
* Command Line Interfaces

The Notebooks and the CLIs each have their own directory which is seen above.

The primary goals of our work were:

1. Authenticate users using TACC accounts
2. Create Neo4j Pods to be able to store data on Tacc Servers
3. Load pre existing data into the Neo4j Pods
4. Be able to set permissions of Pods
5. Be able to parse Cypher queries from our clients and directly communicate with the data on our Pods
6. Visualize data through neo4jupyter (notebooks)
7. Have interactive user interface for requesting Cypher input (CLIs)


