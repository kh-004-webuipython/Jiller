FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /config
ADD requirements.pip /config/
RUN pip install -r /config/requirements.pip
RUN mkdir /poker;
WORKDIR /poker