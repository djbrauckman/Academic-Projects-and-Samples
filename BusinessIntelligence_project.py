# -*- coding: utf-8 -*-
"""G5_Final_Project_Assignment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/193A4eDHH_fdE-O164yE6co5XMqc1osL4

# Effects of Risk and Mitigation Factors on Frequency of Transportation Accidents

By: Bryan Loeffler, Jordan Gussett, Daniel Brauckman, and Ashley Ramnath

# Analysis of Data

# Data Cleaning
"""

import io
import pandas as pd
import requests as r
import geopy
from geopy.geocoders import Nominatim
import re
import matplotlib.pyplot as plt


#Update to source directory where your data files reside
path = '/path to source file/'

#Set file variables for reading, manipulation, and merging. As long as your
#file names match no modifications here are required.
file_1 = 'Weekly_Texas_Regular_Conventional_Retail_Gasoline_Prices.csv'
file_2 = 'Real-Time_Traffic_Incident_Reports.csv'
file_3 = 'Traffic_Cameras.csv'
file_4 = 'Monthly_Per_Capita_Consumption.csv'
file_out1 = 'gas_test.csv'
file_out2 = 'accid_test.csv'
file_out3 = 'cam_test.csv'
file_out4 = 'MPCC_test.csv'
file_out5 = 'merged_test.csv'
file_out6 = 'test_test.csv'
file_out7 = 'gas_merge.csv'
file_out8 = 'cam_merge.csv'
file_out9 = 'mpcc_merge.csv'


#Read datasets into dataframe variables
df_gas = pd.read_csv(path + file_1)
df_accid = pd.read_csv(path + file_2)
df_cam = pd.read_csv(path + file_3)
df_mpcc = pd.read_csv(path + file_4)

##############################################################################

# working with camera data
# Remove rows that lack a turn on date
df_cam.dropna(subset=['Turn on Date'], inplace=True)


# pull desired columns
cam_pull = ['Camera Status', 'Turn on Date', 'Location']
df_cam_pull = df_cam[cam_pull]

# purge irrelevant cam statuses
cam_status_purge = ['REMOVED','VOID','DESIRED']

for z in cam_status_purge:
    df_cam_pull = df_cam_pull[df_cam_pull['Camera Status'] != z]

# convert turn on date and extract month and year
df_cam_pull['Turn on Date'] = pd.to_datetime(df_cam_pull['Turn on Date'])
df_cam_pull['Month'] = df_cam_pull['Turn on Date'].dt.month
df_cam_pull['Year'] = df_cam_pull['Turn on Date'].dt.year

# each camera turned on gets a value of 1 in order to groupby the sum for each month
df_cam_pull['Camera Counter'] = 1

# group by month and year while adding the total amount of cameras turn on in those time frames
df_cam_pull = df_cam_pull.groupby(['Year', 'Month'])['Camera Counter'].sum().reset_index()

# for viewing
# df_cam.to_csv(path + file_out3, index=False)

##############################################################################

##############################################################################

# working with gas data

# assign the first column a title due to original file lacking one
df_gas = df_gas.rename(columns={'Unnamed: 0': 'Week of'})

# drop the first line of data which original file treated as a column name
df_gas.dropna(inplace=True)

# convert week of date and extract month and year
df_gas['Week of'] = pd.to_datetime(df_gas['Week of'])
df_gas['Month'] = df_gas['Week of'].dt.month
df_gas['Year'] = df_gas['Week of'].dt.year

# shortening the length of the column title
df_gas.rename(columns={'Weekly Texas Regular Conventional Retail Gasoline Prices Dollars per Gallon': 'Weekly Gas Prices'}, inplace=True)

# remove $ sign from values and convert to numeric values
df_gas['Weekly Gas Prices']= df_gas['Weekly Gas Prices'].str.replace('$', '')
df_gas['Weekly Gas Prices'] = pd.to_numeric(df_gas['Weekly Gas Prices'], errors='coerce')

# Group by year and month while averaging gas prices for said year and month combination
df_gas = df_gas.groupby(['Year', 'Month'])['Weekly Gas Prices'].mean().reset_index()

# for viewing
#df_gas.to_csv(path + file_out1, index=False)

##############################################################################


##############################################################################

# working with alcohol data

# pull desired columns
mpcc_pull = ['Year','Month','DistilledSpiritsTotalGallons','WineTotalGallonsEstimated',
             'BeerTotalGallons','AleTotalGallons']

# create df with desired columns
df_mpcc_pull = df_mpcc[mpcc_pull]

