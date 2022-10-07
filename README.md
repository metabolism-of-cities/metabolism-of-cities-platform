# Overview

This repository contains the source code of [Metabolism of Cities](https://metabolismofcities.org/). The following technologies are used:

- Django 3
- Python 3
- PostgreSQL 
- PostGIS
- Docker

In order to meaningfully contribute to this project (or clone it and use it for your own purposes), you should ideally be comfortable with (or willing to learn about) the aforementioned technologies. You can make a meaningful contribution if you know either about python/Django, or about HTML/CSS/Javascript (allowing you to contribute with back-end or front-end programming, respectively).

The tech work on Metabolism of Cities has so far be done by a small number of people. However, we are very keen to get others involved. Due to the nature of the work, it would be ideal if you have a background both in urban metabolism/industrial ecology, and in web development. If you are not very familiar with our topic matter, but you are a keen programmer and willing to learn and spend time on this project, then we are happy to assist you in that journey.

We don't manage tasks through github, but instead have an online forum and [task list](https://metabolismofcities.org/tasks/?type=9&status=open_unassigned&priority=&project=&tag=) integrated on our website. If you are thinking of contributing, please open a new [forum thread](https://metabolismofcities.org/forum/) and let us know what you have in mind.

# Getting started

DISCLAIMER: the system is currently running in a Linux environment only, but it should also work perfectly fine on Windows or other operating systems if you have Docker running on it. The commands shown below, however, are Linux specific, but these are simply copy / create directory commands that should be easy enough in any OS.

To get started with this project, do the following:

- Clone the repository on your local machine
- Install Docker and specifically [Docker Compose](https://docs.docker.com/compose/)
- Create a number of baseline directories (see below)
- Create a configuration file (see below)
- Build your container
- Import our database

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

Replace "db.sql" for the name of your database file (which should be uncompressed before loading it). After the database is loaded, you will need to reload your container (CTRL+C followed by:

    $ sudo docker-compose up

And the website should be up and running at [http://0.0.0.0:8000](http://0.0.0.0:8000) and adminer to manage the database is available at [http://0.0.0.0:8080](http://0.0.0.0:8080).

NOTE: there may be additional database migrations that are not yet applied to this database. You can run the migrations by running:

    $ ./migrate

From the root directory of the project. This is a shortcut to migrate any unapplied migrations in the docker container (check out the file contents to see what commands it runs).

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

Also see the [Programming contributor support videos](https://multimedia.metabolismofcities.org/videos/collection/968/) in our multimedia library.

# What to work on?

Before doing any work, check in with us through our online [forum](https://metabolismofcities.org/forum/). We have an online task system where you can see [all open programming tasks](https://metabolismofcities.org/tasks/?type=9&status=open_unassigned&priority=&project=&tag=). Feel free to pick any task and assign it to yourself, but if it is your first time contributing it is highly recommended you leave a note on our site stating your intentions to make sure it fits with our current priorities.

# What if I need help?

Head over to our [forum](https://metabolismofcities.org/forum/) and give us a shout! We'll be glad to help debug any issues you may have with our site. Do note that operating-specific issues may be out of scope, but we will try to help where possible.

**Thanks for your contribution!**


## Macbook installation

### Pre-requisites

1. postgres + postgis + gdal + libgeoip (using brew)
2. pip
3. pyenv/virtualenv

### Clone the repo

```bash
git clone https://github.com/metabolism-of-cities/metabolism-of-cities-platform.git
```

create `settings.py` file

```bash
cd metabolism-of-cities-platform/src
mkdir media
mkdir logs
mkdir static
cp ie/settings.sample.py ie/settings.py
```

### Install virtualenv and install project packages

```bash
pyenv virtualenv 3.10.5 metabolism
pyenv activate metabolism
```

create a `.env` file with content

```bash
pyenv activate metabolism

export GDAL_LIBRARY_PATH="$(gdal-config --prefix)/lib/libgdal.dylib"
export GEOS_LIBRARY_PATH=/opt/homebrew/lib/libgeos_c.dylib
```

Please note that the `GEOS_LIBRARY_PATH` value might be different due to different macos, you can check it here https://gist.github.com/codingjoe/a31405952ec936beba99b059e665491e

then run

```bash
source .env
```

Install needed packages

```bash
pip install requirements_macos.pip
```

### Setup database for the project

Connect to psql using `psql -u root -p` and run

```
DROP DATABASE IF EXISTS metabolism;

CREATE DATABASE metabolism;

CREATE ROLE metabolism WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE metabolism TO metabolism;
ALTER USER metabolism SUPERUSER;
```

We need `metabolism` user as a superuser, as this needs to create a test database and run test on.

### Migrate and runserver

```bash
python manage.py migrate
python manage.py runserver
```

Open localhost:8000 on web browser and you will see an error page with message "Project matching query does not exist.". This is OK, as we haven't imported the test data yet.


### Import database

There are 3 databases to import (detail: https://github.com/metabolism-of-cities/metabolism-of-cities-platform#dbsqlgz)

Download any of them, and import to the current database:

```bash
psql -U metabolism metabolism < db.sql
```

After that, migrate the database
```bash
python manage.py migrate
```

Then create first project and other related data:

Open Django shell_plus

```bash
python manage.py shell_plus
```

and run those statements as below

```bash
Project.objects.create(type=ProjectType.objects.first(), slug='staf')
ProjectDesign.objects.create(project_id=Project.objects.all()[0].id)
```

Then exit, and run

```bash
python manage.py createsuperuser
```

Create your own superuser, email and username should be the same, ex: joe@gmail.com

Run the server
```bash
python manage.py runserver
```

Open the page http://localhost:8000/ and login with the superuser you have created.


## Docker on Macbook

```bash
docker-compose build
ENVIRONMENT=docker docker-compose up
```
