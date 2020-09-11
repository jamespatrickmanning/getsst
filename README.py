Readme for "getsst"

JiM's adaptation of Huimin's code from 2017

Note: In order to make this run on my old Toshiba Windows Laptop during 2020 Pandemic, I first needed to:

    -added lots of print statements to be Python 3 compatible as "print()" to monitor progress
    -changed the URL from basin to thredds.demac 
    -change the "pydap" method to the more up-to-date "netCDF4"
    -convert the masked sst array to a regular array
    -first posted on Github for Jack Polentes to try and later pointed Kristen to it 
    
Other changes may ne need on your machine.

Makes gif animations from a set of png files.

Hardcodes include:
    - number of days to aggregate images (done by imagery folks)
    - choice of imagery source (UDEL and MARACOOS in mid-2020)
    - cont_lev to specify the min, max, and int of temp contours in units of choice
    - choice of "area" to focus on including for example "Cape Cod", "NorthSHore", etc which defines geographic box
    - cluster of drifter or miniboat tracks to overlay
    - specification of whether to "plot_model_drifters"  or not
    
Note: new section for "plot_model_drifters" was not working in Sep 2020
    




