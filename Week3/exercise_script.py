import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file('data_files/Counties.shp') # load the counties shapefile
counties.to_crs(epsg=32629, inplace=True) # transform to UTM projection

wards = gpd.read_file('data_files/NI_Wards.shp') # load the counties shapefile
wards.to_crs(epsg=32629, inplace=True) # transform to UTM projection

# your analysis goes here...
join = gpd.sjoin(counties, wards, how='inner', lsuffix='left', rsuffix='right') # perform the spatial join

# make print output look nicer
pop_sum_counties = join.groupby(['CountyName'], as_index=False)['Population'].sum() # summarise population per county
                                                                                      # output as GeoDataFrame

print('The population counts per county are as follows:\n',
      pop_sum_counties.to_string(columns=['CountyName', 'Population'], index=False))
# summarize the population by CountyName
      # display as string, only display county name and popultaion and hide other columns including index

# ---------------------------------------------------------------------------------------------------------------------
# What county has the highest population? What about the lowest?

cpopmax = pop_sum_counties['Population'].max() # calculate the maximum population value

cpopmin = pop_sum_counties['Population'].min() # calculate the minimum population value

cpmax = pop_sum_counties.loc[pop_sum_counties['Population'].idxmax()]['CountyName']
# find the county with the maximum population value

cpmin = pop_sum_counties.loc[pop_sum_counties['Population'].idxmin()]['CountyName']
# find the county with the minimum population value

print('Of all counties, {} has the highest population with {} residents'.format(cpmax, cpopmax))
# print statement adding county and value

print('Of all counties, {} has the lowest population with {} residents'.format(cpmin, cpopmin))
# print statement adding county and value


# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('sample_map.png', dpi=300, bbox_inches='tight')


# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Below are the extension exercises

# ---------------------------------------------------------------------------------------------------------------------
# Are there any wards that are located in more than one county? YES
# how many, and what is the total population of these wards

freq = join['Ward'].value_counts() # generate frequency each ward value appears
items = freq[freq>1].index # get index of wards that appear more than once
split_wards = join[join['Ward'].isin(items)] # create new DataFrame with only wards that appear more than once
                                             # (based on their index)
num_split_wards = len(split_wards.Ward.unique()) # get number of unique wards from table of split wards
print('There are {} wards that are split between county boundaries'.format(num_split_wards)) # print statement

split_wards_no_dup = split_wards.drop_duplicates(subset = ['Ward']) # remove rows where ward appears more than once so
                                                       # that each ward only appears in one row in DataFrame

split_wards_sum = split_wards_no_dup['Population'].sum() # get sum of populations (each row/ward added together)
print('The total population of the split wards is {}'.format(split_wards_sum)) # print statement


# ---------------------------------------------------------------------------------------------------------------------
# What ward has the highest population? What about the lowest?

popmax = wards['Population'].max() # calculate the maximum population value

popmin = wards['Population'].min() # calculate the minimum population value

wpmax = wards.loc[wards['Population'].idxmax()]['Ward'] # find the ward with the maximum population value

wpmin = wards.loc[wards['Population'].idxmin()]['Ward'] # find the ward with the minimum population value

print('Of all wards, {} has the highest population with {} residents'.format(wpmax, popmax)) # print statement
                                                                                             # adding ward and value

print('Of all wards, {} has the lowest population with {} residents'.format(wpmin, popmin)) # print statement
                                                                                            # adding ward and value


# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# Repeat the exercise above using the script but this time use the population density
# (in number of residents per square km)

for ind, row in wards.iterrows():  # iterate over each row in the GeoDataFrame
    wards.loc[ind, 'Areakm2'] = row['geometry'].area/1000000  # assign the row's geometry area to a new column Areakm2

for ind, row in wards.iterrows():  # iterate over each row in the GeoDataFrame
    wards.loc[ind, 'PopDensity'] = row['Population']/row['Areakm2']  # assign the population density as
                                                                     # population/areakm2 to a new column PopDensity

joinpd = gpd.sjoin(counties, wards, how='inner', lsuffix='left', rsuffix='right')
                                                                     # new spatial join for populaion density

