FROM postgres:14

# Instalar dependencias necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-server-dev-14 \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clonar y compilar pgvector
WORKDIR /tmp
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install

# Limpiar
RUN apt-get purge -y --auto-remove build-essential git