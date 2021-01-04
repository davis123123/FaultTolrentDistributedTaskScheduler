# getting base image ubuntu
FROM python

ADD . /TaskScheduler

WORKDIR /TaskScheduler


MAINTAINER davis pal <daviswong123@gmail.com>

RUN pip install -r requirements.txt
RUN pip show pymongo
CMD ["echo", "Hellow World...! base!!!!!"]



