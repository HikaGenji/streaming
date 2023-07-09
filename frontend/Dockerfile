FROM python:latest


#Labels as key value pair
LABEL Maintainer="jfp"


# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY frontend.py ./
# Now the structure looks like this '/usr/app/src/test.py'

RUN pip install pandas psycopg2 plotly streamlit sqlalchemy sqlalchemy-risingwave
#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]