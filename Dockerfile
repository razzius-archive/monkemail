FROM ubuntu

MAINTAINER Razzi Abuissa

RUN apt-get update

RUN apt-get install -y tar git curl wget dialog net-tools build-essential

RUN apt-get install -y python python-dev python-distribute python-pip

RUN apt-get install -y libtinfo-dev libncurses5-dev libpq-dev

RUN git clone https://github.com/razzius/monkemail.git

# Add environment variables

ADD environment.sh environment.sh

RUN /bin/bash environment.sh


WORKDIR monkemail

RUN pip install -r requirements.txt

CMD python server.py

EXPOSE 8000
