# Ethan McGarrigle and Morgan Edwards
# HFC Modeling


import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') #fixes framework problem with GUI
import matplotlib.pyplot as plt

# Create Data frames within a dictionary 

## Scenarios refer to the different ways NA5 and A5 demand is modeled
    ## interp = Demand modeled by Linear interpolation 
    ## exp_growth = Demand modeled by Exponential Growth

## Start with just Refrigeration and AC; add more sectors later 
sector_List = ['MAC','SAC','DOM','IND','COM','TRANS','FOAMS','FIRE']
 # add 'policy_Islands' to the policy scenarios later
scenario_List = ['policy_EU','policy_NA','policy_India','interp','exp_growth']
region_List = ['NA5','A5']
vars_list = ['demand','bank','emissions','recycling','production','recovery','destruction']

## Construct a Dictionary with keys as such: { ('Scenario', 'Region (NA5 or A5)','Sector') : Data Frame}

data_frames = {} # data frames that contain sectorized breakdowns of each HFC flow variable

summed_sectors_data_frames = {} # data frames that contain the total (sum of all sectors) for each scenario 

global_data_frames = {} # data frames that contain the total sum of all sectors and all regions (NA5 and A5) for each scenario

for scenario in range(0,len(scenario_List)):
    for region in range(0,len(region_List)):
        for sector in range(0,len(sector_List)):
            data_frames.update( { (scenario_List[scenario],region_List[region],sector_List[sector]) : 
            pd.DataFrame(
            columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery','destruction'), 
            index = range(2014, 2051)
            ) } )
            summed_sectors_data_frames.update( { (scenario_List[scenario] , region_List[region]) : 
            pd.DataFrame(
            columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery','destruction'), 
            index = range(2014, 2051) ) } )
            global_data_frames.update( { (scenario_List[scenario]) : 
            pd.DataFrame(
            columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery','destruction'), 
            index = range(2014, 2051) ) } )

            



### Insert emissions factors here (Velders 2015si and TEAP 2016/TEAP 2015b)

ems_factors_dict = {('MAC','NA5') : 0.15175, ('MAC','A5'): 0.15, ('SAC','NA5') : 0.07125, ('SAC','A5') : 0.0665, 
    ('IND','NA5') : 0.0875, ('IND','A5') : 0.11, ('DOM','NA5') : 0.025, ('DOM','A5') : 0.025, ('COM','NA5') : 0.13475,
    ('COM','A5') : 0.11, ('TRANS','NA5') : 0.197, ('TRANS','A5') : 0.197, ('FIRE','NA5') : 0.03, ('FIRE','A5') : 0.03, 
    ('FOAMS','NA5') : 0.05, ('FOAMS','A5') : 0.05 }
## Foams emissions factors vary between foams and will be applied to percentages of the foam bank in the flows section

### Insert Sector-breakdown percentages of demand here: (TEAP 2014b) (Mt CO2-eq)
sector_prcnts = {('MAC','NA5',2015) : 0.1776, ('MAC','NA5',2020) : 0.1478, ('MAC','NA5',2025) : 0.1307, ('MAC','NA5',2030) : 0.129, (
    'SAC','NA5',2015) : 0.513, ('SAC','NA5',2020) : 0.5866, ('SAC','NA5',2025) : 0.6556, ('SAC','NA5',2030) : 0.6786, (
    'DOM','NA5',2015) : 0.0037, ('DOM','NA5',2020) : 0.0025, ('DOM','NA5',2025) : 0.0023, ('DOM','NA5',2030) : 0.0022, (
    'COM','NA5',2015) : 0.2537, ('COM','NA5',2020) : 0.2198, ('COM','NA5',2025) : 0.174, ('COM','NA5',2030) : 0.156, (
    'IND','NA5',2015) : 0.0356, ('IND','NA5',2020) : 0.028, ('IND','NA5',2025) : 0.024, ('IND','NA5',2030) : 0.0227, (
    'TRANS','NA5',2015) : 0.0165, ('TRANS','NA5',2020) : 0.0147, ('TRANS','NA5',2025) : 0.013, ('TRANS','NA5',2030) : 0.016, (
    'MAC','A5',2015) : 0.144, ('MAC','A5',2020) : 0.128, ('MAC','A5',2025) : 0.109, ('MAC','A5',2030) : 0.1026, (
    'SAC','A5',2015) : 0.5017, ('SAC','A5',2020) : 0.5186, ('SAC','A5',2025) : 0.4819, ('SAC','A5',2030) : 0.4722, (
    'DOM','A5',2015) : 0.0387, ('DOM','A5',2020) : 0.026, ('DOM','A5',2025) : 0.02, ('DOM','A5',2030) : 0.0166, (
    'COM','A5',2015) : 0.28, ('COM','A5',2020) : 0.283, ('COM','A5',2025) : 0.346, ('COM','A5',2030) : 0.36, (
    'IND','A5',2015) : 0.0185, ('IND','A5',2020) : 0.0289, ('IND','A5',2025) : 0.030, ('IND','A5',2030) : 0.031, (
    'TRANS','A5',2015) : 0.0169, ('TRANS','A5',2020) : 0.0147, ('TRANS','A5',2025) : 0.0132, ('TRANS','A5',2030) : 0.0116 }

### Insert Bank 2015 breakdown percentages 
bank_prcnts = { ('MAC','NA5') : 0.325942 , ('MAC','A5') : 0.250457, ('SAC','A5') : 0.258529, ('SAC','NA5') : 0.393038, (
    'COM','NA5') : 0.169199, ('COM','A5') : 0.285630, ('TRANS','NA5') : 0.012194, ('TRANS','A5') : 0.003385, (
    'IND','NA5') : 0.046744, ('IND','A5') : 0.025824, ('DOM','NA5') : 0.052884, ('DOM','A5') : 0.176175 }


### Insert Servicing Demand Tables from TEAP 2016 
## Mt CO2-eq (reported in kt CO2-eq from TEAP 2016)