# filling in 0 values in the aletotalgallons column
mean_value = df_mpcc_pull[df_mpcc_pull['AleTotalGallons'] != 0]['AleTotalGallons'].mean()

df_mpcc_pull['AleTotalGallons'] = df_mpcc_pull['AleTotalGallons'].replace(0, mean_value)

# create a total column for all alcohol
df_mpcc_pull['TotalAlcohol'] = (df_mpcc_pull['DistilledSpiritsTotalGallons']+
                                df_mpcc_pull['WineTotalGallonsEstimated']+
                                df_mpcc_pull['BeerTotalGallons']+
                                df_mpcc_pull['AleTotalGallons'])

# for viewing
# df_mpcc_pull.to_csv(path + file_out4, index=False)

##############################################################################


##############################################################################

# working with vehicle accident data

# convert week of date and extract month and year
df_accid['Published Date'] = pd.to_datetime(df_accid['Published Date'])
df_accid['Month'] = df_accid['Published Date'].dt.month
df_accid['Year'] = df_accid['Published Date'].dt.year

# mainly to remove accidents most likely to not result in traffic cameras being installed. This can be skipped
accid_drop = ['BOAT ACCIDENT','LOOSE LIVESTOCK','STALLED VEHICLE',
              'TRFC HAZD/DEBRIS','zSTALLED VEHICLE']

#Loop through irrelevant incidents and remove
for y in accid_drop:
    df_accid = df_accid[df_accid['Issue Reported'] != y]

# each accident gets a value of 1 in order to groupby the sum for each month
df_accid['Accident Counter'] = 1

# group by year and month while adding up the total amount of accidents that occured each month
df_accid = df_accid.groupby(['Year', 'Month'])['Accident Counter'].sum().reset_index()


"""
Note - this will not work on large datasets without throttling or access to the API.
To run against a dataset you will need to break out records into smaller subsets (< 500 rows)


#Snippet to extract address, zip code from coordinate data

geolocator = Nominatim(user_agent='G5')

df_accid['full_address'] = df_accid.apply(lambda row: geolocator.reverse((row['Latitude'], row['Longitude'])).address, axis=1)

#Use regex to identify where zip codes start within the address
zip_code_pattern = r'\s7\d{4}\b'

#Find the zipcode and create a new column to isolate
df_accid['zipcode'] = df_accid['full_address'].apply(lambda x: re.search(zip_code_pattern, x).group(0) if re.search(zip_code_pattern, x) else None)
"""

# for viewing
# df_accid.to_csv(path + file_out2, index=False)
##############################################################################

"""# Data Merging"""

##############################################################################

# creation of the final merged document
df_merged = df_accid.merge(df_gas, how='inner', on=['Year', 'Month'])

df_merged = df_merged.merge(df_cam_pull, how='inner', on=['Year', 'Month'])

df_merged = df_merged.merge(df_mpcc_pull, how='inner', on=['Year', 'Month'])

# for viewing
# df_merged.to_csv(path + file_out5, index=False)

##############################################################################


"""
This was a failed section, in an attempt to see the correlation between
each variable compared to accidents. While the correlation is changes, it is
only a minor change when compared to the main merged file
"""

##############################################################################
'''
creating individual merges to see how data correlates with just one set
as opposed to all 3
'''
# df_merged_gas = df_accid.merge(df_gas, how='inner', on=['Year', 'Month'])
# df_merged_gas.to_csv(path + file_out7, index=False)

# df_merged_cam = df_accid.merge(df_cam_pull, how='inner', on=['Year', 'Month'])
# df_merged_cam.to_csv(path + file_out8, index=False)

# df_merged_mpcc = df_accid.merge(df_mpcc_pull, how='inner', on=['Year', 'Month'])

# df_merged_mpcc.to_csv(path + file_out9, index=False)
##############################################################################

"""# Visualization of Data"""

# correlation of all merged data
x = df_merged.corr()

# for viewing since not all columns will be shown during the .corr() command
x.to_csv(path + file_out6)

# creates an abomination of graphs
pd.plotting.scatter_matrix(df_merged)

# simple command to see a scatter plot for each category against accidents
df_merged.plot.scatter(x='Camera Counter', y='Accident Counter', title='Scatter Plot')
df_merged.plot.scatter(x='Weekly Gas Prices', y='Accident Counter', title='Scatter Plot')
df_merged.plot.scatter(x='TotalAlcohol', y='Accident Counter', title='Scatter Plot')

# histogram of the four major columns
pulled_columns = ['Accident Counter', 'Weekly Gas Prices', 'Camera Counter', 'TotalAlcohol']

df_merged_pulled= df_merged[pulled_columns]

df_merged_pulled.hist()