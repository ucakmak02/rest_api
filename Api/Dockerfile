#FROM python:3.6.8
FROM tiangolo/uwsgi-nginx-flask:python3.7

#RUN python -m pip install --upgrade pip

COPY . /src
WORKDIR /src
RUN pip install -r requirements.txt
#RUN python apimain.py
CMD ["python", "api.py"]