servc_demand_estimates = { ('MAC','NA5',2015) : 65.959, ('MAC','NA5',2020) : 57.008, ('MAC','NA5',2025) : 42.495, ('MAC','NA5',2030) : 27.579, ('MAC','NA5',2035) : 22.448, (
    'MAC','NA5',2040) : 26.023, ('MAC','NA5',2045): 30.167, ('MAC','NA5',2050): 34.972, ('SAC','NA5',2015) : 48.696, ('SAC','NA5',2020) : 76.968, ('SAC','NA5',2025) : 98.555, (
    'SAC','NA5',2030) : 105.746,  ('SAC','NA5',2035) : 116.640, ('SAC','NA5',2040) : 130.410, ('SAC','NA5',2045): 146.371, ('SAC','NA5',2050): 164.875,(
    'DOM','NA5',2015) : 0.004, ('DOM','NA5',2020) : 0.003, ('DOM','NA5',2025) : 0.002, ('DOM','NA5',2030) : 0.001, (
    'DOM','NA5',2035) : 0.001, ('DOM','NA5',2040) : 0.002, ('DOM','NA5',2045): 0.002, ('DOM','NA5',2050): 0.001, (
    'COM','NA5',2015) : 52.299, ('COM','NA5',2020) : 40.636, ('COM','NA5',2025) : 25.944, ('COM','NA5',2030) : 18.361, (
    'COM','NA5',2035) : 16.998, ('COM','NA5',2040) : 19.705, ('COM','NA5',2045): 22.844, ('COM','NA5',2050): 26.482, (
    'IND','NA5',2015) : 2.205, ('IND','NA5',2020) : 2.295, ('IND','NA5',2025) : 2.123, ('IND','NA5',2030) : 1.848, (
    'IND','NA5',2035) : 1.779, ('IND','NA5',2040) : 1.909, ('IND','NA5',2045): 1.941, ('IND','NA5',2050): 1.957, (
    'TRANS','NA5',2015) : 3.362, ('TRANS','NA5',2020) : 3.495, ('TRANS','NA5',2025) : 3.104, ('TRANS','NA5',2030) : 2.682, (
    'TRANS','NA5',2035) : 2.429, ('TRANS','NA5',2040) : 2.312, ('TRANS','NA5',2045): 2.177, ('TRANS','NA5',2050): 2.020, (
    'MAC','A5',2015) : 24.465, ('MAC','A5',2020) : 33.615, ('MAC','A5',2025) : 42.676, ('MAC','A5',2030) : 54.204, ('MAC','A5',2035) : 69.179, (
    'MAC','A5',2040) : 88.292, ('MAC','A5',2045): 112.686, ('MAC','A5',2050): 143.819, ('SAC','A5',2015) : 93.574, ('SAC','A5',2020) : 207.716, ('SAC','A5',2025) : 376.891, (
    'SAC','A5',2030) : 588.252,  ('SAC','A5',2035) : 806.125, ('SAC','A5',2040) : 995.730, ('SAC','A5',2045): 1151.882, ('SAC','A5',2050): 1265.513,(
    'DOM','A5',2015) : 0.676, ('DOM','A5',2020) : 0.948, ('DOM','A5',2025) : 1.210, ('DOM','A5',2030) : 1.447, (
    'DOM','A5',2035) : 1.709, ('DOM','A5',2040) : 2.089, ('DOM','A5',2045): 2.572, ('DOM','A5',2050): 3.196, (
    'COM','A5',2015) : 42.163, ('COM','A5',2020) : 97.346, ('COM','A5',2025) : 180.431, ('COM','A5',2030) : 283.822, (
    'COM','A5',2035) : 407.198, ('COM','A5',2040) : 540.880, ('COM','A5',2045): 683.077, ('COM','A5',2050): 851.240, (
    'IND','A5',2015) : 6.858, ('IND','A5',2020) : 16.294, ('IND','A5',2025) : 30.257, ('IND','A5',2030) : 46.901, (
    'IND','A5',2035) : 64.494, ('IND','A5',2040) : 84.427, ('IND','A5',2045): 107.328, ('IND','A5',2050): 133.933, (
    'TRANS','A5',2015) : 3.201, ('TRANS','A5',2020) : 5.416, ('TRANS','A5',2025) : 7.948, ('TRANS','A5',2030) : 10.267, (
    'TRANS','A5',2035) : 12.730, ('TRANS','A5',2040) : 15.823, ('TRANS','A5',2045): 19.888, ('TRANS','A5',2050): 24.821}

## A dictionary that contains servicing demand arrays for each sector and region; f
## for example: serv_demand_sched.get( ('MAC','NA5') ) returns an array of servicing demand values from 2014 to 2050 for the MAC sector for NA5 countries 
servc_demand_arrs = {}

## A dictionary that contains arrays of interpolated sector percentages between estimates and will likely contain extrapolated percentages 
sector_percnts_arrs = {}

estimate_years_TEAP = [2014,2015,2020,2025,2030,2035,2040,2045,2050] # Years for TEAP 2016 estimates




### Assumptions

# SAC NA5 ems factor is an equally weighted average of 4 groups that are NA5 countries (Velders 2015si)
# sac_a5_ems_factor is an equally weighted average of 2 groups that make up A5 countries (Velders 2015si)
### No emissions factor given for A5/developing countries, so for now, will assume they are the same as NA5 as a place holder for Velders 2015si


# AER: Aerosols Sector (break up into medical and non-medical?)
    # TEAP 2009 updated supplement groups non-medical aerosols with solvents, but leaves medical aerosols as a separate group 
    # have not decided whether this model will do the same as of yet 

# FIRE: Fire Protection Sector

# FOAM: Foams Sector
## Foam estimates by TEAP 2009, supplement report only report HFC banks and foams globally (no data for A5 and NA5 countries)


# AER: Aerosols Sector (break up into medical and non-medical?)
    # TEAP 2009 updated supplement groups non-medical aerosols with solvents, but leaves medical aerosols as a separate group 
    # have not decided whether this model will do the same as of yet 


# FIRE: Fire Protection Sector

# FOAM: Foams Sector
## Foam estimates by TEAP 2009, supplement report only report HFC banks and foams globally (no data for A5 and NA5 countries)


# Models

def linearExtrapolation(x1,x2,x3,y1,y2):
    # x1 and x2 are the x-coords of the known data points, x3 is the x-value of the unknown point
    # y1 and y2 are the y-coords of the known data points, y3 is the y-value of the unknown point
    y3 = y1 + (y2-y1)*((x3-x1)/(x2-x1))
    return y3


