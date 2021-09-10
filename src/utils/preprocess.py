import os
import pandas as pd
import numpy as np

common_cols = ["direction_of_travel",
               "fips_state_code",
               "functional_classification",
               "lane_of_travel",
               "station_id"]
temporal_cols = ["date",
                 "day_of_data",
                 "day_of_week",
                 "month_of_data",
                 "year_of_data"]
spatial_cols = ["fips_county_code", "latitude", "longitude"]

new_traffic_vol_cols = [str(x) for x in range(0, 24)]
sub_df_cols = temporal_cols + new_traffic_vol_cols + common_cols
historical_vol_cols = ["date"] + new_traffic_vol_cols


def get_new_vol_cols(traffic_data):
    traffic_vol_cols = [
        word for word in traffic_data.columns if 'traffic_volume_counted' in word]
    traffic_data.rename(columns=dict(zip(traffic_vol_cols,
                                     new_traffic_vol_cols)), inplace=True)

    return traffic_data


def modify_temporal_cols(traffic_data):
    traffic_data["date"] = pd.to_datetime(
        traffic_data["date"], format='%Y-%m-%d')
    traffic_data = get_new_vol_cols(traffic_data)
    traffic_data.loc[traffic_data["day_of_week"] == 1, "day_of_week"] = 8
    traffic_data["day_of_week"] -= 2

    return traffic_data


def save_df_feather(df, file_dir, filename, verbose=True):
    file_path = os.path.join(file_dir, f"{filename}.fea")
    df.to_feather(file_path)
    if verbose:
        print(f"Saved file {file_path}")


def read_df_feather(file_dir, filename):
    file_path = os.path.join(file_dir, f"{filename}.fea")
    df = pd.read_feather(file_path, use_threads=True)
    return df


def get_filtered_df(fips_state_code, save_dir,
                    traffic_data=None, traffic_stations=None, overwrite=False):
    file_path = f"{os.path.join(save_dir, str(fips_state_code))}.pkl"

    if overwrite == False and os.path.isfile(file_path):
        print(f"File already exists. Retrieving DataFrame from '{file_path}'.")
        df = read_df_feather(save_dir, filename=fips_state_code)
        return df

    sub_df_cols = temporal_cols + new_traffic_vol_cols + common_cols
    sub_df = traffic_data[traffic_data["fips_state_code"]
                          == fips_state_code][sub_df_cols]

    df = pd.merge(sub_df, traffic_stations[traffic_stations["fips_state_code"] == fips_state_code]
                  [common_cols + spatial_cols], on=common_cols)
    df["day_vol"] = df[new_traffic_vol_cols].sum(axis=1).values

    save_df_feather(df, save_dir, filename=fips_state_code)

    return df


def get_transformed_vol_df(station_id, sub_df=None, save_dir=None, verbose=True, overwrite=False):
    file_path = f"{os.path.join(save_dir, station_id)}.fea"

    if overwrite == False and os.path.isfile(file_path):
        if verbose:
            print(
                f"File already exists. Retrieving DataFrame from '{file_path}'.")
        processed_df = read_df_feather(save_dir, filename=station_id)
        return processed_df

    col_timestamp = "date"
    col_trafficvol = "traffic_volume"

    station_df = sub_df[sub_df["station_id"]
                        == station_id][historical_vol_cols]
    sum_station_df = pd.DataFrame()
    dates = list(station_df[col_timestamp].unique())

    if verbose:
        print(
            f"Calculating total hourly volume collected per timestamp from station {station_id}.")
        iter = tqdm(dates)
    else:
        iter = dates
    for date in iter:
        date_condition = station_df[col_timestamp] == date
        sum_df = station_df[date_condition].sum()
        sum_df[col_timestamp] = date

        sum_station_df = sum_station_df.append(sum_df, ignore_index=True)

    row_idxs = range(0, sum_station_df.shape[0])
    if verbose:
        print(f"Transforming DataFrame with hourly volume rows.")
        iter = tqdm(row_idxs)
    else:
        iter = row_idxs
    dates = sum_station_df[col_timestamp].to_list()
    hourly_volumes = sum_station_df[new_traffic_vol_cols].to_numpy()

    all_volumes = []
    timestamps = []

    hour_delta = [np.timedelta64(hour, 'h') for hour in range(0, 24)]

    for row_cnt in iter:
        sub_timestamps = [dates[row_cnt] + hour for hour in hour_delta]
        sub_vols = list(hourly_volumes[row_cnt])

        timestamps += sub_timestamps
        all_volumes += sub_vols

    processed_df = pd.DataFrame()
    processed_df[col_timestamp] = timestamps
    processed_df[col_trafficvol] = all_volumes
    processed_df = processed_df.sort_values(
        by=[col_timestamp]).reset_index(drop=True)

    if save_dir != None:
        save_df_feather(df=processed_df,
                        file_dir=save_dir,
                        filename=station_id,
                        verbose=verbose)

    return processed_df


def get_dataset_splits(df, test_count=61, datetime_unit="D", ratio_split=False, temporal_split=True):
    """
    test_count : 61 days for November (30 days) and December (31 days)
    datetime_unit : "D" to indicate days
    """

    col_timestamp = "date"

    val_ratio = .15
    test_ratio = .15
    train_ratio = 1 - (test_ratio + val_ratio)

    temporal_limit = df[col_timestamp].max(
    ) - np.timedelta64(test_count, datetime_unit)

    if temporal_split:
        train_df = df[df[col_timestamp] <= temporal_limit]
        val_df = None
        test_df = df[df[col_timestamp] > temporal_limit]
    elif ratio_split:
        train_range = int(df.shape[0]*train_ratio)
        val_range = int(df.shape[0]*val_ratio)

        train_df = df.iloc[0:train_range]
        val_df = df.iloc[train_range:train_range+val_range]
        test_df = df.iloc[train_range+val_range:]

    return train_df, val_df, test_df


def get_sliding_windows(df, n_in=1, n_out=1, dropnan=True):
    cols = list()

    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))

    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))

    # put it all together
    windowed_entries = pd.concat(cols, axis=1)

    # drop rows with NaN values
    if dropnan:
        windowed_entries.dropna(inplace=True)

    windowed_entries = windowed_entries.values
    X_values, y_values = windowed_entries[:, :-1], windowed_entries[:, -1]

    return X_values, y_values
