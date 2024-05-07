FROM postgres

WORKDIR /tmp/db

RUN mkdir /data && chown postgres /data

# Initialize with custom schema
COPY schema.sql /docker-entrypoint-initdb.d/

