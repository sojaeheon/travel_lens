FROM flink:1.18.1-scala_2.12

# ==================================================
# 1️⃣ Python + wget
# ==================================================
RUN apt-get update && \
    apt-get install -y python3 python3-pip wget && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ==================================================
# 2️⃣ PyFlink
# ==================================================
RUN pip install --no-cache-dir \
    apache-flink==1.18.1 \
    psycopg2-binary

# ==================================================
# 3️⃣ Kafka SQL Connector (버전 맞춤)
# ==================================================
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.0/flink-sql-connector-kafka-1.17.0.jar

# ==================================================
# 4️⃣ 🔥 JDBC Connector (이게 빠져 있었음)
# ==================================================
RUN wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.2-1.18/flink-connector-jdbc-3.1.2-1.18.jar \
    -P /opt/flink/lib/

# ==================================================
# 5️⃣ PostgreSQL JDBC Driver
# ==================================================
RUN wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar \
    -P /opt/flink/lib/