def exponentialGrowth(x_0,r,t_0,t_f):
    # x_0 is the initial value of whatever you are modeling
    # r is the growth rate 
    # t_0 is the initial/starting time
    # t_f is the final/ending time
    xarray = []
    xarray.append(x_0)
    deltaT = t_f - t_0
    for t in range(1,deltaT+1):
        x = x_0*(1+r)**(t)
        xarray.append(x)
    return xarray


# Interpolate servicing demand to create a full demand list from 2015-2050 


for region in range(0,len(region_List)):
    for sector in range(0,len(sector_List)):
        if (sector_List[sector] != 'FIRE') and (sector_List[sector] != 'FOAMS') :
            # Servicing Demand 
            estimates = []
            interp_servicing_demand = []
            for t in range(2015,2055,5):
                # Add each servicing demand estimate to a list for each sector
                estimates.append(servc_demand_estimates[(sector_List[sector],region_List[region],t)])
            # Extrapolate a 2014 estimate and insert it in the beginning of the estimates array
            estimate_2014 = linearExtrapolation(2015,2020,2014,estimates[0],estimates[1])
            estimates.insert(0,estimate_2014)
            # interpolate the demand after the list is filled 
            interp_servicing_demand = np.interp(list(range(2014,2051)),estimate_years_TEAP,estimates)
            # Add the interpolated demand to its dictionary 
            servc_demand_arrs.update( { (sector_List[sector], region_List[region]) : interp_servicing_demand  } )

            # Sector Percents 
            prcnt_estimates = []
            interp_sector_percents = []
            for t in range(2015,2035,5):
                # Add each percentage to the list
                prcnt_estimates.append(sector_prcnts.get((sector_List[sector],region_List[region],t)))
            # Extrapolate a 2014 estimate and insert into the beginning of the estimates array 
            prcnt_estimates.insert(0,linearExtrapolation(2015,2020,2014,prcnt_estimates[0],prcnt_estimates[1]))
            # interpolate the percentages 
            interp_sector_percents = np.interp(list(range(2014,2031)),[2014,2015,2020,2025,2030],prcnt_estimates)
            # Add the percentages list to a dictionary 
            sector_percnts_arrs.update( { (sector_List[sector],region_List[region]) : interp_sector_percents } )



# Reported Consumption from Excel Spreadsheet for A5 and NA5 Countries t: [1992,2014]  [Mt CO2-eq]
na5_historical_consumption = [1.13,14.81,32.68,42.78,47.30,58.57,77.05,107.78,152.24,166.05,198.82,240.64,278.20,316.42,345.07,379.10,416.99,460.90,495.30,595.63,670.99,694.67,695.46]
a5_historical_consumption = [0.02,0.41,0.93,1.66,2.62,3.64,4.59,5.90,7.88,14.21,22.04,29.68,39.55,52.76,91.97,126.79,149.58,184.90,243.65,343.74,397.54,466.01,537.83]


## Fill in the 2015 estimates for banks for each sector based on percentage breakdowns for sectors 
for scenario in range(0,len(scenario_List)):
    for region in range(0,len(region_List)):
        if region_List[region] == 'NA5' :
            bank_estimate = 3191
        elif region_List[region] == 'A5' :
            bank_estimate = 1127
        for sector in range(0,len(sector_List)):
            if (sector_List[sector] != 'FIRE') and (sector_List[sector] != 'FOAMS') :
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[2015,'bank'] = bank_estimate * (
                    bank_prcnts.get( (sector_List[sector], region_List[region]) )) # Mt CO2-eq (TEAP 2009 updated supplement)



rec_fac = 0.4 # recycling factor (as a fraction of emissions factor)


#### Based on checking these numbers from the TEAP 2009 updated supplement with the reports
#### it seems that these bank and emissions estimates are generally underestimating by about 100 Mt CO2-eq, so they will be semi-accurate placeholders for now


## Extrapolate Consumption, Emissions, Banks for 2015-2050 BAU for NA5 and A5 Countries Separately
#for t in range(2017,2051) :
    # Calculate consumption 
 #   na5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_bau_flows.loc[t-2,'demand'],na5_bau_flows.loc[t-1,'demand'])
  #  a5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_bau_flows.loc[t-2,'demand'],a5_bau_flows.loc[t-1,'demand'])


################### Exponential Growth Scenario #######################

# Note: Sector bank percentages from TEAP 2009 report are based on the modeled banks in tonnes, no data was provided
# for modeled banks in tCO2-eq, so these percentages are prone to error 

### Assuming a 15% annual servicing of the bank

servicing_pcnt = 0.15



########### Foams sector

# estimate foams refrigeration consumption as a percentage of total consumption 
na5_foam_dem_estimates = [79.003, 86.049, 95.004, 104.892] # Mt CO2-eq; 2015,2020,2025,2030
annual_na5_foam_growth_rate = 0.0218 # Calculated from TEAP 2014b reported HFC foams demand
a5_foam_dem_estimates = [13.466,21.035,33.408,41.633] # Mt CO2-eq; 2015,2020,2025,2030; HFC's only; a lot smaller because of increased use of HCFC in A5 countries 
annual_a5_foam_growth_rate = 0.139 ## large, given HCFC's are still phasing out of A5 countries 

# data_frames[('exp_growth','NA5','FOAMS')].loc[2015,'demand'] = 79.003
# data_frames[('exp_growth','A5','FOAMS')].loc[2015,'demand'] = 13.466 
data_frames[('exp_growth','NA5','FOAMS')]['demand'] = exponentialGrowth(
    linearExtrapolation(2015,2020,2014,79.003,86.049),0.0218,2014,2050)
data_frames[('exp_growth','A5','FOAMS')]['demand'] = exponentialGrowth(
    linearExtrapolation(2015,2020,2014,13.466,21.035),0.139,2014,2050)

data_frames[('interp','NA5','FOAMS')]['demand'] = data_frames[('exp_growth','NA5','FOAMS')]['demand']
data_frames[('interp','A5','FOAMS')]['demand'] = data_frames[('exp_growth','A5','FOAMS')]['demand']

#### No A5/NA5 breakdown provided for banks; estimate using percentages from demand: 85% NA5; 15% A5
    ### These percentages are very likely to change as A5 grows; these are just for 2015 estimate 

### Global foam bank = 604.811 # Mt CO2-eq 

