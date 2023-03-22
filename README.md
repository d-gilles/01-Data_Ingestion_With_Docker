# Data Ingestion Pipeline with Docker
This project demonstrates a data ingestion pipeline using **Docker** containers, **PostgreSQL**, and **Python**. We set up multiple containers to run a PostgreSQL database, pgAdmin, and a data ingestion script, connected through a Docker network. The pipeline fetches data from the web and inserts it into the database, showcasing an efficient and scalable environment for data processing.

### Overview:
**Docker Network:** Enables communication between the containers.</br>
**PostgreSQL Database:** Container running PostgreSQL.</br>
**pgAdmin:** Container running pgAdmin for database management.</br>
**Data Ingestion:** Python script for fetching and inserting data into the database.</br>
**Docker-Compose:** Simplifies container orchestration and management.</br>
**Docker Container:** Build and run a docker container running a Python script to ingest a second table to the database.</br>

## Install Requirements
To install all the required dependencies for this project, run:</br>
`pip install -r requirements.txt`</br>
Additionally, you need a Docker daemon running on your machine to handle the Docker-related tasks.

## Create a Network in Docker
```bash
docker network create pg-network
```

## Run Local PostgreSQL Server in Network
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
The PostgreSQL Docker image we use can be found [here](
https://hub.docker.com/layers/library/postgres/13/images/sha256-b23f1053795f3ecbad72264caaad696c241827e659da6d18c576e04b773ff9a1?context=explore)

The datebase can now be accessed by `pgcli` from bash,
or by sqlachemist using python.

## Run pgAdmin to Connect to PostgreSQL Server in Network
```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name=pgAdmin \
  dpage/pgadmin4
```
The pgAdmin Docker image we use can be found [here](https://hub.docker.com/r/dpage/pgadmin4)

This container runs a web interface for accessing the database. You can find the interface [here](http://localhost:8080/browser/)

To access pgAdmin use USER:`admin@admin.com` und PWD: `root`.

Connect to the database using:
- db name: pgdatabase
- user : root
- PWD : root


## Write a Notebook to Ingest the First Table to the Database
  Refer to the upload-data.ipynb file.
### Convert the upload-data.ipynb to Python File:
```bash
jupyter nbconvert --to=script upload-data.ipynb
```
Clean up a bit and save as upload-data.py

# Run Python File to Insert Data to Database:

First, set the URL as an environment variable in bash and then run the script locally. This file is meant to be run locally with the command below:
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

Now the first table is created in the PostgreSQL database.
Stop the Docker containers by running
`docker ps` and find the container IDs to stop.
Run `docker stop <id>` to stop the 2 containers.

# Use Docker-Compose to Start the 2 Containers in One Process

The docker-compose.yaml looks like this:

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



# Download Another File

To ingest the next table, I wrote a notebook ingest_data.ipynb and converted it to ingest_data.py. The Dockerfile is meant to build an image to run this file in a container and ingest more data to the database.

Use `docker build --rm -t taxi_ingest:v001 .` to build the image.

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
docker run -it --rm \
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
