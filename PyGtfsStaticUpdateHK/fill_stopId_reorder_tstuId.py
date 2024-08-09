import pandas as pd
import ast


def get_file(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


df = get_file("./local_storage/stop_to_agency_mapping.csv")


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


updated_data_df = get_file("./tstu_2_4.csv")

# Update tstu_id and stop_id
for index, row in updated_data_df.iterrows():
    # Update tstu_id
    updated_data_df.at[index, "tstu_id"] = index + 1

    # Update stop_id
    stop_src_id = row["stop_src_id"]
    stop_id = find_stop_id(df, stop_src_id)
    updated_data_df.at[index, "stop_id"] = stop_id
    print(index)

    # Save the updated DataFrame to a new CSV file
updated_data_df.to_csv("./tstu_2_4_updated.csv", index=False)
