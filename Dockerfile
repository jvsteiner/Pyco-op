############################################################
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Jamie Steiner

VOLUME ['/home/jamie/Code/Docker']

# Add the application resources URL: 
# RUN echo "deb http://archive.ubuntu.com/ubuntu/ raring main universe" >> /etc/apt/sources.list
RUN echo "deb http://get.docker.com/ubuntu docker main" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

#RUN git clone https://github.com/jvsteiner/Pyco-op.git /home/pyco-op

# Get pip to download and install requirements:
#RUN pip install -r /home/pyco-op/requirements.txt

# Expose ports
EXPOSE 9000

RUN mkdir -p /app
ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Set the default command to execute
CMD ["python", "runserver.py"]

# Set the default directory where CMD will execute
##WORKDIR /home/pyco-op

# Set the default command to execute
# when creating a new container
# i.e. using CherryPy to serve the application
##CMD python /home/pyco-op/app.py runserver
