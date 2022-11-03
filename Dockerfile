FROM ubuntu:kinetic-20220830

RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install nano -y
RUN apt-get install openjdk-8-jre-headless -y


COPY ./ /app
WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 666
EXPOSE 8888

CMD sh app.sh
