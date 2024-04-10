
import pandas as pd
import duckdb

# read csv files and translate epoch to human time, rename column to timestamp
def read_file(filename):
    data = duckdb.sql(f"""
SELECT
    to_timestamp(Timestamp) as timestamp,
    * EXCLUDE(Timestamp),
FROM read_csv('{filename}')
""").df()
    return data

def resample_files(dfs):
    resampled_dfs = []
    for df in dfs:
        # Convert epoch timestamps to human-readable timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        # Resample at a frequency of 10Hz and set NaN to last recorded value value (forward fill)
        df_resampled = df.resample('100ms').mean().ffill()  
        resampled_dfs.append(df_resampled)
    return resampled_dfs

# Find which file has the latest starttime
def find_latest_start_time(dfs):
    latest_start_time = dfs[0].index.min()
    for df in dfs:
        df_min_date = df.index.min()
        if df_min_date > latest_start_time:
            latest_start_time = df_min_date
    return latest_start_time

# Synchronize files according to the latest starttime
def syncronize_start_time(dfs, start_time):
    syncronized_dfs = []
    for df in dfs:
        mask = df.index >= start_time
        df = df[mask]
        syncronized_dfs.append(df)
    return syncronized_dfs

def synchronize_end_time(df1, df2):
    if len(df1) > len(df2):
        df1 = df1.iloc[:len(df2)]  # Truncate df1 to match the length of df2
    elif len(df2) > len(df1):
        df2 = df2.iloc[:len(df1)]  # Truncate df2 to match the length of df1
    return df1, df2

def process(filepath_floor_1, filepath_floor_2, filepath_seat, initials, test_id):
    #df_floor_1 = read_file(filepath_floor_1)
    #df_floor_2 = read_file(filepath_floor_2)
    #df_seat = read_file(filepath_seat)

    df_floor_1 = pd.read_csv(filepath_floor_1)
    df_floor_2 = pd.read_csv(filepath_floor_2)
    df_seat = pd.read_csv(filepath_seat)

    # Resample files at 10Hz
    df_floor_1, df_floor_2, df_seat = resample_files([df_floor_1, df_floor_2, df_seat])

    # Synchronize the starting timestamps
    start_time = find_latest_start_time([df_floor_1, df_floor_2, df_seat])
    df_floor_1, df_floor_2, df_seat = syncronize_start_time([df_floor_1, df_floor_2, df_seat], start_time)

    # Synchronize the ending timestamps on the two floor mats
    df_floor_1, df_floor_2 = synchronize_end_time(df_floor_1, df_floor_2)

    df_floor_1.to_csv(f'MALISA_Python/processed_data/{initials}_{test_id}_floor1.csv')
    df_floor_2.to_csv(f'MALISA_Python/processed_data/{initials}_{test_id}_floor2.csv')
    df_seat.to_csv(f'MALISA_Python/processed_data/{initials}_{test_id}_seat.csv')






