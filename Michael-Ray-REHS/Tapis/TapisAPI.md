# Tapis Tutorial Video
A framework to support computational research to enable scientists to utilize and amnage multi-institution machines

A set of hosted multi datacenter REST APIs together with languages SDKs and CLI for securely managing data and executing code on HPC HTC and cloud systems

what is a REST api? 
it transfers data over HTTP, usually in the form of JSon in a client server architecture, which can automatically use chaching

basicaly allows interaction with any REST web service, any web service which adheres to teh REST architectural constraints
You access the data of a rest API by sending an http request to its url and processing its response

tapis is used for its oauth and storage capabilities. Also can manage jobs and apps

for example, you can use a web form to trigger and HPC job

implements concepts of systems applications files and jobs. Easy secure data sharing in cloud and HPC systems
associate JSON documents with Tapis Resources

provide actor based function execution. Event driven functions 

OAuth, tenant specific user authentication

coming soon is containerization

also will suport low volume event driven sensor data transfer

user request to associate site -> forward request to primary site -> request processed and placed in job queue -> associate site agent processes task locally -> data and secrets remain local to associate sites

assuming the user is already authenticated

security kernel can be hosted on associate site, to maintain security

## challenges
Security:
establishing trust between dispersed services, and allowing local sites to host their own security and secrets

Config:
Determining what components will run on the main and associate sites
routing requests and work to proper service instance

Management:
multiple management services active (each site has its own kubernetes running)
coordinating updates and maintenance
starting and stopping services
monitoring, logging, auditing, and debugging the services

## Decentralized security
security requests are submitted to the security library by rest requests, from other services of Tapis. These requests either go to a secret vault cluster, or a permission checked database in postgres. Automatic caching on the database. 

One interface to two stores

Challenges:

fast authorization
extend the permission model from apache to be more flexible
postgres backend
server chaching

Secrets management
hashicorp vault backend
all non user secrtets used by system kept in the vault. AKA, secrets only tapis and associated systems will use
automated key rotation to increase security
simplify key distribution using ValutCA certificate authority. How do you get secrets? how do you manage them over time

portability:
each client website or service can have its own security kernel so it must be easy to deploy
site admins must be able to manage it directly
the secrets must never leave the site!

## Support for containerization
support for deocker and singularity
make scheduling of jobs much easier
scheduling can take resource availability into account to minimize time to solution

Challenges:
encapsulate all dependencies in an image

portability:
apply on multiple OS
match system capabilities with app requirements
develop algorithms that dynamically minimize time to solution

how do we distribute images on many node clusters efficiently

## Functions as a service with Abaco
users define a function they want to run using docker. They are actors

each actor gets a URL from abaco from which it can receive messages

then the user can send the actor a message by HTTP post to the URL

abaco launches a container from the associated image, injecting the message into the container

realtime complex workflow:
events can trigger processing in one data center

results from an initial step will affect following steps
basically how can you coordinate workflows and processes in different datacenters?

## Streams API
integrating with CHORDS

data constantly streams from sensors

the streams API will trigger processing and workflow based on conditions the user provides
helps with real time data processinhg, and can trigger jobs and applications.

operates with mongo db and backend REST