for scenario in range(0,len(scenario_List)):
    data_frames[(scenario_List[scenario],'NA5','FOAMS')].loc[2015,'bank'] =  514.089 # [Mt CO2-eq]
    data_frames[(scenario_List[scenario],'A5','FOAMS')].loc[2015,'bank'] = 90.722 # [Mt CO2-eq]



### Both BAU scenarios use exponential growth because of lack of FOAM data available

####### Aerosols 

# estimate Aerosol consumption 

# extrapolate aerosol consumption using exponential growth with TEAP 2009 updated supplement growth rates

# Estimate Aerosol bank 

# See Velders 2015si for emissions factors


# Velders 2015si breaks up foams emissions factors into open cell foams, extruded polystyrene foams (XPS), and Polyurethane foams (PUR)

#foams_emissions_fac = 0.026 # global estimate; the average of 6 ratios of TEAP modeled emissions to banks, averaged over the years 2015-2020 (one ratio for each year)


####### Fire Exstinguishing Systems

# Estimate HFC-fire bank 


for scenario in range(0,len(scenario_List)):
    data_frames[(scenario_List[scenario],'NA5','FIRE')].loc[2015,'bank'] =  147.996 # [Mt CO2-eq]
    data_frames[(scenario_List[scenario],'A5','FIRE')].loc[2015,'bank'] = 63.945 # [Mt CO2-eq]


## Fire growth rate based on 2015-2020 change in the bank 
a5_fire_grwth_rate = 0.07757
na5_fire_grwth_rate = 0.07705

# estimate Fire exstinguishing system HFC consumption using a bank calculation

na5_fire_cons_estimate = (((147996)/(1-0.03)) - 138461) * 10**(-3) ### (2015 bank / ems factor) - 2014 bank = 2014 consumption
    # = 14.11219588 Mt CO2-eq
a5_fire_cons_estimate = (((63945)/(1-0.03)) - 59806) * 10**(-3)
    # = 31.544 # Mt CO2-eq

# extrapolate hfc-fire consumption using exponential growth with TEAP 2009 updated supplement growth rates

data_frames[('exp_growth','NA5','FIRE')]['demand'] = exponentialGrowth(na5_fire_cons_estimate,0.07705,2014,2050)
data_frames[('exp_growth','A5','FIRE')]['demand'] = exponentialGrowth(a5_fire_cons_estimate,0.07757,2014,2050)

data_frames[('interp','NA5','FIRE')]['demand'] = data_frames[('exp_growth','NA5','FIRE')]['demand']
data_frames[('interp','A5','FIRE')]['demand'] = data_frames[('exp_growth','A5','FIRE')]['demand']
# See Velders 2015si for Fire-bank emissions factors
    #fire_ems_factor = 0.03 # all regions

#### Both BAU scenarios use exponential growth because of lack of FIRE data 

## Solvents?


## Extrapolate 2015 Consumption for NA5 and A5 countries as a total of the 6 R/AC sectors 

na5_2014_cons_estimate = 695.47 - (
    data_frames[('exp_growth','NA5','FOAMS')].loc[2014,'demand'] + data_frames[('exp_growth',
        'NA5','FIRE')].loc[2014,'demand'])
a5_2014_cons_estimate = 537.83 - (
    data_frames[('exp_growth','A5','FOAMS')].loc[2014,'demand'] + data_frames[('exp_growth',
        'A5','FIRE')].loc[2014,'demand'])

na5_2015_cons_estimate = linearExtrapolation(2013,2014,2015,694.67,695.46)
a5_2015_cons_estimate = linearExtrapolation(2013,2014,2015,466.01,537.83)




################### MAC ######################

    #assume constant percentage break downs for total consumption into sectors
    #assume growth rates do not change (may relax later)
    #assume 2015 percentage break down applies to 2015 and 2016 so that 2 points can be generated for 
    #linear extrapolation 


data_frames[('exp_growth','NA5','MAC')].loc[2014,'demand'] = (0.1776)*na5_2014_cons_estimate # [Mt CO2-eq]
data_frames[('exp_growth','A5','MAC')].loc[2014,'demand'] = (0.144)*a5_2014_cons_estimate # [Mt CO2-eq]


# exponentially model consumption for MAC
data_frames[('exp_growth','NA5','MAC')].loc[2014:2020,'demand'] = exponentialGrowth( data_frames[('exp_growth','NA5','MAC')].loc[2014,'demand'], 0.0054, 2014, 2020) # [Mt CO2-eq]
data_frames[('exp_growth','A5','MAC')].loc[2014:2020,'demand'] = exponentialGrowth( data_frames[('exp_growth','A5','MAC')].loc[2014,'demand'], 0.05, 2014, 2020) # [Mt CO2-eq]
data_frames[('exp_growth','NA5','MAC')].loc[2020:2050,'demand'] = exponentialGrowth( data_frames[('exp_growth','NA5','MAC')].loc[2020,'demand'], 0.03, 2020, 2050) # [Mt CO2-eq]
data_frames[('exp_growth','A5','MAC')].loc[2020:2050,'demand'] = exponentialGrowth( data_frames[('exp_growth','A5','MAC')].loc[2020,'demand'], 0.05, 2020, 2050) # [Mt CO2-eq]


# MAC bank estimates BAU 
    # To estimate the bank of MAC HFC's, the sector bank percentages from TEAP 2009 (updated Supplement) report are applied to the 
    # overall bank estimates (3191, 1127) (NA5, A5 Countries)


# note: having the (1-ems_factor) attached to the bank calculation is the same as separately calculating emissions and subtracting them out

############## SAC: Stationary Air Conditioning

data_frames[('exp_growth','A5','SAC')].loc[2014,'demand'] = a5_2014_cons_estimate*0.5017 # [Mt CO2-eq]
data_frames[('exp_growth','NA5','SAC')].loc[2014,'demand'] = na5_2014_cons_estimate*0.513 # [Mt CO2-eq]

#extrapolate consumption exponentially; TEAP growth rates for NA5 countries are a non-weighted average of the given growth rates
    # assumes equal weighting for NA5 Countries: Something to relax in the future? Weighted average? or break up by country?

