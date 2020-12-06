FROM python:3.7.5

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

ADD requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

CMD ["python3", "gazon_city.py"]