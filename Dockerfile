FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Update packages and install tools
RUN apt-get update -y && apt-get install -y wget \
  git \
  unzip \
  cmake \
  make \
  pkg-config \
  libtiff-dev

# Download and compile openjpeg2.1
WORKDIR /tmp/openjpeg
RUN git clone https://github.com/uclouvain/openjpeg.git ./
RUN git checkout tags/version.2.1
RUN cmake . && make && make install

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

ADD . /code/
