import argparse
import os
from config import urls, filenames
from datautils import create_folder, gdrive_download

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", type=str,
                        help="Indicates directory/location where the data is to be stored.")
    args = parser.parse_args()

    if args.datadir == None:
        print("Missing argument. Sample usage:")
        print(r"python ./src/utils/datasetdownloader.py -d <data-directory>")
        print("Use -h flag for more details.")
        os._exit(0)

    create_folder(args.datadir)
    os.chdir(args.datadir)

    for name in urls:
        gdrive_download(urls[name], filenames[name])

    print(f"Downloaded data under '{args.datadir}' .")


if __name__ == "__main__":
    main()