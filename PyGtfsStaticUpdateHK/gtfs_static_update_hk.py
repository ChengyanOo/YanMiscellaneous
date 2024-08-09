import datetime
from model.agency import Agency, kmb_route_stop_endpoint, ctb_route_stop_endpoint
from typing import Dict, List, Tuple
import pandas as pd
import requests
import ast
import sys

trip_id_set = set()
agency = 4


def get_all_rows_by_agency_filtered_by_date(
    df: pd.DataFrame,
) -> Dict[int, List[Dict[str, str]]]:
    result = {}
    filtered_df = df[df[datetime.datetime.today().strftime("%A").lower()] == 1]
    for _, row in filtered_df.iterrows():
        agency_id = row["agency_src_id"]
        row_data = row.to_dict()
        if agency_id not in result:
            result[agency_id] = []
        result[agency_id].append(row_data)
    return result


def map_stopId_to_agencySrcId(df: pd.DataFrame) -> None:
    """
    Maps stop_id to stop_src_id and stores the mapping to a CSV file in local storage.

    Args:
    df (pd.DataFrame): The DataFrame containing stop_id and stop_src_id columns.

    Returns:
    None
    """
    stop_to_agency = {}
    for _, row in df.iterrows():
        stop_id = row["stop_id"]
        stop_src_id = row["stop_src_id"]

        if pd.isna(stop_id) or pd.isna(stop_src_id):
            continue

        if stop_id not in stop_to_agency:
            stop_to_agency[stop_id] = []

        if stop_src_id not in stop_to_agency[stop_id]:
            stop_to_agency[stop_id].append(stop_src_id)

    mapping_df = pd.DataFrame(
        {
            "stop_id": list(stop_to_agency.keys()),
            "stop_src_id": list(stop_to_agency.values()),
        }
    )

    mapping_df.to_csv("./local_storage/stop_to_agency_mapping.csv", index=False)


def format_url_with_route_n_direction(url: str, route: str, dir: str) -> str:
    return url.format(route=route, direction=dir)


# Return a list of stops from agency[{"route": "234D", "bound": "O", "service_type": "1", "seq": "32", "stop": "71B7CB659DF54E28"}]
def fetch_agency_data(agency: str, route: str, dir: str) -> List[Dict[str, str]]:
    url = ""
    if agency == 2:
        url = kmb_route_stop_endpoint
    elif agency == 4:
        url = ctb_route_stop_endpoint

    print(format_url_with_route_n_direction(url, dir=dir, route=route))
    response = requests.get(
        format_url_with_route_n_direction(url, dir=dir, route=route)
    )

    dir = "O" if dir.lower() in ["o", "outbound"] else "I"
    if (
        response.status_code != 200
        or len(response.json()["data"]) == 0
        # bound for kmb dir for ctb
        or response.json()["data"][0]["dir"] != dir
    ):
        return []

    return response.json()["data"]


def get_all_unique_trip_ids(
    agency: int, static_data: Dict[int, List[Dict[str, str]]]
) -> None:
    global trip_id_set
    if agency in static_data:
        static_data_by_agency = static_data[agency]
        for record in static_data_by_agency:
            trip_id = record.get("trip_id")
            if trip_id:
                trip_id_set.add(trip_id)


def find_stop_id(df, stop_src_id):
    for index, row in df.iterrows():
        try:
            src_id_list = ast.literal_eval(row["stop_src_id"])
            if stop_src_id in src_id_list:
                return row["stop_id"]
        except KeyError as e:
            print(
                f"KeyError: {e} - Check if the column 'stop_src_id' exists in the DataFrame"
            )
        except SyntaxError as e:
            print(
                f"SyntaxError: {e} - Check the format of the 'stop_src_id' column values"
            )
        except ValueError as e:
            print(f"ValueError: {e} - Check the data in 'stop_src_id' column")
    return None


def update_static_data_by_agency(
    agency: int, df: pd.DataFrame, stop_id_mapping_df: pd.DataFrame
) -> List[str]:
    global trip_id_set

    for trip_id in trip_id_set:
        row = df[df["trip_id"] == trip_id].iloc[0]
        route_src_id = row["route_src_id"]
        dir_src = row["dir_src"]
        if dir_src == "O":
            dir_src = "outbound"
        else:
            dir_src = "inbound"

        agency_data = fetch_agency_data(agency, route_src_id, dir_src)
        for data in agency_data:
            with open(
                f"./tstu_{agency}.csv", "a", newline=""
            ) as file:
                updated_data = {
                    "tstu_id": -1,
                    "trip_id": row["trip_id"],
                    "stop_id": find_stop_id(stop_id_mapping_df, data["stop"]),
                    "stop_sequence": data["seq"],
                    "agency_src_id": agency,
                    "route_src_id": row["route_src_id"],
                    "stop_src_id": data["stop"],
                    "dir_src": row["dir_src"],
                    "service_type_src": row["service_type_src"],
                    "monday": row["monday"],
                    "tuesday": row["tuesday"],
                    "wednesday": row["wednesday"],
                    "thursday": row["thursday"],
                    "friday": row["friday"],
                    "saturday": row["saturday"],
                    "sunday": row["sunday"],
                    "service_id": row["service_id"],
                    "buffer": row["buffer"],
                }
                updated_df = pd.DataFrame([updated_data])
                updated_df.to_csv(file, header=file.tell() == 0, index=False)



df = pd.read_csv("./trip_stop_time_update_upload.txt", delimiter="\t")
data = get_all_rows_by_agency_filtered_by_date(df)
get_all_unique_trip_ids(4, data)
stop_id_mapping_df = pd.read_csv("./local_storage/stop_to_agency_mapping.csv")
update_static_data_by_agency(4, df, stop_id_mapping_df)
