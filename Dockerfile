FROM python:3.7-alpine
RUN apt-get update
RUN apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran
RUN pip install numpy
RUN pip install scipy==1.0.1
RUN pip install -r src/requirements.txt
WORKDIR /src
EXPOSE 8050
CMD ["python", "index.py" ]
