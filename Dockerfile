FROM python:3.8.2

# binutils libproj-dev gdal-bin are all required for GeoDjango to work
# See https://docs.djangoproject.com/en/3.0/ref/contrib/gis/install/geolibs/#installing-geospatial-libraries
RUN apt-get update -y && \
    apt-get install --auto-remove -y \
      binutils libproj-dev gdal-bin ffmpeg

ENV PYTHONUNBUFFERED 1
RUN mkdir /src
RUN mkdir /static
WORKDIR /src
ADD ./src /src
RUN pip install -r requirements.pip
