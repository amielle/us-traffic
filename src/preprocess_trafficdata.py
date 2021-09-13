import argparse
import os
from tqdm import tqdm
from utils import preprocess, datautils
from utils.config import filenames
from utils.datautils import create_folder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", type=str,
                        help="Indicates directory/location where the data is to be stored.")
    args = parser.parse_args()

    if args.datadir == None:
        print("Missing argument. Sample usage:")
        print(r"python ./src/utils/preprocess_trafficdata.py -d <data-directory>")
        print("Use -h flag for more details.")
        os._exit(0)

    DATA_LOCATION = args.datadir
    datautils.create_folder(DATA_LOCATION)
    os.chdir(DATA_LOCATION)

    traffic_data, traffic_stations = datautils. load_traffic_datasets(DATA_LOCATION,
                                                                      filenames["TRAFFIC_DATA"],
                                                                      filenames["TRAFFIC_STATIONS"])

    traffic_data = preprocess.get_new_vol_cols(traffic_data)
    traffic_data = preprocess.modify_temporal_cols(traffic_data)

    processed_dir = os.path.join(DATA_LOCATION, "processed")
    datautils.create_folder(processed_dir)

    verbose = False

    # Can be modified to traffic_data["fips_state_code"].unique()
    # if running for the entire dataset. Currently does not yet include
    # optimized operations and will run slow. Preprocessed data may be
    # downloaded through datasetdownloader.py script in the same directory.
    codes = traffic_data["fips_state_code"].value_counts()[0:11].index
    for fips_state_code in tqdm(codes):
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