data_frames[('exp_growth','NA5','SAC')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','SAC')].loc[2014,'demand'],0.012,2014,2020)
data_frames[('exp_growth','A5','SAC')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','SAC')].loc[2014,'demand'],0.01,2014,2020)
data_frames[('exp_growth','NA5','SAC')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','SAC')].loc[2020,'demand'],0.03 ,2020,2050)
data_frames[('exp_growth','A5','SAC')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','SAC')].loc[2020,'demand'],0.01,2020,2050)
 

############# Domestic Refrigeration Sector (DOM)

# Generate consumption estimates for this sector as a percentage of total demand
data_frames[('exp_growth','NA5','DOM')].loc[2014,'demand'] = na5_2014_cons_estimate*0.0037
data_frames[('exp_growth','A5','DOM')].loc[2014,'demand'] = a5_2014_cons_estimate*0.0387

# Extrapolate the rest of consumption for the sector using exponential growth
# growth rates are averages of the growth rates for the groups of countries within the NA5 and A5 groupings
data_frames[('exp_growth','NA5','DOM')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','DOM')].loc[2014,'demand'],0.016,2014,2020)
data_frames[('exp_growth','A5','DOM')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','DOM')].loc[2014,'demand'],0.058,2014,2020)
data_frames[('exp_growth','NA5','DOM')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','DOM')].loc[2020,'demand'],0.03,2020,2050)
data_frames[('exp_growth','A5','DOM')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','DOM')].loc[2020,'demand'],0.058,2020,2050)


################# Commercial Refrigeration Sector (COM)

# estimate Commercial refrigeration consumption as a percentage of total consumption
data_frames[('exp_growth','NA5','COM')].loc[2014,'demand'] = na5_2014_cons_estimate*(0.2537)
data_frames[('exp_growth','A5','COM')].loc[2014,'demand'] = a5_2014_cons_estimate*(0.28)


# Extrapolate Consumption using exponential growth

data_frames[('exp_growth','NA5','COM')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','COM')].loc[2014,'demand'],0.021,2014,2020)
data_frames[('exp_growth','A5','COM')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','COM')].loc[2014,'demand'],0.018,2014,2020)
data_frames[('exp_growth','NA5','COM')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','COM')].loc[2020,'demand'],0.03,2020,2050)
data_frames[('exp_growth','A5','COM')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','COM')].loc[2020,'demand'],0.045,2020,2050)

############### Industrial Refrigeration (IND)

# estimate Industrial refrigeration consumption as a percentage of total consumption
data_frames[('exp_growth','NA5','IND')].loc[2014,'demand'] = na5_2014_cons_estimate*(0.0356)
data_frames[('exp_growth','A5','IND')].loc[2014,'demand'] = a5_2014_cons_estimate*(0.0185)


# Extrapolate Consumption using exponential growth

data_frames[('exp_growth','NA5','IND')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','IND')].loc[2014,'demand'],0.051,2014,2020)
data_frames[('exp_growth','A5','IND')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','IND')].loc[2014,'demand'],0.018,2014,2020)
data_frames[('exp_growth','NA5','IND')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','IND')].loc[2020,'demand'],0.04,2020,2050)
data_frames[('exp_growth','A5','IND')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','IND')].loc[2020,'demand'],0.037,2020,2050)

############ Transport Refrigeration (TRANS) sector

# estimate transportation refrigeration consumption as a percentage of total consumption
data_frames[('exp_growth','NA5','TRANS')].loc[2014,'demand'] = na5_2014_cons_estimate*(0.0165)
data_frames[('exp_growth','A5','TRANS')].loc[2014,'demand'] = a5_2014_cons_estimate*(0.0169)


# Extrapolate Consumption using exponential growth

data_frames[('exp_growth','NA5','TRANS')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','TRANS')].loc[2014,'demand'],0.02,2014,2020)
data_frames[('exp_growth','A5','TRANS')].loc[2014:2020,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','TRANS')].loc[2014,'demand'],0.018,2014,2020)
data_frames[('exp_growth','NA5','TRANS')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','NA5','TRANS')].loc[2020,'demand'],0.03,2020,2050)
data_frames[('exp_growth','A5','TRANS')].loc[2020:2050,'demand'] = exponentialGrowth(data_frames[('exp_growth','A5','TRANS')].loc[2020,'demand'],0.045,2020,2050)



####################### Scenario 2 (linear interpolation of 5-year TEAP demand estimates) - TEAP 2016

#### NA5 are placeholder for now, consider using more accurate demand estimates 


###### Motor Air Conditioning (MAC) 
na5_mac_demand_estimates = [linearExtrapolation(2015,2020,2014,88.867,62.970),88.867,62.970,49.587,35.812,31.998,37.094,43.002,49.851] # Mt CO2-eq
a5_mac_demand_estimates = [linearExtrapolation(2015,2020,2014,66.815,86.684),66.815,86.684,110.406,140.647,179.505,229.099,292.395,373.178] # Mt CO2-eq


data_frames[('interp','NA5','MAC')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_mac_demand_estimates)
data_frames[('interp','A5','MAC')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_mac_demand_estimates)



### Stationary Air Conditioning (SAC)

na5_sac_demand_estimates = [ linearExtrapolation(2015,2020,2014,197.747, 226.484),197.747,226.484,271.380,306.098,348.903,399.665,458.512,526.733] # Mt CO2-eq
a5_sac_demand_estimates = [ linearExtrapolation(2015,2020,2014,297.348,540.012),297.348,540.012,836.773,1172.226,1435.230,1673.455,1881.983,2052.031] # Mt CO2-eq

data_frames[('interp','NA5','SAC')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_sac_demand_estimates)
data_frames[('interp','A5','SAC')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_sac_demand_estimates)




#### Transportation Refrigeration (TRANS)

na5_TRANS_demand_estimates = [ linearExtrapolation(2015,2020,2014,6.343,4.174),6.343,4.174,3.993,3.713,3.623,3.696,3.782,3.881] # Mt CO2-eq
a5_TRANS_demand_estimates = [ linearExtrapolation(2015,2020,2014,8.809,11.212),8.809,11.212,15.744,20.565,25.563,31.814,39.817,49.656] # Mt CO2-eq

data_frames[('interp','NA5','TRANS')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_TRANS_demand_estimates)
data_frames[('interp','A5','TRANS')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_TRANS_demand_estimates)


##### Commercial Refrigeration (COM)

na5_COM_demand_estimates = [ linearExtrapolation(2015,2020,2014,66.582,51.407),66.582,51.407,35.389,29.310,29.691,34.420,39.902,46.257] # Mt CO2-eq
a5_COM_demand_estimates = [ linearExtrapolation(2015,2020,2014,130.374,231.006),130.374,231.006,401.142,604.083,806.301,1038.235,1302.872,1623.617] # Mt CO2-eq

data_frames[('interp','NA5','COM')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_COM_demand_estimates)
data_frames[('interp','A5','COM')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_COM_demand_estimates)



##### Industrial Refrigeration (IND)

na5_IND_demand_estimates = [ linearExtrapolation(2015,2020,2014,4.375,3.530),4.375,3.530,3.134,2.524,2.562,2.817,2.994,3.178] # Mt CO2-eq
a5_IND_demand_estimates = [ linearExtrapolation(2015,2020,2014,14.058,27.623),14.058,27.623,48.071,67.841,89.605,114.539,143.440,177.238] # Mt CO2-eq

data_frames[('interp','NA5','IND')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_IND_demand_estimates)
data_frames[('interp','A5','IND')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_IND_demand_estimates)


#### Domestic Refrigeration (DOM)

na5_DOM_demand_estimates = [ linearExtrapolation(2015,2020,2014,1.895,1.255),1.895,1.255,1.256,1.143,1.325,1.536,1.781,2.064] # Mt CO2-eq
a5_DOM_demand_estimates = [ linearExtrapolation(2015,2020,2014,17.422,20.136),17.442,20.136,24.029,28.594,35.550,44.248,55.110,68.668] # Mt CO2-eq

data_frames[('interp','NA5','DOM')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,na5_DOM_demand_estimates)
data_frames[('interp','A5','DOM')]['demand'] = np.interp(list(range(2014,2051)),estimate_years_TEAP,a5_DOM_demand_estimates)



# sum the demand of each sector for each region, needed to model the demand from the india proposal 

for scenario in range(0,len(scenario_List)):
    if (scenario_List[scenario] == 'interp') or (scenario_List[scenario] == 'exp_growth') :
        for region in range(0,len(region_List)):
            summed_sectors_data_frames[scenario_List[scenario],region_List[region]]['demand'] = 0 # must set equal to 0, otherwise "+=" doesnt work
            for sector in range(0,len(sector_List)):
                summed_sectors_data_frames[scenario_List[scenario],region_List[region]]['demand'] += data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['demand']


############# Policy Scenarios ###############

year = list(range(2014,2051))

#### North America Proposal 

# NA5 Baseline: 100% of average HFC consumption and production and 75% of average HCFC Consumption and production from 2011-2013
# A5 Baseline: 100% of average HFC consumption and 50% of average HCFC consumption and production from 2011-2013

# NA5 steps: 
    # 2019: 90%; 2024: 65%; 2030: 30%; 2036: 15%
# A5 steps: 
    # 2021: 100%; 2026: 80%; 2032: 40%; 2046: 15%

na5_NA_policy_years = [2014, 2019, 2024, 2030, 2036, 2050]
na5_NA_policy_targets = [695.46, 649.10, 468.79, 216.37, 108.18, 108.18] # [Mt CO2-eq]
a5_NA_policy_years = [2014, 2021, 2026, 2032, 2046, 2050]
a5_NA_policy_targets = [537.83, 836.32, 669.05, 334.53, 125.45, 125.45] # [Mt CO2-eq]


# interpolate the targets

na5_NA_policy = np.interp(year,na5_NA_policy_years,na5_NA_policy_targets)
a5_NA_policy = np.interp(year,a5_NA_policy_years,a5_NA_policy_targets)


#### Island Proposal 

## See india proposal and general montreal protocl termonology for annex groups
## Hold off for now 

##### India Proposal

# NA5 Baseline: average of 2013-2015 consumption, freeze in 2016 (100% of baseline) 
# A5 Baseline: average of 2028-2030, freeze (100% baseline) in 2031,
#phase-down (flexible approach) to reach plateau of 15% of baseline in 2035 (NA5) and 2050 (A5)

india_na5_baseline = (na5_2015_cons_estimate + na5_historical_consumption[22] + 694.67)/3
# india_a5_baseline is based on modeled consumption and is therefore subject to change and error

india_a5_baseline = 1358.5969 # use average of 'interp' and 'exp_growth' scenario baselines 

na5_INDIA_policy_years = [2014,2016,2035,2050]
na5_INDIA_policy_targets = [695.5,india_na5_baseline,(0.15*india_na5_baseline),(0.15*india_na5_baseline)]
a5_INDIA_policy_years = [2014,2031,2050]
a5_INDIA_policy_targets = [537.83, india_a5_baseline, (0.15)*india_a5_baseline]

# from linear interpolation scenario; A5 baseline = 1914.3978
# from exponential growth scenario; A5 baseline = 802.596
# average of the two baselines = 1358.5969
# average of modeled 2031 A5 consumption from the 2 scenarios: 

na5_india_policy = np.interp(year,na5_INDIA_policy_years,na5_INDIA_policy_targets) 
a5_india_policy = np.interp(year,a5_INDIA_policy_years,a5_INDIA_policy_targets)



###### EU Proposal 

# Policy targets for A5 (Article 5) and NA5 (Non Article 5) countries (taken from the EU proposal):
    # NA5: 2009-2012 average of HFC consumption + 45% of 2009-2012 average of HCFC Consumption = Baseline
    # A5: 2009-2012 average of HFC consumption + 70% of 2009-2012 average of HCFC Consumption = Baseline


na5_EU_policy_years = [2014, 2019, 2034, 2050]
na5_EU_policy_targets = [695.5, 520.6, 91.9, 91.9] # [Mt CO2-eq]
a5_EU_policy_years = [2014, 2019, 2040, 2050]
a5_EU_policy_targets = [537.8, 896.3, 134.4, 134.4] # [Mt CO2-eq]



# Interpolate policy targets for total demand (linear interpolation): (2014-2050)
na5_EU_policy = np.interp(year, na5_EU_policy_years, na5_EU_policy_targets)
a5_EU_policy = np.interp(year, a5_EU_policy_years, a5_EU_policy_targets)
#global_policy = [sum(x) for x in zip(na5_EU_policy, a5_EU_policy)]



projected_years = [2015,2020,2025,2030]


### Sectorized breakdown for each policy scenario 

# Using the sectorized percentages in the dictionary, breakdown demand by sector by applying percentages in appropriate years 

policies_dict = {}

# fill a dictionary of interpolated policy for each region to make looping easier 
policies_dict.update({('NA5','policy_NA') : na5_NA_policy, ('A5','policy_NA') : a5_NA_policy, (
    'NA5','policy_EU') : na5_EU_policy, ('A5','policy_EU') : a5_EU_policy, (
    'NA5','policy_India') : na5_india_policy, ('A5','policy_India') : a5_india_policy})

### Note: Extrapolation generates negative consumption results after 2036

### Apply the sector-based percentages to the demand estimates in the appropriate years
### Extrapolate demand until constant using linear extrapolation 
for scenario in range(0,len(scenario_List)):
    # precautionary if statement; these loops are only for the policy scenarios 
    if 'policy' in scenario_List[scenario] :
        for region in range(0,len(region_List)):
            # Define the "last year", which is the last year after which the demand estimates stay constant until 2050
            if scenario_List[scenario] == 'policy_NA' :
                if region_List[region] == 'NA5' : # extrapolate until 2036, constant afterwards 
                    last_year = 2036
                elif region_List[region] == 'A5' : # extrapolate until 2046, constant afterwards 
                    last_year = 2046 
            if scenario_List[scenario] == 'policy_EU' :
                    last_year = 2034
            if scenario_List[scenario] == 'policy_India' :
                if region_List[region] == 'NA5' : # extrapolate until 2035, constant afterward 
                    last_year = 2035
                elif region_List[region] == 'A5' : # extrapolate until 2050, constant afterward 
                    last_year = 2050

            # set up the correct region's total demand estimates; percentages are applied to these estimates to estimate demand within each sector 
            policy_demand = policies_dict.get( (region_List[region], scenario_List[scenario] ) )

            # Generate demand percentages for foams and fire (non R/AC sectors), only need through 2030
            foams_pcnt = [(n/m) for n,m in zip(data_frames[('exp_growth',region_List[region],'FOAMS')].loc[2014:last_year,'demand'],summed_sectors_data_frames[('exp_growth',region_List[region])].loc[2014:last_year,'demand'])]
            fires_pcnt = [(n/m) for n,m in zip(data_frames[('exp_growth',region_List[region],'FIRE')].loc[2014:last_year,'demand'],summed_sectors_data_frames[('exp_growth',region_List[region])].loc[2014:last_year,'demand'])]

            policy_demand_RAC = [n - (n*m) - (n*q) for n,m,q in zip(policy_demand,foams_pcnt,fires_pcnt)]

            for sector in range(0,len(sector_List)):
                policy_estimates = []
                if (sector_List[sector] != 'FOAMS') and (sector_List[sector] != 'FIRE') :
                # Fill a temporary list of policy estimates in the year 2015,2020,2025,and 2030 in each sector
                    for t in range (2015,2035,5): # all policies 
                        # Apply percentages of each sector to the demand estimates to fill the list of sectorized estimates
                        policy_estimates.append( policy_demand_RAC[t-2014] * sector_prcnts.get(
                            (sector_List[sector], region_List[region], t ) ) )
                    # Interpolate within each sector to fill demand from 2015 to 2030 (same for all policies)
                    data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2015:2030,'demand'] = np.interp(
                        list(range(2015,2031)),projected_years, policy_estimates)

                    # apply percentages to 2014 demand estimate to fill in 2014 demand 
                    if region_List[region] == 'NA5' :
                        demand_est = na5_2014_cons_estimate # these estimates factor out foams and fire so the percentages make sense 
                    elif region_List[region] == 'A5' :
                        demand_est = a5_2014_cons_estimate # these estimates factor out foams and fire so the percentages make sense
                    # small assumption: assume 2014 percentage breakdowns are the same as 2015 (small change between years)
                    data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2014,'demand'] = demand_est * (
                        sector_prcnts[sector_List[sector],region_List[region],2015])
                
                if (sector_List[sector] != 'FOAMS') and (sector_List[sector] != 'FIRE') :
                    # Extrapolate the remaining demand percentage to the last year specified by each policy for each region 
                    percents_array = sector_percnts_arrs.get((sector_List[sector],region_List[region]))
                    percents_array = list(percents_array)
                    for t in range(2031,last_year + 1):
                        percents_array.append(linearExtrapolation(t-2,t-1,t,percents_array[t-2016],percents_array[t-2015]))
                    # Apply last year's percentage to the last year total demand estimate, and then interpolate between 2030 and last year 
                    data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2030:last_year,'demand'] = list(np.interp(
                        list(range(2030,last_year+1)),[2030, last_year],[ data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2030,'demand'], percents_array[len(
                            percents_array) - 1] * policy_demand[last_year-2014]]))
                elif sector_List[sector] == 'FOAMS' :
                    data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2014:last_year,'demand'] = [a*b for a,b in zip(policy_demand,foams_pcnt)] # 2014:2030
                elif sector_List[sector] == 'FIRE' :
                    data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[2014:last_year,'demand'] = [a*b for a,b in zip(policy_demand,fires_pcnt)] # 2014:2030
                # fill in the remaining demand with the last value, as a constant
                data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[last_year:2050,'demand'] = data_frames[scenario_List[scenario],region_List[region],sector_List[sector]].loc[last_year,'demand']
                


# interpolate and extrapolate percentages for 2015-2050 to apply to policy consumption figures 
# interpolate 2015-2030
#na5_interp_mac_prcntgs = np.interp(list(range(2015,2031)),projected_years,na5_mac_cons_prcntgs)
#a5_interp_mac_prcntgs = np.interp(list(range(2015,2031)),projected_years,a5_mac_cons_prcntgs)

#HFC-134a is phased out in new EU vehicles as of 2017, so demand decreases between 2015 and 2020 
#Phase out in new SAC equipment with HFC's with GWP's > 2500 by 2020 from EU

# Fill in initial size of bank [Mt CO2-eq] and recycling:
#policy_flows.loc[2014, 'bank'] = 5000

# Calculate stocks and flows year-by-year:
#ems_fac = 0.30 # emissions factor with range 0.15-0.3
##rec_fac = 0.2 # recycling factor (as a fraction of emissions factor)


#### Calculate emissions, recycling, destructions, banks, etc. using material flow calculations, emissions factors, and recycling factors 
#### Sum everything at the end to generate regional and global estimates of flows 

for scenario in range(0,len(scenario_List)):
    for var in range(0,len(vars_list)):
        # set each variable equal to 0 so the += works (doesn't work with NAN values)
        global_data_frames[(scenario_List[scenario])][vars_list[var]] = 0

    for region in range(0,len(region_List)):
        for var in range(0,len(vars_list)):
            # set each category (variable) equal to 0 in the empty data frames 
            summed_sectors_data_frames[(scenario_List[scenario],region_List[region])][vars_list[var]] = 0

        for sector in range(0,len(sector_List)):
            # Determine appropriate emissions factor           
            ems_fac = ems_factors_dict.get((sector_List[sector], region_List[region]))

            # Calculate 2014 Bank estimate using algebraic manipulation
            data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[2014,'bank'] = (
                (data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[2015,'bank'] / ( 
                    1 - ems_fac)) - data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[2014,'demand'])

            for t in range(2014,2051):
                if (sector_List[sector] == 'FOAMS') or (sector_List[sector] == 'FIRE') or ('policy' in scenario_List[scenario]):
                # Calculate Recovery as a fixed percentage of the bank using a servicing percentage (15%)
                    data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'recovery'] = (
                        servicing_pcnt) * (data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank']) 
                else:
                    # Calculate Recovery as equal to servicing demand in a given year 
                    data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'recovery'] = servc_demand_arrs.get(
                        (sector_List[sector],region_List[region]))[t-2014] 

                # Calculate a recycling rate (as a fraction of emissions) that corresponds to an amount of recycling that is 20% of servicing 
                    ## Upper bound of recycling scenario = 20% 
                rec_fac = ((0.20)*(data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'recovery']))/((
                    data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank'] + data_frames[(
                    scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand']) * (ems_fac))

                # Calculate Emissions 
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'emissions'] = (ems_fac) * (
                    1 - rec_fac)*(data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank'] 
                    + data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand'])

                # Calculate Recycling
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'recycling'] = (ems_fac) * (
                    rec_fac)*(data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank'] 
                    + data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand'])

                # Calculate next year's Bank
                if (t != 2050) and (t != 2014) :
                    data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t + 1,'bank'] = (
                        1 - ems_fac) * (data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank'] 
                        + data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand'])

                # Re-adjust Demand given servicing of the bank to calculate demand for new manufacturing
                #if (sector_List[sector] == 'FOAMS') or (sector_List[sector] == 'FIRE') or ('policy' in scenario_List[scenario]) :
                    ## using a 15% servicing percentage 
                    #data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand'] -= (
                    #    servicing_pcnt) * (data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'bank'])
                #else: 
                    ## Using an array of servicing demand from 2014:2050
                    #data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])].loc[t,'demand'] -= servc_demand_arrs.get( 
                       #(sector_List[sector],region_List[region]) )[t-2014] 

            # Calculate Destruction
            data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['destruction'] = (
                .9999) * (data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['recovery'] - 
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['recycling'])

            # Calculate Production
            data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['production'] = (
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['demand'] - 
                data_frames[(scenario_List[scenario],region_List[region],sector_List[sector])]['recycling'])

            for var in range(0,len(vars_list)):
                # Sum all of the flows for each sector and place into these data frames 
                summed_sectors_data_frames[(scenario_List[scenario],region_List[region])][vars_list[var]] += data_frames[(
                    scenario_List[scenario],region_List[region],sector_List[sector])][vars_list[var]]

        #sum the regions (NA5 and A5) to get global estimates 
        # do this for each variable (banks, demand, emissions, etc.)
        for var in range(0,len(vars_list)):
            global_data_frames[(scenario_List[scenario])][vars_list[var]] += summed_sectors_data_frames[(
                scenario_List[scenario],region_List[region])][vars_list[var]]


#for t in range(2014, 2050):
    # Calculate emissions:
 #   policy_flows.loc[t, 'emissions'] = ems_fac * (1 - rec_fac) * (
  #      policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    # Calculate recycling:
   # policy_flows.loc[t, 'recycling'] = ems_fac * rec_fac * (
    #    policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    # Calculate bank:
    #policy_flows.loc[t + 1, 'bank'] = (1 - ems_fac) * (
    #    policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    #flows.loc[t+1,'bank'] = flows.loc[t,'demand'] + flows.loc[t,'bank'] - 

#policy_flows['production'] = policy_flows['demand'] - policy_flows['recycling']

emissions = sum(policy_flows['emissions'])
recycling = sum(policy_flows['recycling'])

# Plot results:
matplotlib.style.use('ggplot')
matplotlib.rcParams.update({'font.size': 20})
matplotlib.rcParams.update({'legend.fontsize': 18})
matplotlib.rcParams.update({'figure.autolayout': True})
matplotlib.rcParams.update({'mathtext.default': 'regular'}) 

plot1 = pd.DataFrame(
    columns = ('Production','Recycling'), 
    index = range(2014, 2051)
    )
plot1['Production'] = policy_flows['production']
plot1['Recycling'] = policy_flows['recycling']

p1 = plot1.plot(kind = 'area')
plt.xlabel('Year')
plt.ylabel('Mt CO$_2$-eq')
plt.savefig('demand.pdf')

plot2 = pd.DataFrame(
    columns = ('Bank','Cumulative Emissions'), 
    index = range(2014, 2051)
    )
plot2['Bank'] = policy_flows['bank']
plot2['Cumulative Emissions'] = np.cumsum(policy_flows['emissions'])

p2 = plot2.plot()
plt.xlabel('Year')
plt.ylabel('Mt CO$_2$-eq')
plt.gca().set_ylim([0, 3e4])
plt.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))



plt.savefig('banks.pdf')
#bank_2014 = 0 #5000 #this is just approximated
#recycling_rate = 0.35
#delay = 10 #years

# Make the bank as something with the ages recorded.
#recycling = [0] * delay #[] #[0] * (2050 - 2014 + 1)

#for t in range(0, 2051 - 2014 - delay):
#    recycling.append(total_target[t] * recycling_rate)

#[c_i - r_i for c_i, r_i in zip(total_target, recycling)]

# For year 2014 to 2050:
# Take consumption and add 10% of it to the avialable bank


# Based on consumption scenarios, calcluate amount of additional production 
# required:

