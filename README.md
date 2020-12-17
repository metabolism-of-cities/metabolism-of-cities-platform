# Overview

This repository contains the source code of [Metabolism of Cities](https://metabolismofcities.org/). The following technologies are used:

- Django 3
- Python 3
- PostgreSQL 
- PostGIS
- Docker

In order to meaningfully contribute to this project (or clone it and use it for your own purposes), you should ideally be comfortable with (or willing to learn about) the aforementioned technologies. You can make a meaningful contribution if you know either about python/Django, or about HTML/CSS/Javascript (allowing you to contribute with back-end or front-end programming, respectively).

The tech work on Metabolism of Cities has so far be done by a small number of people. However, we are very keen to get others involved. Due to the nature of the work, it would be ideal if you have a background both in urban metabolism/industrial ecology, and in web development. If you are not yet there, but you are willing to learn and spend time on this project, then we are happy to assist you in that journey.

We don't manage tasks through github, but instead have an online forum and [task list](https://metabolismofcities.org/tasks/?type=9&status=open_unassigned&priority=&project=&tag=) integrated on our website. If you are thinking of contributing, please open a new [forum thread](https://metabolismofcities.org/forum/) and let us know what you have in mind.

# Getting started

DISCLAIMER: the system is currently running in a Linux environment only, but it should also work perfectly fine on Windows or other operating systems if you have Docker running on it. The commands shown below, however, are Linux specific, but these are simply copy / create directory commands that should be easy enough in any OS.

To get started with this project, do the following:

- Clone the repository on your local machine
- Install Docker and specifically [Docker Compose](https://docs.docker.com/compose/)
- Create a number of baseline directories (see below)
- Create a configuration file (see below)
- Build your container

Once this is done, you have completed all the required steps to get the system running. Specific details below:

Let's say you have cloned this repository to /home/user/metabolism-of-cities

    $ cd /home/user/metabolism-of-cities
    $ mkdir src/{media,logs,static}
    $ cp src/ie/settings.sample.py src/ie/settings.py
    $ sudo docker-compose build

Now that this is done, you can run the container like so:

    $ cd /home/user/metabolism-of-cities
    $ sudo docker-compose up

Wait a few moments, and the containers should be up and running. Your main container (moc_web) will display errors because there is no database yet. Please select your preferred database below and import this as follows:

    $ sudo docker container exec -i moc_db psql -U postgres moc < db.sql

Replace "db.sql" for the name of your database file (which should be uncompressed before loading it). After the database is loaded, you _may_ need to reload your container (CTRL+C followed by:

    $ sudo docker-compose up

And the website should be up and running at [http://0.0.0.0:8000](http://0.0.0.0:8000) and adminer to manage the database is available at [http://0.0.0.0:8080](http://0.0.0.0:8080).

# Database

A copy of our database is available for development purposes. These are copies of our live database, taken on December 17, 2020. However, user data, user posts, and other personal data has been removed. There are three versions available, depending on your interests:

### [db.sql.gz](http://metabolismofcities.org/media/files/db.sql.gz)

247 Mb (839 Mb uncompressed)

This file contains the entire Metabolism of Cities database, including all geometry and reference spaces. If you want to work with the data platform and you need mapping functionality, this is your file.

### [db-without-geometry.sql.gz](http://metabolismofcities.org/media/files/db-without-geometry.sql.gz)

31 Mb (303 Mb uncompressed)

In this file we have removed ALL the geometry data. That means that none of the mapping functionality will work. However, other than that everything is left the same as the full database above. This database is useful if you would like to work with the data portal but don't need mapping functionality.

### [db-without-spaces.sql.gz](http://metabolismofcities.org/media/files/db-without-spaces.sql.gz)

12 Mb (36 Mb uncompressed)

In this file we removed ALL reference spaces (and therefore also any geometry). This means that there is no infrastructure, boundaries, etc. but also no material stocks and flows data (which is linked to reference spaces). Use this file if you don't care about the data part of the website.

# Tutorials

We made some instruction videos for contributors:

![Installing locally](https://multimedia.metabolismofcities.org/media/records/screenshot_0do6q2O.thumbnail.png)

[Installing Metabolism of Cities locally](https://multimedia.metabolismofcities.org/videos/578485/)

![File structure](https://multimedia.metabolismofcities.org/media/records/Screenshot_2020-12-17_18-52-39.thumbnail.png)

[Metabolism of Cities file structure](https://multimedia.metabolismofcities.org/videos/581189/)

# What to work on?

Before doing any work, check in with us through our online [forum](https://metabolismofcities.org/forum/). We have an online task system where you can see [all open programming tasks](https://metabolismofcities.org/tasks/?type=9&status=open_unassigned&priority=&project=&tag=). Feel free to pick any task and assign it to yourself, but if it is your first time contributing it is highly recommended you leave a note on our site stating your intentions to make sure it fits with our current priorities.

# What if I need help?

Head over to our [forum](https://metabolismofcities.org/forum/) and give us a shout! We'll be glad to help debug any issues you may have with our site. Do note that operating-specific issues may be out of scope, but we will try to help where possible.

**Thanks for your contribution!**
