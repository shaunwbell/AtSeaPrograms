#!/usr/bin/env

"""
CTD_plot.py

Plot data from cruises

Currently
---------
ctd plots

Input - CruiseID

"""

#System Stack
import datetime
import os
import argparse


#Science Stack
import numpy as np
from netCDF4 import Dataset

#Visual Packages
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# User Stack
from io_utils import EcoFOCI_netCDF_read
from plots.profile_plot import CTDProfilePlot
from calc import EPIC2Datetime

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 8, 22)
__modified__ = datetime.datetime(2016, 8, 24)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Plots', 'Cruise', 'QC'



"""--------------------------------Plot Routines---------------------------------------"""

def twovar_minmax_plotbounds(var1,var2):
    """expects missing values to be np.nan"""
    if np.isnan(var1).all() and np.isnan(var2).all():
        min_bound = -1
        max_bound = 1
    elif np.isnan(var1).all() and not np.isnan(var2).all():
        min_bound = var2[~np.isnan(var2)].min()
        max_bound = var2[~np.isnan(var2)].max()
    elif np.isnan(var2).all() and not np.isnan(var1).all():
        min_bound = var1[~np.isnan(var1)].min()
        max_bound = var1[~np.isnan(var1)].max()
    else:
        min_bound = np.min((var1[~np.isnan(var1)].min(), var2[~np.isnan(var2)].min()))
        max_bound = np.max((var1[~np.isnan(var1)].max(), var2[~np.isnan(var2)].max()))
        
    return (min_bound, max_bound)
   

"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,help='full path to directory of processed nc files')
parser.add_argument('-TSvD','--TSvD', action="store_true",
               help='Temperature, Salinity, SigmaT vs depth')
parser.add_argument('-OxyFluor','--OxyFluor', action="store_true",
               help='Temperature, Oxygen, Fluorometer vs depth')
parser.add_argument('-ParTurbFluor','--ParTurbFluor', action="store_true",
               help='PAR, Turbidity, Fluorometer vs depth')


args = parser.parse_args()

nc_path = args.DataPath

if not '.nc' in nc_path:
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]
else:
    nc_path = [nc_path,]
    
for ncfile in sorted(nc_path):
 
    print "Working on file %s " % ncfile
    nc = EcoFOCI_netCDF_read.EcoFOCI_netCDF(ncfile)
    ncdata = nc.ncreadfile_dic()
    g_atts = nc.get_global_atts()
    nc.close()
    cast_time = EPIC2Datetime.EPIC2Datetime(ncdata['time'],ncdata['time2'])[0]

    if not os.path.exists('images/' + g_atts['CRUISE']):
        os.makedirs('images/' + g_atts['CRUISE'])
    if not os.path.exists('images/' + g_atts['CRUISE'] + '/TSSigma/'):
        os.makedirs('images/' + g_atts['CRUISE'] + '/TSSigma/')
    if not os.path.exists('images/' + g_atts['CRUISE'] + '/TO2F/'):
        os.makedirs('images/' + g_atts['CRUISE'] + '/TO2F/')
    if not os.path.exists('images/' + g_atts['CRUISE'] + '/PARTurbFluor/'):
        os.makedirs('images/' + g_atts['CRUISE'] + '/PARTurbFluor/')


    try:
        g_atts['STATION_NAME'] = g_atts['STATION_NAME']
    except:
        g_atts['STATION_NAME'] = 'NA'

    if args.TSvD:
        CTDplot = CTDProfilePlot()

        (plt, fig) = CTDplot.plot3var(epic_key=['T_28','T2_35','S_41','S_42','ST_70','ST_2070'],
                         xdata=[ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],
                                ncdata['S_41'][0,:,0,0],ncdata['S_42'][0,:,0,0],
                                ncdata['ST_70'][0,:,0,0],
                                np.array([])],
                         ydata=ncdata['dep'][:],
                         xlabel=['Temperature (C)','Salinity (PSU)','SigmaT (kg/m^3)'],
                         secondary=True)

        ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                          fileid=ncfile.split('/')[-1],
                          castid=g_atts['CAST'],
                          stationid=g_atts['STATION_NAME'],
                          castdate=cast_time,
                          lat=ncdata['lat'][0],
                          lon=ncdata['lon'][0])

        t = fig.suptitle(ptitle)
        t.set_y(1.06)
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

        plt.savefig('images/' + g_atts['CRUISE'] + '/TSSigma/' + ncfile.split('/')[-1].split('.')[0] + '_plot_2TSSigma.png', bbox_inches='tight', dpi = (300))
        plt.close()

    if args.OxyFluor:
        CTDplot = CTDProfilePlot()

        fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
        for fkey in fluor_key_list:
            if fkey in ncdata.keys():
                fluor_key = fkey

        (plt, fig) = CTDplot.plot3var(epic_key=['T_28','T2_35','OST_62','CTDOST_4220',fluor_key,''],
                         xdata=[ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],
                                ncdata['OST_62'][0,:,0,0],ncdata['CTDOST_4220'][0,:,0,0],
                                ncdata[fluor_key][0,:,0,0],
                                np.array([])],
                         ydata=ncdata['dep'][:],
                         xlabel=['Temperature (C)','Oxygen % Sat.','Chlor-A mg/m^3'],
                         secondary=True)

        ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                          fileid=ncfile.split('/')[-1],
                          castid=g_atts['CAST'],
                          stationid=g_atts['STATION_NAME'],
                          castdate=cast_time,
                          lat=ncdata['lat'][0],
                          lon=ncdata['lon'][0])

        t = fig.suptitle(ptitle)
        t.set_y(1.06)
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

        plt.savefig('images/' + g_atts['CRUISE'] + '/TO2F/' + ncfile.split('/')[-1].split('.')[0] + '_plot_2TSSigma.png', bbox_inches='tight', dpi = (300))
        plt.close()

    if args.ParTurbFluor:
        CTDplot = CTDProfilePlot()

        fluor_key_list = ['F_903', 'Fch_906', 'fWS_973', 'Chl_933']
        for fkey in fluor_key_list:
            if fkey in ncdata.keys():
                fluor_key = fkey

        (plt, fig) = CTDplot.plot3var(epic_key=['PAR_905','','Trb_980','',fluor_key,''],
                         xdata=[ncdata['PAR_905'][0,:,0,0],np.array([]),
                                ncdata['Trb_980'][0,:,0,0],np.array([]),
                                ncdata[fluor_key][0,:,0,0],np.array([])],
                         ydata=ncdata['dep'][:],
                         xlabel=['PAR','Turbidity','Chlor-A mg/m^3'],
                         secondary=True)

        ptitle = CTDplot.add_title(cruiseid=g_atts['CRUISE'],
                          fileid=ncfile.split('/')[-1],
                          castid=g_atts['CAST'],
                          stationid=g_atts['STATION_NAME'],
                          castdate=cast_time,
                          lat=ncdata['lat'][0],
                          lon=ncdata['lon'][0])

        t = fig.suptitle(ptitle)
        t.set_y(1.06)
        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

        plt.savefig('images/' + g_atts['CRUISE'] + '/PARTurbFluor/' + ncfile.split('/')[-1].split('.')[0] + '_plot_2TSSigma.png', bbox_inches='tight', dpi = (300))
        plt.close()