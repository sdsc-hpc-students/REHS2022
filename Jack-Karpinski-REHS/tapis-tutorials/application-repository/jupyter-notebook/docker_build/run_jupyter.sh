#!/bin/bash

PrgName=`basename $0`

# Determine absolute path to location from which we are running.
export RUN_DIR=`pwd`
export PRG_RELPATH=`dirname $0`
cd $PRG_RELPATH/.
export PRG_PATH=`pwd`
cd $RUN_DIR

# This file will be located in the directory mounted by the job.
SESSION_FILE="delete_me_to_end_session"
touch $SESSION_FILE

# The password used to log into the Notebook instance.
export PASSWORD=`date | md5sum | cut -c-32`

# RUN NOTEBOOK IN BACKGROUND  -->  CAN STAY THE SAME
LOCAL_IPY_PORT=8888

# WHY ARE THERE REFERENCES TO STOCKYARD BUT IT'S NOT SET ANYWHERE?
# LEAVE IT OUT OR COMMENTED OUT IN DOCKER FILE
# export XDG_RUNTIME_DIR="$STOCKYARD/jupyter"

NODE_HOSTNAME_PREFIX=$(hostname -s)   # Short Host Name  -->  name of compute node: c###-###
NODE_HOSTNAME_DOMAIN=$(hostname -d)   # DNS Name  -->  stampede2.tacc.utexas.edu
NODE_HOSTNAME_LONG=$(hostname -f)     # Fully Qualified Domain Name  -->  c###-###.stampede2.tacc.utexas.edu

# KEEP THIS IN THE wrapper.sh
START_PORT=45000

# The compute node port is determined using the get_port.py file.
export LOGIN_IPY_PORT=$(python3 $PRG_PATH/get_port.py $START_PORT $NODE_HOSTNAME_PREFIX)

# The native install of Jupyter Notebook is run in the background to allow
# the user command line access once Jupyter Notebook has started.
nohup jupyter-notebook --ip=0.0.0.0 --port=${LOCAL_IPY_PORT} --NotebookApp.token=${PASSWORD} > /dev/null &

# Port forwarding is set up for the four login nodes.
#
#   f: Requests ssh to go to background just before command execution.
#      Used if ssh asks for passwords but the user wants it in the background. Implies -n too.
#   g: Allows remote hosts to connect to local forwarded ports
#   N: Do not execute a remote command. Useful for just forwarding ports.
#   R: Connections to given TCP port/Unix socket on remote (server) host forwarded to local side.
#
# Create a reverse tunnel port from the compute node to the login nodes.
# Make one tunnel for each login so the user can just connect to stampede.tacc.utexas.edu.
for i in $(seq 4); do
    ssh -o StrictHostKeyChecking=no -f -g -N -R  $LOGIN_IPY_PORT:$NODE_HOSTNAME_LONG:$LOCAL_IPY_PORT login$i
done

# This is the URL that you can access
echo
echo Your notebook is now running at http://$NODE_HOSTNAME_DOMAIN:$LOGIN_IPY_PORT with password $PASSWORD 
echo

# Delete the session file to kill the job.
echo $NODE_HOSTNAME_LONG $IPYTHON_PID > $SESSION_FILE

# While the session file remains undeleted, keep Jupyter Notebook running.
while [ -f $SESSION_FILE ] ; do
    sleep 10
done
