import os
from tqdm import tqdm


def main():
    from utils import preprocess, datautils
    from utils.config import filenames

    DATA_LOCATION = os.path.join(os.getcwd(), 'data')
    datautils.create_folder(DATA_LOCATION)

    traffic_data, traffic_stations = datautils. load_traffic_datasets(DATA_LOCATION,
                                                                      filenames["TRAFFIC_DATA"],
                                                                      filenames["TRAFFIC_STATIONS"])

    traffic_data = preprocess.get_new_vol_cols(traffic_data)
    traffic_data = preprocess.modify_temporal_cols(traffic_data)

    processed_dir = os.path.join(DATA_LOCATION, "processed")
    datautils.create_folder(processed_dir)

    verbose = False

    for fips_state_code in tqdm(traffic_data["fips_state_code"].unique()):
        sub_df = preprocess.get_filtered_df(fips_state_code=fips_state_code,
                                            save_dir=processed_dir,
                                            traffic_data=traffic_data,
                                            traffic_stations=traffic_stations)
        model_input_dir = os.path.join(processed_dir, str(fips_state_code))
        datautils.create_folder(model_input_dir)

        for station_id in tqdm(sub_df["station_id"].unique()):
            processed_df = preprocess.get_transformed_vol_df(station_id,
                                                             sub_df=sub_df,
                                                             save_dir=model_input_dir,
                                                             verbose=verbose)


if __name__ == "__main__":
    main()
