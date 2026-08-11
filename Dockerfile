FROM python:3.13-bookworm

WORKDIR /home/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    openjdk-17-jdk \
    wget \
    make \
    procps \
    gcc \
    g++ \
    cmake \
    pkg-config \
    libssl-dev \
    libzstd-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Works with both arm and amd
RUN ln -s $(ls -d /usr/lib/jvm/java-17-openjdk-* | grep -v current | head -1) \
    /usr/lib/jvm/java-17-openjdk-current

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-current
ENV PATH=$JAVA_HOME/bin:$PATH

# Install Spark 
ENV SPARK_VERSION=4.1.2
ENV SPARK_HOME=/opt/spark
ENV SPARK_MAJOR_VERSION=4.0
ENV ICEBERG_VERSION=1.10.1

# archive is throttled and slow
# RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \ 

# dlcdn link is faster but only keeps latest Spark releases; 
RUN wget -q https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# download jar for Iceberg
RUN curl https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.13/${ICEBERG_VERSION}/iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.13-${ICEBERG_VERSION}.jar -Lo $SPARK_HOME/jars/iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.13-${ICEBERG_VERSION}.jar

ENV PATH=$PATH:$SPARK_HOME/bin
ENV PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.9.9-src.zip:${PYTHONPATH}"

COPY ./spark_defaults.conf $SPARK_HOME/conf/spark-defaults.conf
COPY ./log4j2.properties $SPARK_HOME/conf/log4j2.properties
ENV PYSPARK_PYTHON="python3"

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

ENV PYTHON_VERSION=3.13
# RUN uv init --bare --python 3.13
# RUN uv add jupyterlab pyspark pyspark[sql] duckdb jupysql duckdb-engine "grpcio-status>=1.48.1" "zstandard>=0.25.0" grpcio googleapis-common-protos pyarrow toml mcp[cli]

# Install Node.js 22 LTS + npm on Debian Bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://pi.dev/install.sh | sh
RUN pi install npm:pi-mcp-extension
RUN pi install git:github.com/DietrichGebert/ponytail

# command to start jupyter lab
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

CMD ["/startup.sh"]
