FROM python:3.6.3

ENV MONGO_HOST localhost
ENV MONGO_PORT 27017

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

WORKDIR /wiki

COPY ./wikipod.py /wikipod.py
COPY ./wikipedia_app.py /wikipedia_app.py

CMD ["python", "wikipedia_app.py"]