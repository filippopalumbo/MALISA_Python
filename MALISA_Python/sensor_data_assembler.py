import pandas as pd

# Read the CSV files into DataFrames
# (Replace with your CSV file path)
data_rug1 = pd.read_csv('/Users/heddaeriksson/Documents/GitHub/MALISA_Python/MALISA_Python/DS_TUG_Floor1')
data_rug2 = pd.read_csv('/Users/heddaeriksson/Documents/GitHub/MALISA_Python/MALISA_Python/DS_TUG_Floor2')
data_seat = pd.read_csv('/Users/heddaeriksson/Documents/GitHub/MALISA_Python/MALISA_Python/DS_TUG_Seat2')


#### SEAT data config #### 
# Insert four columns after the first column (index 0)
for i in range(80):
    data_seat.insert(i+1, f'{i+1}', None) 

# Insert four columns after the 20th column (index 19)
num_columns = len(data_seat.columns)    
for i in range(80):
    data_seat.insert(num_columns+i, f'{i+81}', None)

# Fill missing values with zeros
data_seat.fillna(0, inplace=True)

# Write the modified DataFrame back to a new CSV file
data_seat.to_csv('modified_file.csv', index=False)


#### RUG data config ####
# Create a mirrored version of the selected part 
mirrored_data = data_rug2.iloc[:, ::-1]


#### MERGE data ####

# Merge the DataFrames horizontally using the 'Timestamp' column as the key 
# Merge of both rugs
merged_data_rugs = pd.merge(mirrored_data, data_rug1, on='Timestamp', how='outer')
# Merging seat with rugs
merged_data = pd.merge(merged_data_rugs, data_seat, on='Timestamp', how='outer')

# Fill missing values with zeros
merged_data.fillna(0, inplace=True)

# Sort the DataFrame by the 'Timestamp' column
merged_data.sort_values(by='Timestamp', inplace=True)

# Save the merged and sorted DataFrame to a new CSV file
merged_data.to_csv('merged_data.csv', index=False)
