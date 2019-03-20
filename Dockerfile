FROM python:3.7
RUN apt-get update
RUN apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran
#RUN pip install numpy
#RUN pip install scipy==1.0.1
WORKDIR /root
COPY ["Home Oracle/requirements.txt", "Home Oracle/"]
RUN pip install -r "Home Oracle/requirements.txt"
COPY .aws .aws
COPY ["Home Oracle", "Home Oracle"]
COPY ["Data", "Data"]
WORKDIR "Home Oracle"
EXPOSE 8050
CMD ["python", "index.py" ]