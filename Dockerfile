FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Update packages and install tools
RUN apt-get update -y && apt-get install -y wget \
  git \
  unzip \
  cmake \
  make \
  pkg-config \
  libtiff-dev \
  libmagic-dev \
  libleptonica-dev \
  ocrmypdf

# Download and compile openjpeg2.1
WORKDIR /tmp/openjpeg
RUN git clone https://github.com/uclouvain/openjpeg.git ./
RUN git checkout tags/v2.3.1
RUN cmake . && make && make install

# Download and compile JBIG2 Encoder
WORKDIR /tmp/jbig2enc
RUN git clone https://github.com/agl/jbig2enc ./
RUN ./autogen.sh && ./configure && make && make install

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

ADD . /code/
