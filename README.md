# US Traffic (2015)

<p align="center"><img src="imgs/anims/sample_traffic.gif" ></p>

The repository contains analysis of traffic volume trends from [2015 US traffic data](https://www.kaggle.com/jboysen/us-traffic-2015) with simple proofs-of-concept (PoC) to show possibility of using the data for forecasting. Additional insights are also included in this README to show possible use cases and how to extend our findings.

Results of the analysis and models may be reproduced by following the steps under *1. Prerequisites* then *2. Usage guide*. It's also possible to look at the *3. Summary of findings* section to check the overview of the repository contents.

## Table of Contents

- [1. Prerequisites]()
  - [1.1 Dependencies]()
  - [1.2 Download the dataset]()
- [2. Usage guide]()
- [3. Summary of findings]()
  - [3.1 Data Patterns and Feature Engineering]()
    - [3.1.1 Introduction to the data and initial assumptions]()
    - [3.1.2 Temporal]()
      - Day of Month
      - Day of Week
      - Day of Week and Hour of Day
      - Seasonal Decomposition and Stationarity
    - [3.1.3 Spatial]()
      - Incorrect Latitude and Longitude values
      - Correlation between station count and traffic
      - Traffic volume trends comparison for urban and rural areas
    - [3.1.4 Features for forecasting]()
  - [3.2 Forecasting PoC]()
  - [3.3 Insights and recommendations]()

## 1. Prerequisites

### 1.1 Dependencies

1. Install the latest stable version of Python 3 and Jupyter in the system. Additionally, the user can also opt to create and activate a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html) for testing. 
2. Install the required libraries. Ensure that there are proper permissions and certificates (if needed) when installing.
```
pip install -r .\requirements.txt
```

### 1.2 Download the dataset

