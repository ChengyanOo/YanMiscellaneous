
import requests
from google.transit import gtfs_realtime_pb2
import csv
import time

def fetch_gtfs_realtime_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_gtfs_realtime_data(data):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)
    return feed

def append_to_csv(feed, filename):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['entity_id', 'trip_id', 'stop_sequence', 'arrival_time', 'stop_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        for entity in feed.entity:
            trip_id = entity.trip_update.trip.trip_id
            for update in entity.trip_update.stop_time_update:
                writer.writerow({
                    'entity_id': entity.id,
                    'trip_id': trip_id,
                    'stop_sequence': update.stop_sequence,
                    'arrival_time': update.arrival.time,
                    'stop_id': update.stop_id
                })

def initialize_csv(filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['entity_id', 'trip_id', 'stop_sequence', 'arrival_time', 'stop_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

if __name__ == "__main__":
    urls_and_filenames = [
        ("https://googl.transit.mapking.com/gtfs-realtime/trip-id/KMB_11D_N_fw?key=eFovRXRjNkZJdUFjZTdDc3B0a3ZRU2puOUJBMzNtdzFDVXJ1d2tRaEx6QT0=", "gtfs_realtime_data_kmb.csv"),
        ("https://googl.transit.mapking.com/gtfs-realtime/trip-id/CFB_48_C_wd?key=eFovRXRjNkZJdUFjZTdDc3B0a3ZRU2puOUJBMzNtdzFDVXJ1d2tRaEx6QT0=", "gtfs_realtime_data_cfb.csv")
    ]
    
    # Initialize the CSV files with headers
    for _, filename in urls_and_filenames:
        initialize_csv(filename)

    while True:
        for url, filename in urls_and_filenames:
            try:
                gtfs_data = fetch_gtfs_realtime_data(url)
                feed = parse_gtfs_realtime_data(gtfs_data)
                append_to_csv(feed, filename)
                print(f"GTFS Realtime data appended to {filename}")
            except Exception as e:
                print(f"An error occurred with URL {url}: {e}")
        
        # Wait for 5 minutes before fetching the data again
        time.sleep(1)
