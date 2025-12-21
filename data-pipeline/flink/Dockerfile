FROM flink:1.18.1

# Python 설치
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python

# PyFlink 설치
RUN pip install apache-flink==1.18.1 psycopg2-binary

# PostgreSQL JDBC Driver
RUN wget https://jdbc.postgresql.org/download/postgresql-42.7.3.jar \
    -P /opt/flink/lib/
