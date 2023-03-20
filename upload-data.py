import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from time import time
import os
import re

# This file is mend to be run locally, not in the docker container
# To run it from a container, use the ingest_data.py file

URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

filename_match = re.search(r"/([^/]+)$", URL)

if filename_match:
    filename = filename_match.group(1)
    print("Filename in URL: ", filename)
else:
    print("No filename found in URL.")

if os.path.exists("raw_data"):
    print("The path /raw_data exists.")

else:
    print("The path /raw_data does not exist - I create it.")
    os.system(f"mkdir -p raw_data")

os.system(f"wget {URL} -O raw_data/{filename}")
file = f'raw_data/{filename}'
df = pd.read_csv(file, compression='gzip')

# change date to timestamp
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)


# creates a engine, that can later be connected to the database.
# Takes the kind of database://user:password@host:port/table_name
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

df_iter = pd.read_csv(file, iterator=True, chunksize=100000)

#instead of loading the whole file, we create an iterater from a dataset
df = next(df_iter) # next is a python command, that by running selects the next iteration

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime) #see above
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

#create a data table in the database
df.head(0).to_sql(name='yellow_taxi_trips', con=engine, if_exists='replace') # creates a table in the database (engine) with no date in it

while True:
    t_start = time()
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime) #see above
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    df.to_sql(name='yellow_taxi_trips', con=engine, if_exists='append')
    t_end = time()
    print('inserted another chunk ... took %.3f seconds' % (t_end - t_start))