counties_pop_sum = joinpd.groupby(['CountyName'], as_index=False)['Population'].sum() # summarise population per county
                                                                                      # output as GeoDataFrame
counties_area_sum = joinpd.groupby(['CountyName'], as_index=False)['Areakm2'].sum() # summarise area per county
                                                                                    # output as GeoDataFrame
counties_pd = counties_pop_sum.merge(counties_area_sum, on='CountyName') # merge population and area values per county

for ind, row in counties_pd.iterrows():  # iterate over each row in the GeoDataFrame
    counties_pd.loc[ind, 'PopDensity'] = row['Population']/row['Areakm2']  # assign the population density as
                                                                     # population/areakm2 to a new column PopDensity

counties_pd.PopDensity = counties_pd.PopDensity.round(2) # round population densities to 2 decimal places

print('The population densities per county are as follows:\n',
      counties_pd.to_string(columns=['CountyName', 'PopDensity'], index=False))
# summarize the population density by CountyName
    # display as string, only display county name and popultaion density and hide other columns including index

# ---------------------------------------------------------------------------------------------------------------------
# What county has the highest population density? What about the lowest?

cpopmaxpd = counties_pd['PopDensity'].max() # calculate the maximum population density value

cpopminpd = counties_pd['PopDensity'].min() # calculate the minimum population density value

cpmaxpd = counties_pd.loc[counties_pd['PopDensity'].idxmax()]['CountyName']
# find the county with the maximum population density value

cpminpd = counties_pd.loc[counties_pd['PopDensity'].idxmin()]['CountyName']
# find the county with the minimum population density value

print('Of all counties, {} has the highest population density with {} residents per square km'.format
      (cpmaxpd, cpopmaxpd)) # print statement adding county and value

print('Of all counties, {} has the lowest population density with {} residents per square km'.format
      (cpminpd, cpopminpd)) # print statement adding county and value


# ---------------------------------------------------------------------------------------------------------------------
# Are there any wards that are located in more than one county? YES
# how many, and what is the total population density of these wards

freq = joinpd['Ward'].value_counts() # generate frequency each ward value appears
items = freq[freq>1].index # get index of wards that appear more than once
split_wardspd = joinpd[joinpd['Ward'].isin(items)] # create new GeoDataFrame with only wards that appear more than once
                                                 # (based on their index)
num_split_wardspd = len(split_wardspd.Ward.unique()) # get number of unique wards from table of split wards
print('There are {} wards that are split between county boundaries'.format(num_split_wardspd)) # print statement

split_wards_no_duppd = split_wardspd.drop_duplicates(subset = ['Ward']) # remove rows where ward appears more than once
                                                            # so that each ward only appears in one row in GeoDataFrame

split_wards_sum_pop = split_wards_no_duppd['Population'].sum() # get sum of population (each row/ward added together)
split_wards_sum_area = split_wards_no_duppd['Areakm2'].sum() # get sum of area (each row/ward added together)
split_wards_sum_pd = split_wards_sum_pop/split_wards_sum_area # calculate population density of split wards

print('The total population density of the split wards is {:.2f}'.format(split_wards_sum_pd)) # print statement
                                                                                  # display to 2 decimal places


# ---------------------------------------------------------------------------------------------------------------------
# What ward has the highest population density? What about the lowest?

popmaxpd = wards['PopDensity'].max() # calculate the maximum population density

popminpd = wards['PopDensity'].min() # calculate the minimum population density

wdmaxpd = wards.loc[wards['PopDensity'].idxmax()]['Ward'] # find the ward with the maximum population density

wdminpd = wards.loc[wards['PopDensity'].idxmin()]['Ward'] # find the ward with the minimum population density

print('Of all wards, {} has the highest population density with {:.2f} residents per square km'.format(wdmaxpd, popmaxpd))
# print statement adding ward and value

print('Of all wards, {} has the lowest population density with {:.2f} residents per square km'.format(wdminpd, popminpd))
# print statement adding ward and value

# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='PopDensity', ax=ax, vmin=0, vmax=10000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Population Density'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('sample_map_pd.png', dpi=300, bbox_inches='tight')