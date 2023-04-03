import numpy as np
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches


def percentile_stretch(img, pmin=0., pmax=100.):
    '''
    Contrast stretch raster image using percentile

    Image is tested to ensure arguments are met
    Percentile values are found
    Image is stretched to 0,1
    Anything above or below max and min values are set to new max and min values

    input: image to display, pmin, pmax

    args: pmin must be larger than 0 and pmax must be smaller than 100
          pmin must be smaller than pmax
          image must be 2 dimensional

    defaults: defualt pmin of 0 and default pmax of 100

    returns: stretched image
    '''
    # here, we make sure that pmin < pmax, and that they are between 0, 100
    if not 0 <= pmin < pmax <= 100:
        raise ValueError('0 <= pmin < pmax <= 100')
    # here, we make sure that the image is only 2-dimensional
    if not img.ndim == 2:
        raise ValueError('Image can only have two dimensions (row, column)')

    minval = np.percentile(img, pmin)
    maxval = np.percentile(img, pmax)

    stretched = (img - minval) / (maxval - minval)  # stretch the image to 0, 1
    stretched[img < minval] = 0  # set anything less than minval to the new minimum, 0.
    stretched[img > maxval] = 1  # set anything greater than maxval to the new maximum, 1.

    return stretched


def img_display(img, ax, bands, stretch_args=None, **imshow_args):
    '''
    Displays a raster image

    Copy image and cast as floating-point image
    Percentile stretch each image bands - if no stretch arguments are provided use defaults of percentile_stretch function
                                          if stretch arguments are given unpack these and use
    Image is then transposed and scaled before displaying using image arguments

    input: image to display, ax, bands of image, stretch arguments, image arguments

    defaults: default stretch arguments as None

    returns: handle and ax
    '''
    dispimg = img.copy().astype(np.float32)  # make a copy of the original image,
    # but be sure to cast it as a floating-point image, rather than an integer

    for b in range(img.shape[0]):  # loop over each band, stretching using percentile_stretch()
        if stretch_args is None:  # if stretch_args is None, use the default values for percentile_stretch
            dispimg[b] = percentile_stretch(img[b])
        else:
            dispimg[b] = percentile_stretch(img[b], **stretch_args)

    # next, we transpose the image to re-order the indices
    dispimg = dispimg.transpose([1, 2, 0])

    # finally, we display the image
    handle = ax.imshow(dispimg[:, :, bands], **imshow_args)

    return handle, ax


# ------------------------------------------------------------------------
# note - rasterio's open() function works in much the same way as python's - once we open a file,
# we have to make sure to close it. One easy way to do this in a script is by using the with statement shown
# below - once we get to the end of this statement, the file is closed.
with rio.open('data_files/NI_Mosaic.tif') as dataset:
    img = dataset.read()
    xmin, ymin, xmax, ymax = dataset.bounds

# your code goes here!
# start by loading the outlines and point data to add to the map
counties = gpd.read_file('../Week2/data_files/Counties.shp')
towns = gpd.read_file('../Week2/data_files/Towns.shp')

myCRS = ccrs.UTM(29) # set myCRS

# ensure data files are myCRS
counties.to_crs(epsg=32629, inplace=True)
towns.to_crs(epsg=32629, inplace=True)

# next, create the figure and axis objects to add the map to
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS)) # create new figure axis

# now, add the satellite image to the map
my_stretch = {'pmin': 0.1, 'pmax': 99.9} # create stretch dict to use for image display

my_kwargs = {'extent': [xmin, xmax, ymin, ymax], # create kwargs dict to use for image display
             'transform': myCRS}

h, ax = img_display(img, ax, [2, 1, 0], stretch_args=my_stretch, **my_kwargs) # display satellite image

# next, add the county outlines to the map
county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none') # create county outlines

ax.add_feature(county_outlines) # add county outlines to map
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')] # create county handles for legend

# then, add the town and city points to the map, but separately
# Use intermediate variable and .loc to select only towns and only cities to then add to ax.plot()
just_towns = towns.loc[towns['STATUS'] == 'Town']
town_handle = ax.plot(just_towns.geometry.x, just_towns.geometry.y, 's', color='c', ms=6, transform=myCRS)

just_cities = towns.loc[towns['STATUS'] == 'City']
city_handle = ax.plot(just_cities.geometry.x, just_cities.geometry.y, 'D', color='y', ms=6, transform=myCRS)

# finally, try to add a transparent overlay to the map
# note: one way you could do this is to combine the individual county shapes into a single shape, then
# use a geometric operation, such as a symmetric difference, to create a hole in a rectangle.
# then, you can add the output of the symmetric difference operation to the map as a semi-transparent feature.

counties_union = unary_union(counties.geometry) # create NI outline by joining geometries of counties
map_frame = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]) # create polygon of map extent

map_overlay = ShapelyFeature(map_frame.symmetric_difference(counties_union), myCRS, facecolor='w', alpha=0.5)
ax.add_feature(map_overlay) # crete polygon of map extent polygon minus NI outline using symmetric difference,
                            # display as white background (partially transparent with alpha 0.5) and add to map

# last but not least, add gridlines to the map
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# add a legend
handles = county_handles + town_handle + city_handle
labels = ['County Boundaries', 'Towns', 'Cities']

ax.legend(handles, labels, title='Map Legend', title_fontsize=12,
                fontsize=11, loc='upper left', frameon=True, framealpha=1)

# and of course, save the map!
fig.savefig('imgs/example_map_mine.png', dpi=300, bbox_inches='tight')