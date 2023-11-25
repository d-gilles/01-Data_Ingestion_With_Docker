network:
	docker network create pg-network

postgresql:
	docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name=pgdatabase \
  postgres:13

pgadmin:
	docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  --network=pg-network \
  --name=pgAdmin \
  dpage/pgadmin4

ingest:
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

ingest-zones:
	URL='https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'
	docker run -it --rm \
		--network=01-data_ingestion_with_docker_pg-network \
		taxi_ingest:v001 \
		--pwd=root \
		--user=root \
		--host=pgdatabase \
		--db=ny_taxi \
		--port=5432 \
		--url=${URL} \
		--table_name=zones \
		--zip=False
