# application-repository
This repository serves to house applications that can be run on TACC hardware via Tapis v3 job submissions.

Note that in order to run an application via Tapis you will need to register a Tapis system that can execute 
applications using docker or singularity. For more information
please see the *Systems* section in the Tapis [documentation](https://tapis.readthedocs.io/en/latest/).

Another good reference for Tapis information is the live-docs which may be found [here](https://tapis-project.github.io/live-docs/).

In this repository there is a folder for each application containing the following:
* A README file that discusses how to use the application and any particular changes that may be necessary in the definition.

* A JSON file containing the application definition. Use this as a reference to create the application on a Tapis system.

* If applicable, a "docker_build" folder containing everything needed to build a Docker container from scratch, such as the Dockerfile and associated input files.
<br><br>

## Application types

There are a mix of interactive and non-interactive applications in this repository: 
* Interactive jobs run synchronously on a compute node, allowing the user to interact with the application in a web browser. The job will continue until the user shuts down the session or the job exceeds its maximum runtime.

* Non-interactive jobs do not require additional user interaction after job submission. Once the job is completed, the user can view the output in the directory as specified in the application definition ("execSystemOutputDir").
<br><br>


## Adding applications to the repository

When adding an application definition to the repository, its folder should contain the following:
* A JSON-syntax definition with all the required fields for running the application.

* A JSON-syntax job definition simulating what an actual submission would look like.

* A README detailing any specific inputs or changes that may be made to the application definition. 

* If applicable, a "docker_build" folder containing the Dockerfile used to build the image and any files that need to be copied into the container.
<br><br>

For more information on required application fields,
please see the Tapis live-docs reference [here](https://tapis-project.github.io/live-docs/?service=Apps#operation/createAppVersion).
