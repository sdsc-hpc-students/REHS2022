FROM jupyter/base-notebook:notebook-6.4.4

# The user must be swtiched to root in order to install and update packages with apt-get.
# See https://github.com/jupyter/docker-stacks/blob/master/base-notebook/Dockerfile for info.
USER root

ENV HOMEDIR=/home/tapis
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y install ssh vim sendmail

# As a root user, set up the environment, including a directory we have access to.
# Then switch away from root to a newly created user which uses the listed homedir.
RUN useradd -m tapis

ADD "get_port.py" "run_jupyter.sh" $HOMEDIR
RUN chown -R tapis:tapis $HOMEDIR

# The user is switched back to the one from set in the base image.
USER 1000

# Note: If CMD is switched to ENTRYPOINT, it will make this container non-interactive!
CMD ["/home/tapis/run_jupyter.sh"]
