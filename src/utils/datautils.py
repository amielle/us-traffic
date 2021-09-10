import gdown
import os
import pandas as pd

# Loading Data

def create_folder(DIR):
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
        print(f"Created folder '{DIR}' .")
    else:
        print(f"Folder '{DIR}' exists.")


def gdrive_download(url, filename):
    url_id = url.split("/")[5]
    dl_url = f"https://drive.google.com/uc?id={url_id}"
    gdown.download(dl_url, filename, quiet=False)


def load_txtgz(DATA_LOCATION, FILE):
    df = pd.read_csv(os.path.join(DATA_LOCATION,FILE),
                    header=0,
                    sep=',',
                    quotechar='"')

    return df


def load_traffic_datasets(DATA_LOCATION, TRAFFIC_DATA_FILE, 
                          TRAFFIC_STATIONS_FILE):
    """
        Loads data contained in the files to DataFrames
    """
    print(f"Loading traffic data from '{TRAFFIC_DATA_FILE}' ...")
    traffic_data = load_txtgz(DATA_LOCATION, TRAFFIC_DATA_FILE)

    print(f"Loading traffic stations from '{TRAFFIC_STATIONS_FILE}' ...")
    traffic_stations = load_txtgz(DATA_LOCATION, TRAFFIC_STATIONS_FILE)

    print("Finished loading data.")
    return traffic_data, traffic_stations


def load_other_datasets(DATA_LOCATION, FIPS_FILE):

    print(f"Loading FIPS state codes reference from '{FIPS_FILE}' ...")
    fips_cols= ['state_abbreviation', 'fips_code', 'state_name']
    fips_df = pd.read_csv(os.path.join(DATA_LOCATION, FIPS_FILE), 
                            names=fips_cols,
                            header=None)

    print("Finished loading data.")
    return fips_df


def create_fips_ref(fips_df):
    """
        Sets all the state names in the fips_df to lowercase for easier 
        comparisons and makes a dict reference with the FIPS code as 
        the key to shorten code instead of having to match/query the 
        DataFrame repeatedly.
    """
    fips_state_ref = dict(zip(fips_df["fips_code"],
                            [x.lower() for x in fips_df["state_name"]]))

    return fips_state_ref
