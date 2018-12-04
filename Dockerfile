FROM debian:stretch-slim

RUN apt-get update
RUN apt-get -y install python-pip python-dev

WORKDIR /parcs

COPY . /parcs

RUN pip install -r requirements.txt

CMD ["./run.sh"]
