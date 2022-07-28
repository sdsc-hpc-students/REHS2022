# Details

This folder contains the Dockerfile used to build the image associated with the Jupyter Notebook HPC app, along with the files needed by the container to run.

To build the image for local testing, download this folder and navigate to it on the command line, then run the command ```docker build -f Dockerfile -t <NAME_OF_IMAGE> .```
<br><br>


## Dockerfile

The image is built upon Jupyter's official _base-notebook_ image, which is itself based on Ubuntu Linux.
<br><br>


## get_port.py

Jobs are executed on compute nodes belonging to Stampede2 or Frontera. This file is used to determine the random compute node that the job will be running on.
<br><br>


## run_jupyter.sh

A native install of Jupyter Notebook is started on the compute node determined by _get_port.py_. A reverse tunnel port from the compute node to the login node is created so the user can interact with Jupyter Notebook in a browser on their local machine.