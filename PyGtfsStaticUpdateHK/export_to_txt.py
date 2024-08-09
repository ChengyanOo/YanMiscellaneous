import pandas as pd

# Step 1: Read the CSV file into a DataFrame
df = pd.read_csv('updated_stop_to_agency_mapping_kmb_updated.csv')

# Step 2: Export the DataFrame to a text file
df.to_csv('output.txt', index=False, sep='\t')

print("CSV file has been successfully exported to output.txt")