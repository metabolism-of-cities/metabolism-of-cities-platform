# Overview

This repository contains the source code of [Metabolism of Cities](https://metabolismofcities.org/). This repository supersedes the previous Github-hosted repository of our old website. This new website is written in Python using Django. The following technologies are used:

- Django 2.1
- Python 3
- PostgreSQL 
- Docker

# Getting started

To get started with this project, do the following:

- Clone the repository on your local machine
- Install Docker and specifically [Docker Compose](https://docs.docker.com/compose/)
- Create a number of baseline directories (see below)
- Create a configuration file (see below)
- Build your container

Once this is done, you have completed all the required steps to get the system running. Specific details below:

Let's say you have cloned this repository to /home/user/moc

    $ cd /home/user/moc
    $ mkdir src/{media,logs,static}
    $ cp src/ie/settings.sample.py src/ie/settings.py
    $ docker-compose build

Now that this is done, you can run the container like so:

    $ cd /home/user/moc
    $ docker-compose up

Wait a few moments, and the website should be up and running at http://localhost:8000
