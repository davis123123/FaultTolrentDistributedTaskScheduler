# getting base image ubuntu
#FROM ubuntu:16.04
FROM python

ADD . /TaskScheduler/master

WORKDIR /TaskScheduler/master


MAINTAINER davis pal <daviswong123@gmail.com>
EXPOSE 80
EXPOSE 5001	
RUN pip install -r requirements.txt
RUN pip show pymongo

CMD ["echo", "Hellow World...! from my first docker image"]
#CMD ["master.py"]

