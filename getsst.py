# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 14:02:40 2017
Simple version of Sat SST plot with one panel
@author: huimin
Modifications by JiM in June 2019 to work on laptop at home
Modifications by JiM in mid-June 2020 to update both the URL, add netCDF4 method, cont_lev, and miniboat overlay
Modifications by JiM in late-June 2020 to add another sat image option
"""

import datetime as dt
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import netCDF4
import pandas as pd
import numpy as np
from numpy import ma
import time
#NOTE:  JiM NEEDED THE FOLLOWING LINE TO POINT TO his PROJ LIBRARY
import os,imageio
import glob
os.environ['PROJ_LIB'] = 'c:\\Users\\Joann\\anaconda3\\pkgs\\proj4-5.2.0-ha925a31_1\\Library\share'
from mpl_toolkits.basemap import Basemap
import warnings
warnings.filterwarnings("ignore") # JiM added Sep 2020 to supopress the "matplotlibDeprecationWarning"

#HARDCODES
sat_option='MARACOOS' #or 'UDEL', the two options for imagery available in mid-2020
datetime_wanted=dt.datetime(2020,9,4,0,0,0)
ndays=7
png_dir='c:\\Users\\Joann\\Downloads\\getsst\\pngs\\'
area='GBANK' # geographic box (see gbox function below)
cont_lev=[14.,24.,1.0]# min, max, and interval in either degC or degF of temp contours wanted
agg="3" # number of days of satellite image aggragation done by UDEL
cluster='wnerr_2020_1' # batch of drifter
gif_name=cluster+'_'+str(ndays)+'_'+agg+'_obs.gif'
#cluster='ep_2020_1' #leave blank if none
#ID=206430702 # drifter ID to overlay
ID=203400681
plot_model_tracks='no' # JiM added sep 2020 otherwise 'yes' plots Wilkin's model tracks


#FUNCTIONS
def make_gif(gif_name,png_dir,start_time=False,end_time=False,frame_length = 2,end_pause = 4 ):
    '''use images to make the gif
    frame_length: seconds between frames
    end_pause: seconds to stay on last frame
    the format of start_time and end time is string, for example: %Y-%m-%d(YYYY-MM-DD)'''
    
    if not os.path.exists(os.path.dirname(gif_name)):
        os.makedirs(os.path.dirname(gif_name))
    allfile_list = glob.glob(os.path.join(png_dir,'*.png')) # Get all the pngs in the current directory
    print(allfile_list)
    file_list=[]
    '''if start_time:    
        for file in allfile_list:
            if start_time<=os.path.basename(file).split('.')[0]<=end_time:
                file_list.append(file)
    else:'''
    file_list=allfile_list
    #list.sort(file_list, key=lambda x: x.split('/')[-1].split('t')[0]) # Sort the images by time, this may need to be tweaked for your use case
    images=[]
    # loop through files, join them to image array, and write to GIF called 'wind_turbine_dist.gif'
    for ii in range(0,len(file_list)):       
        file_path = os.path.join(png_dir, file_list[ii])
        if ii==len(file_list)-1:
            for jj in range(0,int(end_pause/frame_length)):
                images.append(imageio.imread(file_path))
        else:
            images.append(imageio.imread(file_path))
    # the duration is the time spent on each image (1/duration is frame rate)
    imageio.mimsave(gif_name, images,'GIF',duration=frame_length)

def getgbox(area):
  # gets geographic box based on area
  if area=='SNE':
    gbox=[-71.,-66.,39.,42.] # for SNE
  elif area=='OOI':
    gbox=[-72.,-69.5,39.5,41.5] # for OOI
  elif area=='GBANK':
    gbox=[-70.5,-66.,40.5,42.5] # for GBANK
  elif area=='GS':           
    gbox=[-71.,-63.,38.,42.5] # for Gulf Stream
  elif area=='NorthShore':
    gbox=[-71.,-69.5,41.5,43.] # for north shore
  elif area=='WNERR':
    gbox=[-71.,-69.,41.0,44.] # for WNERR deployment
  elif area=='DESPASEATO':
    gbox=[-71.,-69.5,42.6,43.25] # for miniboat Despaseato deployment
  elif area=='CCBAY':
    gbox=[-70.75,-69.8,41.5,42.23] # CCBAY
  elif area=='inside_CCBAY':
    gbox=[-70.75,-70.,41.7,42.23] # inside_CCBAY
  elif area=='NEC':
    gbox=[-69.,-64.,39.,43.5] # NE Channel
  elif area=='NE':
    gbox=[-76.,-66.,35.,44.5] # NE Shelf 
  return gbox

def getsst(m,datetime_wanted,gbox,sat_option):
    # gets and contours satellite SST
    second=time.mktime(datetime_wanted.timetuple())
    if sat_option=='UDEL':
        #url1='http://basin.ceoe.udel.edu/thredds/dodsC/Aqua3DayAggregate.nc' # new address found in Nov 2017
        url1='http://thredds.demac.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc'
        dataset=Dataset(url1)
        #times=list(nc.variables['time']) # this took way too much time
        times=ma.getdata(dataset.variables['time'])
        print('finding the nearest image index over times')
        index_second=int(round(np.interp(second,times,range(len(times)))))# finds the closest time index
        url='http://thredds.demac.udel.edu/thredds/dodsC/Aqua'+agg+'DayAggregate.nc?lat[0:1:4499],lon[0:1:4999],'+'sst['+str(index_second)+':1:'+str(index_second)+'][0:1:4499][0:1:4999]'+',time['+str(index_second)+':1:'+str(index_second)+']'
        dataset=Dataset(url)
        print('converting the masked array sst to an array') 
        sst=ma.getdata(list(dataset['sst']))
    else: #sat_option='MARACOOS'
        url1='http://tds.maracoos.org/thredds/dodsC/AVHRR'+agg+'.nc'
        dataset=Dataset(url1)
        times=ma.getdata(dataset.variables['time'])
        inds=int(round(np.interp(second,times,range(len(times)))))# finds the closest time index
        print("inds = "+str(inds))
        #url='http://tds.maracoos.org/thredds/dodsC/AVHRR7.nc?lon[0:1:4499],lat[0:1:3660],mcsst['+str(inds)+':1:'+str(inds)+'][0:1:4499][0:1:3660],time['+str(inds)+':1:'+str(inds)+']'
        url='http://tds.maracoos.org/thredds/dodsC/AVHRR7.nc?lon[0:1:4499],lat[0:1:3660],time['+str(inds)+':1:'+str(inds)+'],mcsst['+str(inds)+':1:'+str(inds)+'][0:1:3660][0:1:4499]'
        dataset=Dataset(url)
        print('converting the masked array sst to an array') 
        sst=ma.getdata(list(dataset['mcsst']))
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
    sst_part=sst[0,index_lat1:index_lat2,index_lon1:index_lon2]#*1.8+32
    print('got the subsampled sst')
    sst_part[(sst_part==-999)]=np.NaN# if sst_part=-999, convert to NaN
    if cont_lev[0]>30: # use degF
        sst_part=sst_part*1.8+32 # conver to degF
        labelT='deg F'
    else:
        labelT='deg C'
    print('temp range is '+str(np.nanmin(sst_part))+' to '+str(np.nanmax(sst_part))+' deg')
    #X,Y=np.meshgrid(lon[index_lon1:index_lon2],lat[index_lat1:index_lat2])
    X,Y=m.makegrid(len(lon[index_lon1:index_lon2]),len(lat[index_lat1:index_lat2]))#lon[index_lon1:index_lon2],lat[index_lat1:index_lat2])
    print('ready to contour')
    X,Y=m(X,Y)
    cmap = plt.cm.jet
    m.contourf(X,Y,sst_part,np.arange(cont_lev[0],cont_lev[1],cont_lev[2]),cmap=cmap,zorder=0)
    cb=plt.colorbar(cmap=cmap)
    cb.set_ticks(np.linspace(cont_lev[0],cont_lev[1],int(cont_lev[1]-cont_lev[0])+1))#/(cont_lev[2]*2.))))
    cb.set_label(labelT)

#MAINCODE -- MAKE BASEMAP and overlay tracks
gbox=getgbox(area) # uses the getgbox function to define lat/lon boundary
latsize=[gbox[2],gbox[3]]
lonsize=[gbox[0],gbox[1]]
tick_int=gbox[3]-gbox[2] # allow for 3-4 tick axis label intervals
if tick_int>=1:
    tick_int=int(tick_int/2.)   # make the tick_interval integer increments
if tick_int<1:
    tick_int=.5
for jj in range(-1,ndays-1):
 datetime_wanted=datetime_wanted+dt.timedelta(days=1)
 fig,ax=plt.subplots()
 m = Basemap(projection='merc',llcrnrlat=min(latsize),urcrnrlat=max(latsize),\
            llcrnrlon=min(lonsize),urcrnrlon=max(lonsize),resolution='i')
 m.fillcontinents(color='gray')
 #GET SST & PLOT
 getsst(m,datetime_wanted,gbox,sat_option)
 #GET TRACK & PLOT
 if len(cluster)!=0:
  if cluster[0:2]=='ep': # case of educational passages miniboats
    df=pd.read_csv('http://nefsc.noaa.gov/drifter/drift_'+str(ID)+'_sensor.csv')
    df=df[0:24*3] # end it 3 days in
    #df=df[df['id']==ID]
    xx=df.yearday.values #bad header makes  lon yearday and lat lon
    yy=df.lon.values
    x,y=m(xx,yy)
    m.plot(x,y,'m-')
    for k in np.arange(5,len(xx),5):
        if cont_lev[0]>30:
            t=df['mean_sst'][k]*1.8+32 # actually getting mean_sst
        else:
            t=df['mean_sst'][k]
        ax.annotate('%.1f' % t,(x[k],y[k]),color='k',fontweight='bold',fontsize=12,zorder=10)#xytext=(-500,500),textcoords='offset points'
  else: # case of multiple drifters
    df=pd.read_csv('http://nefsc.noaa.gov/drifter/drift_'+cluster+'.csv')
    ids=np.unique(df['ID'])
    for k in ids:
        df1=df[df['ID']==k]
        df1=df1[df1['DAY']==datetime_wanted.day]
        df1=df1[df1['MTH']==datetime_wanted.month]# JiM added sep 2020
        x,y=m(df1['LON'].values,df1['LAT'].values)
        m.plot(x,y,'k')
    if plot_model_tracks=='yes':    
        #get the forecast drifter data where I had to change the number of time steps from 31 to 29 on 7/10 vs 7/11/2020
        #url='http://tds.marine.rutgers.edu/thredds/dodsC/floats/doppio_flt_202007'+str(datetime_wanted.day)+'.nc?ocean_time[0:1:312],lon[0:1:312][0:1:29],lat[0:1:312][0:1:29],depth[0:1:312][0:1:29],temp[0:1:312][0:1:29],salt[0:1:312][0:1:29]'
        url='http://tds.marine.rutgers.edu/thredds/dodsC/floats/doppio_flt_2020'+str(datetime_wanted.month).zfill(2)+str(datetime_wanted.day)+'.nc?lon,lat'
        nc=netCDF4.Dataset(url) # where we have imported Datset from netCDF4
        dlons=nc.variables['lon'][:].filled(np.nan)# replaces the masked values with nan7
        dlats=nc.variables['lat'][:].filled(np.nan)
        sh=np.shape(dlons) # get the shape to see how many drifters there are
        for k in range(sh[1]): #  loop through all the drifters
            x,y=m(np.ma.getdata(dlons[:,k])[:],np.ma.getdata(dlats[:,k])[:])
            m.plot(x,y,'r')
    
 m.drawparallels(np.arange(min(latsize),max(latsize)+1,tick_int),labels=[1,0,0,0])
 m.drawmeridians(np.arange(min(lonsize),max(lonsize)+1,tick_int),labels=[0,0,0,1])
 #m.drawcoastlines()
 m.drawmapboundary()
 #plt.title(str(datetime_wanted.strftime("%d-%b-%Y"))+' '+agg+'-day '+sat_option+' composite')#+cluster)
 plt.title(str(datetime_wanted.strftime("    %d-%b-%Y"))+' composite')#+cluster)
 plt.savefig(png_dir+sat_option+'_'+area+'_'+datetime_wanted.strftime('%Y-%m-%d')+'_'+agg+'.png')
 plt.show()  
gif_name=png_dir+gif_name
make_gif(gif_name,png_dir,start_time=datetime_wanted-dt.timedelta(days=ndays),end_time=datetime_wanted)
