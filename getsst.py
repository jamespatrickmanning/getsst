# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 14:02:40 2017
Simple version of Sat SST plot with one panel
@author: huimin
Modifications by JiM in June 2019 to work on laptop at home
Modifications by JiM in June 2020 to update both the URL, add netCDF4 method, add cont_lev
"""

import sys
import datetime as dt
import matplotlib.pyplot as plt
#from pydap.client import open_url
from netCDF4 import Dataset
import numpy as np
from numpy import ma
import time
import os
#NOTE:  JiM NEEDED THE FOLLOWING LINE TO POINT TO PROJ LIBRARY
os.environ['PROJ_LIB'] = 'c:\\Users\\Joann\\anaconda3\\pkgs\\proj4-5.2.0-ha925a31_1\\Library\share'
from mpl_toolkits.basemap import Basemap

#HARDCODES
#datetime_wanted=dt.datetime(2017,11,18,8,0,0,0)
datetime_wanted=dt.datetime(2020,6,16,8,0,0,0)
area='WNERR'
#cont_lev=[16,23,1]# min, max, and interval of temp contours wanted
cont_lev=[60,66,1]
agg="1"
def getgbox(area):
  # gets geographic box based on area
  if area=='SNE':
    gbox=[-71.,-66.,39.,42.] # for SNE
  elif area=='OOI':
    gbox=[-72.,-69.5,39.5,41.5] # for OOI
  elif area=='GBANK':
    gbox=[-70.,-64.,39.,42.] # for GBANK
  elif area=='GS':           
    gbox=[-71.,-63.,38.,42.5] # for Gulf Stream
  elif area=='NorthShore':
    gbox=[-71.,-69.5,41.5,43.] # for north shore
  elif area=='WNERR':
    gbox=[-71.,-70.,42.,43.] # for WNERR deployment
  elif area=='CCBAY':
    gbox=[-70.75,-69.8,41.5,42.23] # CCBAY
  elif area=='inside_CCBAY':
    gbox=[-70.75,-70.,41.7,42.23] # inside_CCBAY
  elif area=='NEC':
    gbox=[-69.,-64.,39.,43.5] # NE Channel
  elif area=='NE':
    gbox=[-76.,-66.,35.,44.5] # NE Shelf 
  return gbox
def getsst(datetime_wanted,gbox):
    
    second=time.mktime(datetime_wanted.timetuple())
    #url1='http://basin.ceoe.udel.edu/thredds/dodsC/Aqua3DayAggregate.nc' # new address found in Nov 2017
    #url1='http://basin.ceoe.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc'
    url1='http://thredds.demac.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc'
    #dataset1=open_url(url1)
    nc=Dataset(url1)
    #times=list(dataset1['time'])
    #times=list(nc.variables['time'])
    times=ma.getdata(nc.variables['time'])
    print('finding the nearest image index over times')
    index_second=int(round(np.interp(second,times,range(len(times)))))# finds the closest time index
    #url='http://basin.ceoe.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc?lat[0:1:4499],lon[0:1:4999],'+'sst['+str(index_second)+':1:'+str(index_second)+'][0:1:4499][0:1:4999]'+',time['+str(index_second)+':1:'+str(index_second)+']'
    url='http://thredds.demac.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc?lat[0:1:4499],lon[0:1:4999],'+'sst['+str(index_second)+':1:'+str(index_second)+'][0:1:4499][0:1:4999]'+',time['+str(index_second)+':1:'+str(index_second)+']'
    
    try:
        print(url)
        #dataset=open_url(url)
        dataset=Dataset(url)
    except:
        print("please check your url!")
        sys.exit(0)
    print('converting the masked array sst to an array') 
    sst=ma.getdata(list(dataset['sst']))
    print('got the sst')
    lat=ma.getdata(dataset['lat'][:])
    lon=ma.getdata(dataset['lon'][:])
    print('got the lat & lon')
     # find the index for the gbox
    index_lon1=int(round(np.interp(gbox[0],lon,range(len(lon)))))
    index_lon2=int(round(np.interp(gbox[1],lon,range(len(lon)))))
    index_lat1=int(round(np.interp(gbox[2],lat,range(len(lat)))))
    index_lat2=int(round(np.interp(gbox[3],lat,range(len(lat)))))
    # get part of the sst
    #sst_part=sst[index_second,index_lat1:index_lat2,index_lon1:index_lon2]
    sst_part=sst[0,index_lat1:index_lat2,index_lon1:index_lon2]#*1.8+32
    print('got the subsampled sst')
    sst_part[(sst_part==-999)]=np.NaN# if sst_part=-999, convert to NaN
    sst_part=sst_part*1.8+32 # conver to degF
    print('temp range is '+str(np.nanmin(sst_part))+' to '+str(np.nanmax(sst_part))+' degF')
    X,Y=np.meshgrid(lon[index_lon1:index_lon2],lat[index_lat1:index_lat2])
    print('ready to contour')
    cmap = plt.cm.jet
    plt.contourf(X,Y,sst_part,np.arange(cont_lev[0],cont_lev[1],cont_lev[2]),cmap=cmap)
    cb=plt.colorbar(cmap=cmap)
    cb.set_ticks(np.linspace(cont_lev[0],cont_lev[1],int(cont_lev[1]-cont_lev[0])+1))#/(cont_lev[2]*2.))))
    cb.set_label('Degree C')
#MAKE BASEMAP
gbox=getgbox(area) # uses the getgbox function to define lat/lon boundary
latsize=[gbox[2],gbox[3]]
lonsize=[gbox[0],gbox[1]]
tick_int=(gbox[3]-gbox[2])/4. # allow for 3-4 tick axis label intervals
if tick_int>2:
    tick_int=int(tick_int)   # make the tick_interval integer increments
fig=plt.figure()
m = Basemap(projection='cyl',llcrnrlat=min(latsize),urcrnrlat=max(latsize),\
            llcrnrlon=min(lonsize),urcrnrlon=max(lonsize),resolution='i')
m.drawparallels(np.arange(min(latsize),max(latsize)+1,tick_int),labels=[1,0,0,0])
m.drawmeridians(np.arange(min(lonsize),max(lonsize)+1,tick_int),labels=[0,0,0,1])
#m.drawcoastlines()
m.fillcontinents(color='gray')
m.drawmapboundary()
#GET SST & PLOT
getsst(datetime_wanted,gbox)

plt.title(str(datetime_wanted.strftime("%d-%b-%Y"))+' '+agg+' day UDEL composite')
plt.savefig(area+'_'+datetime_wanted.strftime('%Y-%m-%d %H:%M')+'_'+agg+'.png')
plt.show()