The user can download the [Kaggle dataset](https://www.kaggle.com/jboysen/us-traffic-2015) manually and unpack the files to *us-traffic\src\data* or **download the data through the following script**:
```
python ./src/datasetdownloader.py -d "<git-repo-directory>/us-traffic/src/data/"
```
Modify the command above with the appropriate <git-repo-directory> value. For ease of use, the notebooks have a default configuration that sets the data directory as *src/data* relative to the *us-traffic* folder location as shown above. The user can also opt to modify the `DATA_LOCATION` variables in the notebook when testing if the data is located somewhere else.

## 2. Usage guide

The repository contains the following structure:

```
us-traffic
│   
└───imgs
│   └───anims
│   └───eda
│   │   └─── ...
└───src
|   |   datasetdownloader.py
|   |   preprocess_trafficdata.py
│   │   ...
│   │
│   └───data 
|   │   |    dot_traffic_2015.txt.gz
|   │   |    dot_traffic_stations_2015.txt.gz
│   │   |
|   │   └─── ...
│   │
│   └───html 
│   └───notebooks 
|   │   |    1. EDA.ipynb
|   │   |    2. Feature Engineering.ipynb
|   │   |    3. Forecasting models.ipynb
|   │   └─── ...
│   └───utils
|   ...
...
```

`data` - Contains the data used for analysis. In this repository, other data such as *fips_code.csv* and *fips_latlong.csv* were manually collected and verified through available government websites to cross check state names per FIPS state code and approximate coordinates per state.
  
`html` - Since map plots in Jupyter Notebooks are not visible through GitHub, HTML files are provided to access the dynamic graphs (e.g. station plots which were based on and modified from [this notebook](https://www.kaggle.com/frankcorrigan/end-to-end-data-science-project)).
  
`notebooks` - Contains Jupyter notebooks for the analysis. The notebooks are numbered in order of how it should be run.
  
`utils` - Contains utility functions used by the files under `notebooks`. Separated for easier reuse.

## 3. Summary of findings

### 3.1 Data Patterns

#### 3.1.1 Introduction to the data and initial assumptions

During our initial analysis, we can see from the data that there are hourly entries for traffic volume data collected by stations for a given state in the US for the entire year of 2015. Per state, there are counties and more spatial information such as urban vs. rural, longitude, and latitude values. Upon checking the data, there are gaps between daily entries but no null values were found for the hourly entries. We assume that the timezones of the datapoints are relative to the location where the traffic volume data is collected. Sample distribution plots for some states with incomplete entries for 2015 are shown below.
  
<p align="center"><img src="imgs/eda/sample_dist_dates.png" ></p>
  
While there are 0 and negative values for the hourly entries, we assume that the sensors for each station are properly calibrated and leave those values untouched as these values may be intentional per station. We also assume that while stations may have different sensors, the traffic volume data entries are normalized to be of the same unit in the dataset.

#### 3.1.2 Temporal

To understand the general behavior of the data, data points are initially aggregated for analysis. If we were to plot the entire traffic data according to states and/or stations, we wouldn't be able to visually see the trends due to the amount of lines in the graph. In this case, a dataframe was retrieved by grouping the traffic data points by date (to retrieve 365 points), aggregating the traffic volume by collecting the total daily traffic volume, and transforming the data to retrieve the hourly entries.

- **Day of Month**
  
    Since we retrieved the hourly entries, we can compare the behavior across days in a month. The following plot shows a comparison of hourly aggregated traffic volume for different days in January 2015. The lines in this plot correspond to data from a specific day. Upon checking other months, it can be seen that visually there seems to be some patterns depending on the day. We move onto other temporal features to confirm our initial assumptions regarding the data.

<p align="center"><img src="imgs/eda/1.4.2.1.png" ></p>
  
- **Day of Week**
   
  Since the day of week values in the dataset are encoded numerically, we determine the matches during EDA to supplement the day names for graphs. From the plot below we can see that the traffic volume for weekends (Sunday and Saturday) are lower compared to their weekday counterparts. Additionally, there seems to be a slightly higher volume during Friday. This may be attributed to more casual plans occurring during Fridays as it signals the end of the weekday.
  
<p align="center"><img src="imgs/eda/1.4.3.1.png" ></p>

- **Day of Week and Hour of Day**
  
   We can further check the behavior of the traffic volume per hour during the day of week. We can see here that there is a significantly lower traffic volume during early mornings during the weekend. This may be attributed to activities such as schools and regular office hours only occuring during the weekdays, thus lowering the traffic volume during weekends.
  
<p align="center"><img src="imgs/eda/1.4.3.2.png" ></p>

   During different parts of the day, the trends for the traffic volume differs e.g. for hours during midnight to early morning (0-5AM), it can be seen that the traffic is low since most human activities such as regular office hours and school occur during morning to afternoon from Monday to Friday. This can be further verified by seeing the spike in traffic volume around midmornings (7-9AM) during weekdays wherein public transportation such as buses/taxis and private vehicles are being used to go to [schools](https://www.ciee.org/typical-day-school), [business establishments, offices](https://htir.com/articles/business-hours.php), and others. After stable traffic volumes during early afternoon (11AM-3PM), there are sudden spikes as people most likely return home after their time outside and slowly winding down further as it goes on to the night. 
  
<p align="center"><img src="imgs/anims/weekday-weekend.gif" ></p>
  
   Our initial assumptions regarding the temporal behavior of the data seems to match the general behavior of the data visually during aggregation and from articles regarding regular American working hours. To make it more visually apparent, we also show the average traffic volume per hour for weekday and weekend comparison from the animation above.

- **Seasonal Decomposition and Stationarity**
  
  Since we previously aggregated traffic volume daily, we can check the behavior and trend of the data through seasonal decomposition. Seasonal decomposition was also applied towards hourly entries during EDA but for this summary, trends for daily entries with 365 total data points (daily entries) are shown below. The model was set with a period of 7 to indicate a weekly frequency and matches with our assumptions regardingly the weekly trend of the data across the entire year.
  
<p align="center"><img src="imgs/eda/1.4.4.3.png" ></p>

  
   Statistical tests were also applied and it was seen that the p-value of the hourly traffic volume time series data has a low p-value which indicates it being stationary and not needing further pre-processing. However it is noted that the daily time series data for the traffic volume is relatively high so forecasting for daily traffic volume may need pre-processing to adjust these values (e.g. via log).
  
#### 3.1.3 Spatial
  
- **Incorrect Latitude and Longitude values**
  
  While checking the traffic stations, it was seen that there were some entries with common patterns of incorrect longitude and latitude data. This was verified by collecting external data by matching the FIPS state codes to their approximate longitude and latitude.

  The following plots show the incorrect longitude and latitude values for Delaware (FIPS state code 10) and South Dakota (FIP state 46). 
  
<p align="center"><img src="imgs/eda/10_map_before.png" ><br/>
  <sub>Portion of station plots across a map for FIPS state code 10 (Delaware)</sub></p>

<p align="center"><img src="imgs/eda/46_map_before.png" ><br/>
  <sub>Portion of station plots across a map for FIPS state code 46 (South Dakota)</sub></p>
 
   Based on the pattern seen in the data, it showed that there were other stations with the wrong tens value, occasionally having values of around 1, 900, 9, and others. To fix this, thresholding was applied to adjust the values within threshold limits. Afterwards, it can be shown that the initial assumption regarding the incorrect station locations are correct and can be validated from the plots below.

<p align="center"><img src="imgs/eda/10_map_after.png" ><br/>
  <sub>Portion of station plots across a map for FIPS state code 10 (Delaware) after processing</sub></p>
<p align="center"><img src="imgs/eda/46_map_after.png" ><br/>
  <sub>Portion of station plots across a map for FIPS state code 46 (South Dakota) after processing</sub></p>
  
   However, there are still misplaced stations which cannot be corrected through simple thresholding. These stations may be set aside for future exploration and automated retrieval of these anomalous stations may be retrieved by comparing the longitude and latitude values to the reference given under *fips_latlong.csv*.
  
- **Correlation between station count and traffic**
  
   Since the analysis so far has only been for aggregated total daily traffic volume, there may be a bias concerning the amount of station IDs present in a given state. To reduce this, the traffic data was aggregated per state and the average daily traffic volume across stations per state was collected. The data still seems to be correlated based on the correlation coefficient computed during EDA and the accompanying pairplot below.
  
<p align="center"><img src="imgs/eda/station_count-daily_traffic_volume.png" ></p>
  
  Correlation was also explored between traffic volume data and coordinate values (latitude, longitude) and have no clear linear correlation and can be seen in section *1.5.3 Explore relation between average daily traffic volume and coordinate values* under the EDA notebook.

- **Traffic volume trends comparison for urban and rural areas**
  
  The highest total daily traffic volume was retrieved for the dataset and it was during May 31, 2015 in New York for station ID 003480 with a functional classification name of Urban: Collector. To see if the functional classification name has bearing on the traffic volume, we aggregate the traffic data by this column and retrieve the average total daily traffic volume. Upon checking the plots, it can be seen that compared to rural traffic volumes, urban areas typically have higher average traffic volume across all states. However, there are some values such as "Rural: Principal Arterial - Interstate" which has higher average daily traffic volume but is still much lower compared to it's urban counterpart "Urban: Principal Arterial - Interstate".
  
<p align="center"><img src="imgs/eda/1.5.4.1.png" ></p>
  
#### 3.1.4 Features for forecasting

Some of the features that were explored are the following:

* Historical traffic volume
    * determined by *traffic_volume_counted_after*
* Temporal features
    * Cyclical timestamps (expressed as sin & cos values)
        * Month of year
        * Day of month
        * Day of week
        * Hour of day
    * Part of day (0-5AM, 6-11AM, 12-5PM, 6-11PM)
    * Weekend vs. weekday
* Spatial features
    * longitude
    * latitude
    * fips state code
    * station_id
    * urban/rural from functional_classification_name
    * Additionally, neighboring stations may also be retrieved by sorting and retrieving the [distances between the longitude and latitude values](https://mypages.iit.edu/~maslanka/3Dcoordinates.pdf) of stations
* Traffic features - Can be disregarded if volume trends to be checked are for locations relative to the station (no need for lane/direction in this case)
    * lane of travel
    * direction of travel 

  
### 3.2 Forecasting PoC

For a forecasting PoC, several models such as XGBoost, LightGB, and FBProphet was explored. The main objective set is to predict T+1 to T+24 traffic volume for a given day (e.g. 24 hourly entries). XGBoost models were trained for 11 states with the highest amount of entries in the dataset with the following results.
  
|    | RMSE (Test) | Max Traffic   Volume (Test) | Mean Traffic   Volume (Test) | Traffic Volume   Standard Deviation(Test) | FIPS State Code | State Name  |
|----|-------------|-----------------------------|------------------------------|-------------------------------------------|-----------------|-------------|
| 0  | 814.343292  | 35606                       | 2589.144178                  | 3651.882857                               | 12              | FLORIDA     |
| 1  | 399.729373  | 17801                       | 1459.280962                  | 1785.368333                               | 51              | VIRGINIA    |
| 2  | 1807.944088 | 100095                      | 2827.452846                  | 3734.130332                               | 39              | OHIO        |
| 3  | 850.074584  | 55398                       | 1958.167863                  | 3135.525856                               | 13              | GEORGIA     |
| 4  | 370.427766  | 14132                       | 1131.936928                  | 1563.80398                                | 55              | WISCONSIN   |
| 5  | 783.391322  | 21754                       | 2146.187504                  | 2997.321082                               | 53              | WASHINGTON  |
| 6  | 215.129808  | 11241                       | 622.384583                   | 1074.048508                               | 16              | IDAHO       |
| 7  | 2490.213012 | 105893                      | 1371.468579                  | 4295.141007                               | 36              | NEW   YORK  |
| 8  | 623.811068  | 22308                       | 1555.004114                  | 2568.41778                                | 40              | OKLAHOMA    |
| 9  | 464.095366  | 17396                       | 1324.281701                  | 1820.947934                               | 28              | MISSISSIPPI |
| 10 | 428.878986  | 16690                       | 1095.755869                  | 1864.26651                                | 29              | MISSOURI    |
  
Relative to the maximum, mean, and standard deviation values of the traffic volume, the results provide a pretty good baseline given the general parameters set for the models. To parallelize experimentation, the notebook *4. Experimentation with FLAML* was run in Colab. However, forecasting models such as FBProphet provided resulted in high RMSE and generally unreliable forecasts.
  
### 3.3 Recommendations

- Explore more complex models
- Add more features to the modeling
- Note adjacency between stations
- Perform clustering across the stations to determine anomalous values for the coordinate entries per station
- Utilize models to give business insight such as placing advertisements or opening establishments when there are high data traffic
- Also possible to model user behavior such as UE movement in telecommunications
