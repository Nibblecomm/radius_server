#build arguments
FROM ubuntu:xenial-20200326
RUN apt-get update && apt install -y wget
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt install software-properties-common  -y
RUN add-apt-repository ppa:deadsnakes/ppa -y && wget -qO - https://packages.confluent.io/deb/5.5/archive.key |  apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/5.5 stable main" &&  \
    apt-get update && apt install -y python3.7 mysql-client python3.7-dev  \
    libmysqlclient-dev  git libffi-dev libssl-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev libssl-dev libffi-dev librdkafka-dev \
    libxml2-dev libxslt1-dev supervisor build-essential  libsasl2-dev libldap2-dev python3-pip python3.7-distutils curl \
    && rm -rf /var/lib/apt/lists/*


# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

# Upgrade pip to latest version
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt --exists-action w
RUN pip install  --no-binary :all: confluent-kafka


COPY . /app
WORKDIR /app

EXPOSE 1812
EXPOSE 1813
RUN chmod +x wait-for-it.sh
CMD ["python server.py"]




