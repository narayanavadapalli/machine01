FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install nano -y


COPY ./ /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 666

CMD python3 sampleserver.py
