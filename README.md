# Overview

This repository contains the source code of [Metabolism of Cities](https://metabolismofcities.org/). The following technologies are used:

- Django 3
- Python 3
- PostgreSQL 
- PostGIS
- Docker

In order to meaningfully contribute to this project (or clone it and use it for your own purposes), you should ideally be comfortable with (or willing to learn about) the aforementioned technologies.

The tech work on Metabolism of Cities has so far be done by a small number of people. However, we are very keen to get others involved. Due to the nature of the work, it would be ideal if you have a background both in urban metabolism/industrial ecology, and in web development. If you are not yet there, but you are willing to learn and spend time on this project, then we are happy to assist you in that journey. 

We don't manage tasks through github, but instead have an online forum and task list integrated on our website. If you are thinking of contributing, please open a new [forum thread](https://metabolismofcities.org/forum/) and let us know what you have in mind.

# Getting started

DISCLAIMER: the system is currently running in a Linux environment only, but it should also work perfectly fine on Windows or other operating systems if you have Docker running on it. The commands shown below, however, are Linux specific, but these are simply copy / create directory commands that should be easy enough in any OS.

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

NOTE: you may need to close and restart the container the first time around, as the initializing database boots too slowly on the first run and the web server fails without the db. Only occurs on the first time after building the container.

NOTE 2: you should migrate to get the database structure in place. If you know Django, this should be no problem. However please note that if you would like to seriously work on our website, then it would be most practical to get a copy of our live database so that you have actual data running on your local machine. Just ask us through the [forum](https://metabolismofcities.org/forum/) and we'll work this out.
