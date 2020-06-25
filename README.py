Readme for "getsst"

JiM's adaptation of Huimin's code from 2017

Note: In order to make this run on my old Toshiba Windows Laptop during 2020 Pandemic, I first needed to:

    -added lots of print statements to be Python 3 compatible as "print()" to monitor progress
    -changed the URL from basin to thredds.demac 
    -change the "pydap" method to the more up-to-date "netCDF4"
    -convert the masked sst array to a regular array
    -posted on Github for Jack Polentes to try
    
This code makes as it stands makes a single png for user supplied date and time.

Hardcodes include:
    - number of days to aggregate images (done by UDEL folks)
    - cont_lev to specify the min, max, and int of temp contours in units of choice
    - cluster of drifter or miniboat tracks to overlay
    




