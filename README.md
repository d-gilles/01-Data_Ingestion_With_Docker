# Data Ingestion Pipeline with Docker
This project demonstrates a data ingestion using **Docker** containers, **PostgreSQL**, and **Python**. We set up multiple containers to run a PostgreSQL database, pgAdmin, and a data ingestion script, connected through a Docker network. The pipeline fetches data from the web and inserts it into the database, showcasing an efficient and scalable environment for data processing.

### Overview:
**Docker Network:** Enables communication between the containers.</br>
**PostgreSQL Database:** Container running PostgreSQL.</br>
**pgAdmin:** Container running pgAdmin for database management.</br>
**Data Ingestion:** Python script for fetching and inserting data into the database.</br>
**Docker-Compose:** Simplifies container orchestration and management.</br>
**Docker Container** Build and run a docker container running a Python script to ingest a second table to the db.

## run a network in Docker
```bash
docker network create pg-network
```

## run local postgres server in network
``` bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name=pgdatabase \
  postgres:13
```

The datebase can now be accessed by `pgcli` from bash,
or by sqlachemist using python.

## run pgAdmin to connect to postgres server in network
```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name=pgAdmin \
  dpage/pgadmin4
```

This container runs a web interface for accessing the db. You can find the interface [here](http://localhost:8080/browser/)

To access pgAdmin use USER:`admin@admin.com` und PWD: `root`.

Connect to the database using:
- db name: pgdatabase
- user : root
- PWD : root


## write a notebook to ingest the first table to the database
  look at the upload-data.ipynb
### convert the upload-data.ipynb to python file:
```bash
jupyter nbconvert --to=script upload-data.ipynb
```
Clean up a bit and save as upload-data.py

# run python file to insert date to database:

First we give the url as environmet variable in bash and then run the script locally. This file is mend to run local with the command below:

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

python upload-data.py \
    --pwd=root \
    --user=root \
    --host=localhost \
    --database_name=ny_taxi \
    --port=5432 \
    --url=${URL} \
    --table_name=yellow_taxi_trips \
    --zip=TRUE
```

Now the first table is created in the pg db.
Stop the docker containers by running
`docker ps` and find the container ids to stop.
Run `docker stop <id>` to stop the 2 containers.

# Use docker-compose to start the 2 containers in one process.

``` bash
services:   # services we want to include
  # 1. service
  pgdatabase:
    image: postgres:13
    # environment variables
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    # volumes to mount
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    # port mapping
    ports:
      - "5432:5432"
    networks:
      - pg-network

  # 2. service
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"
    networks:
      - pg-network

# network
networks:
  pg-network:
    driver: bridge

```
to start this run:

```bash
docker-compose up -d # -d = detached mode
```

to stop:
``` bash
docker-compose down
```



# Download another file

To ingest the next table I wrote a notebook ingest_data.ipynb and converted it to ingest_data.py. The dockerfile is mend to build an image to run this file in a container and ingest more data to the db.

Use `docker build --rm -t ingest_data:v001 . ` to build to image.

If you get an error:
```bach
failed to solve with frontend dockerfile.v0:
failed to read dockerfile:
error from sender:
open ny_taxi_postgres_data: permission denied
```
use this command to allow access to `ny_taxi_postgres_data` folder:</br>
`sudo chmod  777 ny_taxi_postgres_data`

Set the URL where the data is located :

`URL='https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'`

And finally run the docker container:

``` bash
docker run -it \
  --network=data-ingestion-with-docker_pg-network \
  taxi_ingest:v001 \
    --pwd=root \
    --user=root \
    --host=pgdatabase \
    --db=ny_taxi \
    --port=5432 \
    --url=${URL} \
    --table_name=zones \
    --zip=False
```
