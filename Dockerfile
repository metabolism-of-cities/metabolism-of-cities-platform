FROM python:3.8.2

# binutils libproj-dev gdal-bin are all required for GeoDjango to work
# See https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/geolibs/#installing-geospatial-libraries
RUN apt-get update -y && \
    apt-get install --auto-remove -y \
      binutils libproj-dev gdal-bin ffmpeg libgdal-dev g++ sqlite3

# proj 6
WORKDIR /opt
RUN wget https://github.com/OSGeo/PROJ/releases/download/8.2.1/proj-8.2.1.tar.gz
RUN tar xvfz proj-8.2.1.tar.gz
WORKDIR /opt/proj-8.2.1
RUN pwd
RUN ./configure
RUN make
RUN make install
RUN export LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

# gdal 3.1
RUN wget http://download.osgeo.org/gdal/3.1.0/gdal-3.1.0.tar.gz
RUN tar xvfz gdal-3.1.0.tar.gz
WORKDIR ./gdal-3.1.0
RUN ./autogen.sh
RUN CPPFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib  ./configure --with-proj=/usr/local/ --with-python=python3 --with-pg --with-geos &&    make &&     make install &&     ldconfig

ENV PYTHONUNBUFFERED 1
RUN mkdir /src
RUN mkdir /static
WORKDIR /src
ADD ./src /src
RUN pip install -r requirements.pip
