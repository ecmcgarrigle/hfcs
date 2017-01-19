# Ethan McGarrigle and Morgan Edwards
# HFC Modeling

import unittest
import pandas as pd
import numpy as np
import main
import copy
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') #fixes framework problem with GUI
import matplotlib.pyplot as plt

# Create Data frames within a dictionary 


# Scenarios refer to the different ways NA5 and A5 demand is modeled
    # interp = Demand modeled by Linear interpolation 
    # exp_growth = Demand modeled by Exponential Growth

# Create sector list including R/AC and some smaller sectors  
sector_List = ['MAC', 'SAC', 'DOM', 'IND',
                'COM','TRANS', 'FOAMS', 'FIRE']

# Add 'policy_Islands' to the policy scenarios later
scenario_List = ['BAU', 'EU Proposal', 'NA Proposal',
                'India Proposal', 'Kigali Proposal','exp_growth']
# BAU = 'interp' scenario for now 
# Define the regions of the world we are iterating for 
    # NA5 = Non-Article 5; A5 = Article 5 countries 
region_List = ['NA5', 'A5']
# Define the list of variables (HFC flows) that we want to track
vars_list = ['demand', 'bank', 'emissions', 'recycling',
            'production', 'recovery', 'destruction']

HFC_List = ['HFC-134a', 'R-410A', 'R-404A + R-507', 'low-GWP', 'HC-600a', 'R-407C', 
    'R-22'] 

# Use TEAP 2016 placeholder values for now, use RTOC values from TEAP 2016
GWP_dictionary = {('HFC-134a') : 1360, ('R-410A') : 2100, ('R-404A + R-507') : 4000, 
    ('low-GWP') : 150, ('HC-600a') : 20, ('R-407C') : 1700, ('R-22') : 1780}
    # Note, R-22 is HCFC-22 

# Create lists of the HFC's used in each sector 

MAC_HFCs = ['HFC-134a', 'low-GWP']
SAC_HFCs = ['HFC-134a', 'R-410A', 'R-407C', 'low-GWP']
DOM_HFCs = ['HFC-134a', 'HC-600a']
COM_HFCs = ['HFC-134a', 'R-404A + R-507']
IND_HFCs = ['HFC-134a', 'R-404A + R-507', 'R-22', 'low-GWP']
TRANS_HFCs = ['HFC-134a', 'R-404A + R-507', 'low-GWP']

# Put those lists into a dictionary 
sector_HFC_lists = { ('MAC') : MAC_HFCs, ('SAC') : SAC_HFCs, ('DOM') : DOM_HFCs, 
    ('COM') : COM_HFCs, ('IND') : IND_HFCs, ('TRANS') : TRANS_HFCs }

# Construct a Dictionary with keys as such: { ('Scenario', 'Region (NA5 or A5)','Sector') : Data Frame}


# Data frames that contain the breakdown of each sector by HFC for a given country, region, scenario
# These will be summed for any given sector, within a region, within a scenario. 
HFC_data_frames = {}

# Data frames that contain sectorized breakdowns, each sector (for a given region) represents
# the total HFC usage in that sector for a given region within a given scenario. 

data_frames = {} 

# data frames that contain the total (sum of all sectors) for each scenario for a given region
summed_sectors_data_frames = {} 

# data frames that contain the total sum of all sectors and all regions (NA5 and A5) for each scenario
global_data_frames = {} 

# This script models HFC material flows from 2014 to 2050
first_year = 2014;
final_year = 2050;
years_range = range(first_year, final_year + 1)

# Create empty data frames 
for scenario in scenario_List:
    for region in region_List:
        for sector in sector_List:
            if sector != 'FOAMS' and sector != 'FIRE' :
                for HFC in sector_HFC_lists[sector]:
                    HFC_data_frames.update({(scenario, region, sector, HFC) : pd.DataFrame(
                        columns = vars_list, 
                        index = years_range)})
            data_frames.update({(scenario, region, sector) : pd.DataFrame(
                columns = vars_list, 
                index = years_range)})
        summed_sectors_data_frames.update({(scenario, region) : pd.DataFrame(
            columns = vars_list, 
            index = years_range)})
    global_data_frames.update({(scenario) : pd.DataFrame(
        columns = vars_list, 
        index = years_range)})


# Insert emissions factors here (Velders 2015si and TEAP 2016/TEAP 2015b)

ems_factors_dict = {('MAC','NA5') : 0.15175, ('MAC','A5'): 0.15, 
    ('SAC','NA5') : 0.07125, ('SAC','A5') : 0.0665, 
    ('IND','NA5') : 0.0875, ('IND','A5') : 0.11, 
    ('DOM','NA5') : 0.025, ('DOM','A5') : 0.025, 
    ('COM','NA5') : 0.13475, ('COM','A5') : 0.11, 
    ('TRANS','NA5') : 0.197, ('TRANS','A5') : 0.197, 
    ('FIRE','NA5') : 0.03, ('FIRE','A5') : 0.03, 
    ('FOAMS','NA5') : 0.05, ('FOAMS','A5') : 0.05}

# ems_factors_dict = data.ems_factors_dict
# Foams emissions factors vary between foams and will be applied to percentages of the foam 
# bank in the flows section

# Insert Sector-breakdown percentages of demand here: (TEAP 2014b) (tonnes)
    # The arrays inside represent percentages for the years [2015, 2020, 2025, 2030]
sector_percents = {('MAC', 'NA5') : [0.256, 0.226, 0.202, 0.197], 
    ('SAC', 'NA5') : [0.529, 0.585, 0.63, 0.634], 
    ('DOM', 'NA5') : [0.010, 0.009, 0.008, 0.008],
    ('COM', 'NA5') : [0.138, 0.115, 0.096, 0.097], 
    ('IND', 'NA5') : [0.059, 0.058, 0.056, 0.057], 
    ('TRANS', 'NA5') : [0.008, 0.007, 0.007, 0.007], 
    ('MAC', 'A5') : [0.187, 0.167, 0.148, 0.142],
    ('SAC', 'A5') : [0.469, 0.489, 0.476, 0.475], 
    ('DOM', 'A5') : [0.07, 0.056, 0.05, 0.048], 
    ('COM', 'A5') : [0.171, 0.193, 0.239, 0.252], 
    ('IND', 'A5') : [0.093, 0.086, 0.077, 0.074],
    ('TRANS', 'A5') : [0.01, 0.009, 0.01, 0.009]}


# Insert Bank 2015 breakdown percentages 
bank_prcnts = { ('MAC', 'NA5') : 0.325942 , ('MAC', 'A5') : 0.250457, 
    ('SAC', 'A5') : 0.258529, ('SAC', 'NA5') : 0.393038,
    ('COM', 'NA5') : 0.169199, ('COM', 'A5') : 0.285630, 
    ('TRANS', 'NA5') : 0.012194, ('TRANS', 'A5') : 0.003385, 
    ('IND', 'NA5') : 0.046744, ('IND', 'A5') : 0.025824, 
    ('DOM', 'NA5') : 0.052884, ('DOM', 'A5') : 0.176175 }


# Insert Servicing Demand Tables from TEAP 2016 
# tonnes(reported in tonnes from TEAP 2016)

# Create lists of each sector's HFC's, put those lists into a dictionary 
# Estimated total servicing demand for the given sector, region, HFC 

servc_demand_estimates = { ('MAC','NA5','HFC-134a') : [50737, 43852, 326888, 21214, 17267, 
    20017, 23206, 26902], ('MAC','NA5','low-GWP') : [0, 5939, 18744, 33587, 44856, 51999, 
    60282, 69884], ('SAC','NA5','HFC-134a') : [1350, 1422, 994, 226, 0, 0, 0 ,0], 
    ('SAC','NA5','R-410A') : [15599, 26146, 35074, 39820, 45894, 53204, 61677, 71501],
    ('SAC','NA5','R-407C') : [10489, 15381, 17999, 17051, 16321, 15649, 14870, 13968],
    ('SAC','NA5','low-GWP') : [0, 1561, 5081, 9161, 13892, 19376, 25733, 33104],
    ('DOM','NA5','HFC-134a') : [2, 2, 1, 1, 1, 1, 1, 2], 
    ('DOM','NA5','HC-600a') : [0, 0, 0, 1, 1, 0, 1, 0], 
    ('COM','NA5','HFC-134a') : [587, 1735, 1624, 1210, 977, 1133, 1312, 1522], 
    ('COM','NA5','R-404A + R-507') : [13065, 9645, 5691, 3595, 3055, 3542, 4106, 4760],
    ('COM','NA5','low-GWP') : [0, 1125, 4613, 8656, 12214, 14160, 16415, 19030],
    ('IND','NA5','HFC-134a') : [716, 730, 749, 722, 808, 864, 942, 1042],
    ('IND','NA5','R-404A + R-507')  : [323, 338, 281, 202, 174, 191, 177, 148],
    ('IND','NA5','R-22') : [675, 455, 306, 206, 139, 0, 0, 0],
    ('IND','NA5','low-GWP') : [5014, 6256, 7826, 9708, 11848, 14177, 16677, 19515],
    ('TRANS','NA5','HFC-134a') : [156, 160, 207, 292, 364, 423, 490, 568],
    ('TRANS', 'NA5','R-404A + R-507') : [802, 828, 702, 553, 450, 384, 307, 217],
    ('TRANS','NA5', 'low-GWP') : [0, 75, 225, 398, 600, 835, 1106, 1420], 
    ('MAC','A5','HFC-134a') : [18819, 25858, 32828, 41695, 53215, 67917, 86681, 110630], 
    ('MAC','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0], 
    ('SAC','A5','HFC-134a') : [728, 1633, 2777, 3858, 3695, 5214, 5573, 5990], 
    ('SAC','A5','R-410A') : [24084, 58068, 106142, 158220, 204672, 239792, 266159, 287886],
    ('SAC','A5','R-407C') : [2863, 58088, 104623, 172502, 251267, 326267, 391117, 435269],
    ('SAC','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('DOM','A5','HFC-134a') : [517, 723, 919, 1094, 1296, 1569, 1931, 2398], 
    ('DOM','A5','HC-600a') : [190, 401, 727, 1194, 1766, 2408, 3133, 3947], 
    ('COM','A5','HFC-134a') : [310, 630, 1036, 1467, 1894, 2359, 2941, 3664], 
    ('COM','A5','R-404A + R-507') : [10587, 24475, 45411, 71493, 102648, 136405, 172280, 214693],
    ('COM','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('IND','A5','HFC-134a') : [670, 1215, 2067, 3413, 5110, 7002, 9147, 11614],
    ('IND','A5','R-22') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('IND','A5','R-404A + R-507')  : [1519, 3734, 6997, 10777, 14682, 19116, 24221, 30159],
    ('IND','A5','low-GWP') : [19329, 23412, 28725, 35824, 43695, 52533, 63022, 75581],
    ('TRANS','A5','HFC-134a') : [524, 1034, 1644, 2123, 2575, 2997, 3525, 4330],
    ('TRANS', 'A5','R-404A + R-507') : [640, 1034, 1475, 1905, 2382, 3036, 3885, 4871],
    ('TRANS','A5', 'low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0]}


# Years for TEAP 2016 estimates (used for interpolation)
estimate_years_TEAP = [2014, 2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050] 




# NA5 are placeholder for now, consider using more accurate demand estimates (all from TEAP 2016)
# TEAP 2016 R/AC Demand estimates in [Mt CO2-eq]
# Each estimate corresponds to years as follows: [2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050]

RAC_demand_estimates = { ('MAC','NA5','HFC-134a') : [68359, 48425, 38118, 27509, 24564, 28477, 
    33013, 38271], ('MAC','NA5','low-GWP') : [0, 18218, 32849, 49939, 63812, 73975, 85758, 99417], 
    ('SAC','NA5','HFC-134a') : [4468, 1422, 994, 226, 0, 0, 0, 0], 
    ('SAC','NA5','R-410A') : [77354, 94230, 114001, 131319, 151966, 176170, 204229, 236758],
    ('SAC','NA5','R-407C') : [26802, 26172, 30349, 31368, 32918, 34890, 37176, 39826],
    ('SAC','NA5','low-GWP') : [0, 8770, 13597, 19034, 25337, 32644, 41115, 50935],
    ('DOM','NA5','HFC-134a') : [1451, 957, 954, 862, 999, 1158, 1342, 1556], 
    ('DOM','NA5','HC-600a') : [415, 545, 786, 1156, 1340, 1553, 1801, 2087], 
    ('COM','NA5','HFC-134a') : [2373, 2400, 2395, 2104, 2013, 2334, 2705, 3136], 
    ('COM','NA5','R-404A + R-507') : [16093, 11907, 7478, 5667, 5457, 6326, 7334, 8502],
    ('COM','NA5','low-GWP') : [0, 4373, 9213, 13988, 18396, 21326, 24723, 28661],
    ('IND','NA5','HFC-134a') : [1113, 1148, 1188, 1233, 1343, 1484, 1661, 1875],
    ('IND','NA5','R-404A + R-507')  : [743, 491, 378, 218, 193, 213, 203, 178],
    ('IND','NA5','R-22') : [675, 455, 306, 206, 139, 0, 0, 0],
    ('IND','NA5','low-GWP') : [8898, 11269, 13764, 16735, 19994, 23621, 27625, 32207],
    ('TRANS','NA5','HFC-134a') : [213, 302, 371, 483, 585, 679, 787, 912],
    ('TRANS', 'NA5','R-404A + R-507') : [1540, 917, 833, 705, 626, 588, 543, 491],
    ('TRANS','NA5', 'low-GWP') : [0, 557, 756, 1014, 1314, 1662, 2065, 2532], 
    ('MAC','A5','HFC-134a') : [51396, 66680, 84928, 108190, 138081, 176230, 224919, 287060], 
    ('MAC','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0], 
    ('SAC','A5','HFC-134a') : [2315, 4556, 5849, 7087, 8173, 8961, 9609, 10338], 
    ('SAC','A5','R-410A') : [106661, 192770, 284682, 364845, 427266, 479588, 524488, 566180],
    ('SAC','A5','R-407C') : [55278, 101216, 174433, 285500, 372998, 457406, 532391, 587361],
    ('SAC','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('DOM','A5','HFC-134a') : [13329, 15333, 18242, 21634, 26893, 33468, 41682, 51935], 
    ('DOM','A5','HC-600a') : [5747, 10141, 15684, 23446, 39496, 36965, 46197, 57613], 
    ('COM','A5','HFC-134a') : [5089, 9356, 11910, 15018, 18781, 23404, 29166, 36346], 
    ('COM','A5','R-404A + R-507') : [31391, 55505, 97823, 148283, 198343, 255658, 320891, 399889],
    ('COM','A5','low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('IND','A5','HFC-134a') : [1320, 2255, 3730, 6074, 8301, 10829, 13737, 17118],
    ('IND','A5','R-22') : [0, 0, 0, 0, 0, 0, 0, 0],
    ('IND','A5','R-404A + R-507')  : [3132, 6266, 10969, 15212, 20001, 25495, 31870, 39332],
    ('IND','A5','low-GWP') : [23571, 28991, 36291, 46469, 56461, 67842, 81380, 97596],
    ('TRANS','A5','HFC-134a') : [1075, 1982, 2608, 3104, 3798, 4521, 5424, 6697],
    ('TRANS', 'A5','R-404A + R-507') : [1881, 2192, 3135, 4195, 5235, 6592, 8316, 10393],
    ('TRANS','A5', 'low-GWP') : [0, 0, 0, 0, 0, 0, 0, 0]}




### Assumptions

# SAC NA5 ems factor is an equally weighted average of 4 groups that are NA5 countries 
# (Velders 2015si)
# sac_a5_ems_factor is an equally weighted average of 2 groups that make up A5 countries 
# (Velders 2015si)
# No emissions factor given for A5/developing countries, so for now, will assume they  
# are the same as NA5 as a place holder for Velders 2015si


# AER: Aerosols Sector (break up into medical and non-medical?)
    # TEAP 2009 updated supplement groups non-medical aerosols with solvents, but leaves 
    # medical aerosols as a separate group 
    # have not decided whether this model will do the same as of yet 

# FIRE: Fire Protection Sector

# FOAM: Foams Sector
# Foam estimates by TEAP 2009, supplement report only report HFC banks and foams globally 
# (no data for A5 and NA5 countries)


# AER: Aerosols Sector (break up into medical and non-medical?)
    # TEAP 2009 updated supplement groups non-medical aerosols with solvents, 
    # but leaves medical aerosols as a separate group. 
    # have not decided whether this model will do the same as of yet 



# Models

def linearExtrapolation(x1, x2, x3, y1, y2):
    # x1 and x2 are the x-coords of the known data points, x3 is the x-value of the unknown point
    # y1 and y2 are the y-coords of the known data points, y3 is the y-value of the unknown point
    y3 = y1 + (y2 - y1)*((x3 - x1)/(x2 - x1))
    return y3


def exponentialGrowth(x_0, r, t_0, t_f):
    # x_0 is the initial value of whatever you are modeling
    # r is the growth rate 
    # t_0 is the initial/starting time
    # t_f is the final/ending time
    xarray = []
    xarray.append(x_0)
    deltaT = t_f - t_0
    for t in range(1, deltaT + 1):
        x = x_0*(1 + r)**(t)
        xarray.append(x)
    return xarray


def calcEmissions(demand, bank, ems_fac, rec_fac):
    # Calculates emissions using a consumption estimate, a bank estimate (both from the 
    #   same year), along with an emissions factor and recycling factor (for that year)
    #   Model: e_t = (e_f) * (1 - r_f) * (b_t + c_t)

    e_t = (ems_fac) * (1 - rec_fac) * (demand + bank)
    return e_t # [Mt CO2-eq]

def calcRecycling(demand, bank, ems_fac, rec_fac):
    # Calculates recycling using a consumption estimate and a bank estimate from the same
    #   year, and an emissions and recycling factor/fraction. 
    #   Model: ems_fac * rec_fac * (b_t+ c_t)
    r_t = ems_fac * rec_fac * (bank + demand)
    return r_t

def calcNextBank(demand, bank, ems_fac):
    # Calculates the next year's bank based on the previous year's demand and bank and
    #   the emissions factor for that sector. The input demand and bank are for the previous
    #   year, and the output is for the current year. 
    #   Model: b_t+1 = (1 - e_f) * (b_t + c_t)
    b_t_plus_one = (1 - ems_fac) * (bank + demand)
    return b_t_plus_one

def calcRecovery(sector, bank, fixed_efficiency_frac, fixed_serv_frac, scenario, 
        servicing_demand, BAU_bank):
    # This function calculates the recovery for a given scenario in a given sector. Different
    # approaches are taken depending on whether the sector is non R/AC and whether the scenario
    # is a policy-based scenario. 

    # This function takes inputs: the sector, that current bank, a fixed efficiency percentage
    # hat represents recovery efficiency, usually very high (99.99%), a fixed servicing fraction, 
    # as percentage of the total bank for a sector, the current scenario, and the current BAU
    # bank (needed to derive a servicing percentage for policy scenarios).

    # This function returns the recovery. 

    # Calculate Recovery depending on the scenarios and sectors
    if (sector == 'FOAMS') or (sector == 'FIRE') :
        # If we are looking at foams and fire, calculate recovery as a fixed percentage
        #   of the total bank. 
        # Calculate Recovery as a fixed percentage of the bank using 
        #   a servicing percentage (15%), given the recovery efficiency. 
        recovery = (fixed_serv_frac * bank * fixed_efficiency_frac)
    elif ('Proposal' in scenario) :
        # Since we do not have servicing estimates in policy scenarios
        # Calculate a servicing percentage that is the ratio of the servicing amount
        # for a sector/region in the BAU to the total bank of the BAU. 
        # Defined as the portion of the total bank that goes to servicing 
        servicing_pcnt  = (servicing_demand) / (BAU_bank)

        # Naturally, apply that percentage to the bank to get recovery
        recovery = (servicing_pcnt) * bank

    else:
        # Calculate Recovery as equal to servicing demand in a given year 
        # if we are in an R/AC sector for a BAU scenario. 
        # These are the estimates provided by TEAP 2016 servicing demand schedule. 
        recovery = servicing_demand; 

    return recovery


# Interpolate servicing demand to create a full demand list from 2015-2050 


    # The following for-loops accomplish:
    # 1. Interpolates servicing demand from servicing demand (TEAP 2016) estimates
    #   for 2014-2015
    # 2. Interpolates sector percentages based on calculated percentages for TEAP data
    #   These percentages represent the fraction of total R/AC demand that is represented by a 
    #   usage sector (ex. MAC, SAC, etc.). NOTE: These percentages are defined as a fraction
    #   of total R/AC demand, so FIRE and FOAMS sectors are not inclued (purpose of the if statement) 

# A. Interpolate the servicing demand and sector fractions for each region and each R/AC
for region in region_List:
    for sector in sector_List:
        if (sector != 'FIRE') and (sector != 'FOAMS') :
            for HFC in sector_HFC_lists[(sector)]:
                # Get Servicing Demand from the corresponding dictionary entry
                estimates = servc_demand_estimates[(sector, region, HFC)]
                # Extrapolate a 2014 estimate and insert it in the beginning of the estimates array
                # Only do this if the 2015 estimate is non-zero, otherwise, set 2014 servicing demand
                #    equal to 0. 
                if (estimates[0] != 0):
                    estimate_2014 = linearExtrapolation(
                        2015, 2020, 2014, estimates[0], estimates[1])
                else:
                    estimate_2014 = 0
                estimates.insert(0, estimate_2014)
                # interpolate the demand after the list is filled 
                interp_servicing_demand = np.interp(
                    list(years_range), estimate_years_TEAP, estimates)
                # Store the new interpolated array into the dictionary (replace the old list)
                servc_demand_estimates[(sector, region, HFC)] = interp_servicing_demand

            # Sector Percents; Defined as the percentage of total demand that is 
            # from a given sector. i.e., what percentage of total demand is from MAC
            # These are used later in the policy scenarios. 
            # Now this part of the script interpolates the sector percentages from 2014 to 2030. 
            interp_sector_percents = []

            percent_estimates = sector_percents.get((sector, region))
            # Extrapolate a 2014 estimate and insert into the beginning of the estimates array 
            percent_estimates.insert(0, linearExtrapolation(
                2015, 2020, 2014, percent_estimates[0], percent_estimates[1]))
            # interpolate the percentages 
            interp_sector_percents = np.interp(list(range(first_year, 2031)),
                [2014, 2015, 2020, 2025, 2030], percent_estimates)
            # Add the percentages list to the dictionary to replace the current list  
            sector_percents[(sector, region)] = interp_sector_percents



# Reported Consumption from Excel Spreadsheet for A5 and NA5 Countries t: [1992,2014]  [tonnes]
na5_historical_consumption = [866, 11396, 24745, 32053, 34567, 41186, 52723, 69444, 93955, 
    98315, 116271, 136843, 155211, 175196, 189412, 208590, 227965, 250266, 269211, 323193, 
    362796, 375778, 376665]

a5_historical_consumption = [14, 319, 718, 1275, 1983, 2710, 3397, 4375, 5744, 10425, 15814, 
    20705, 26768, 33732, 55496, 74501, 87452, 104994, 131139, 178980, 203824, 240243, 278316]

# From TEAP 2009 updated supplement 
na5_RAC_bank_estimate = 1973 * (10**3) # tonnes
a5_RAC_bank_estimate = 722 * (10**3) # tonnes

# Calculate HFC breakdown fraction to be applied to the banks. Each fraction is defined as the 
# ratio of amount of HFC used per total HFC used in that sector for a given year. The goal is 
# to apply those breakdown fractions to 2015 R/AC estimates, so that we can get initial 
# bank estimates by HFC in each sector. 

# Create a dictionary to hold this data, the keys are the sector and HFC

HFC_sector_breakdown_fracs = {}

# Loop through each sector to generate a 2015 fraction for each sector and HFC
# fractions represent how much of a given HFC is used in a sector 

# Section A.2
for region in region_List:
    for sector in sector_List:
        if (sector != 'FOAMS') and (sector != 'FIRE'):
            # Initialize a sum that will represent the 2015 HFC burden for a sector 
            sector_HFCs = []
            total_HFC_in_sector = 0
            for HFC in sector_HFC_lists[sector]: 
                # Get the demand estimate for a given HFC; % The 0th element corresponds to 2015 
                HFC_demand_est = RAC_demand_estimates[(sector, region, HFC)][0] 
                sector_HFCs.append(HFC_demand_est)
            # When the loop finishes, rerun it, creating the fractions
            for HFC in range(0,len(sector_HFC_lists[sector])):
                # Calculate the fraction
                fraction = sector_HFCs[HFC] / (sum(sector_HFCs))
                # Put the fraction in the dictionary
                HFC_sector_breakdown_fracs.update({(
                    sector, region, sector_HFC_lists[(sector)][HFC]) : fraction})

# Now apply those fractions to the 2015 RAC bank estimates and fill in the HFC data frames 

# B. Estimate the 2015 banks of each scenario, for each region and sector. 
    # Calculates and fills in the 2015 estimates for banks for each sector based on 
    #   the 2015 sector percentages (fraction of total R/AC bank) and fractions of HFC's within
    #   a sector. 

for scenario in scenario_List:
    for region in region_List:
        if region == 'NA5' :
            bank_estimate = na5_RAC_bank_estimate
        elif region == 'A5' :
            bank_estimate = a5_RAC_bank_estimate
        for sector in sector_List:
            if (sector != 'FIRE') and (sector != 'FOAMS') :
                data_frames[(scenario, region, sector)].loc[2015,'bank'] = bank_estimate * (
                    bank_prcnts.get((sector, region))) 
                    # tonnes (TEAP 2009 updated supplement)
                for HFC in sector_HFC_lists[sector] : 
                    HFC_data_frames[(scenario, region, sector, HFC)].loc[2015,'bank'] = (
                        bank_estimate * HFC_sector_breakdown_fracs[(sector, region, HFC)])




# Based on checking these numbers from the TEAP 2009 updated supplement with the reports
#   it seems that these bank and emissions estimates are generally underestimating 
#   by about 100 Mt CO2-eq, so they will be semi-accurate placeholders for now. 


################### Exponential Growth Scenario #######################

# Note: Sector bank percentages from TEAP 2009 report are based on the modeled banks in tonnes, 
# no data was provided for modeled banks in tCO2-eq, so these percentages are prone to error 


######### Foams sector Modeling #######

# estimate foams refrigeration consumption/demand as a percentage of total consumption 
# TEAP 2014b reported foam demand estimates (NA5) (see page 40)
na5_foam_dem_estimates = [79.003, 86.049, 95.004, 104.892] # Mt CO2-eq 2015,2020,2025,2030
# Estimate an annual percentage growth rate for NA5 foam demand 

na5_foam_growth_rate = (1/15) * (na5_foam_dem_estimates[3] 
    - na5_foam_dem_estimates[0])/(na5_foam_dem_estimates[0]) 
# Annual, Calculated from TEAP 2014b reported HFC foams demand

# TEAP 2014b reported foam demand estimates (A5) (see page 40)
a5_foam_dem_estimates = [13.466, 21.035, 33.408, 41.633] # Mt CO2-eq; 2015,2020,2025,2030; 
    # HFC's only; a lot smaller because of increased use of HCFC in A5 countries
# Estimate an annual percentage growth rate for A5 foam demand
a5_foam_growth_rate = (1/15) * (a5_foam_dem_estimates[3] 
    - a5_foam_dem_estimates[0])/(a5_foam_dem_estimates[0]) 
    # Annual, large, given HCFC's are still phasing out of A5 countries 

# data_frames[('exp_growth','NA5','FOAMS')].loc[2015,'demand'] = 79.003
# MtCO2eq. (BAU TEAP scenario)
# data_frames[('exp_growth','A5','FOAMS')].loc[2015,'demand'] = 13.466 

# Model foams demand using exponential growth using the data above. 
# Extrapolate a 2014 value to feed into the exponential growth function as the first argument.
# NA5
data_frames[('exp_growth', 'NA5', 'FOAMS')].loc[2014, 'demand'] = linearExtrapolation(
    2015, 2020, 2014, na5_foam_dem_estimates[0], na5_foam_dem_estimates[1])

# data_frames[('exp_growth', 'NA5', 'FOAMS')]['demand'] = exponentialGrowth(
#     linearExtrapolation(2015, 2020, 2014, na5_foam_dem_estimates[0], na5_foam_dem_estimates[1]), 
#     na5_foam_growth_rate, 2014, 2050)
# A5
data_frames[('exp_growth', 'A5', 'FOAMS')].loc[2014, 'demand'] = linearExtrapolation(
    2015, 2020, 2014, a5_foam_dem_estimates[0], a5_foam_dem_estimates[1])


# No A5/NA5 breakdown provided for banks; estimate using percentages from demand: ~85% NA5; ~15% A5
    # These percentages are very likely to change as A5 grows; these are just for 2015 estimate 

global_foam_bank = 549877 # tonnes (TEAP 2009 updated supplement)
global_foam_demand_2015 = na5_foam_dem_estimates[0] + a5_foam_dem_estimates[0]
na5_foam_frac = na5_foam_dem_estimates[0]/global_foam_demand_2015
a5_foam_frac = a5_foam_dem_estimates[0]/global_foam_demand_2015

foam_na5_frac = data_frames[('exp_growth', 'NA5', 'FOAMS')].loc[2015, 'demand']

for scenario in scenario_List:
    data_frames[(scenario, 'NA5', 'FOAMS')].loc[2015, 'bank'] = na5_foam_frac * global_foam_bank 
        # [Mt CO2-eq]
    data_frames[(scenario, 'A5', 'FOAMS')].loc[2015, 'bank'] = a5_foam_frac * global_foam_bank 
        # [Mt CO2-eq]


# Aerosols (UNFINISHED/INCOMPLETE)

# estimate Aerosol consumption 

# extrapolate aerosol consumption using exponential growth with TEAP 2009 updated supplement 
# growth rates

# Estimate Aerosol bank 

# See Velders 2015si for emissions factors

# Velders 2015si breaks up foams emissions factors into open cell foams, 
#   extruded polystyrene foams (XPS), and Polyurethane foams (PUR)

#foams_emissions_fac = 0.026 # global estimate; the average of 6 ratios of 
# TEAP modeled emissions to banks, averaged over the years 2015-2020 (one ratio for each year)


####### Fire Exstinguishing Systems #######

# Estimates of HFC-fire bank 

global_fire_bank_2015 = 63338 # tonnes; TEAP 2009 Updated Supplement

# Calculate the fraction of the total bank that is represented by NA5 and A5
# Using data from 2015 HFC bank data for the fire protection sector.
# Data from TEAP 2009 Updated Supplement 

na5_fire_2015_bank = 41723 # [tonnes]
na5_fire_2014_bank = 39023 # [tonnes]
a5_fire_2015_bank = 21616 # [Mt CO2-eq] % tonnes? (may have forgot to change the unit)
a5_fire_2014_bank = 20213 # [Mt CO2-eq] # tonnes? (may have forgot to change the unit)

# Fill all of the scenarios' 2015 and 2014 spots
for scenario in scenario_List:
    # data_frames[(scenario, 'NA5', 'FIRE')].loc[2015, 'bank'] =  147.996 # [Mt CO2-eq]
    data_frames[(scenario, 'NA5', 'FIRE')].loc[2015, 'bank'] = na5_fire_2015_bank # [tonnes]
    # data_frames[(scenario, 'A5', 'FIRE')].loc[2015, 'bank'] = 63.945 # [Mt CO2-eq]
    data_frames[(scenario, 'A5', 'FIRE')].loc[2015, 'bank'] = a5_fire_2015_bank # [tonnes]


# Fire growth rate calculated 2015-2020 change in the bank (TEAP 2009 updated supplement)
a5_fire_growth_rate = 0.07757
na5_fire_growth_rate = 0.07705

# estimate Fire exstinguishing system HFC consumption using a bank calculation
# See Velders 2015si for Fire-bank emissions factors
fire_ems_factor = 0.03 # all regions

# 2014 Demand estimates 
na5_fire_cons_estimate = (((na5_fire_2015_bank)/(1 - fire_ems_factor)) - na5_fire_2014_bank)  
# (2015 bank / ems factor) - 2014 bank = 2014 consumption
    # = 14.11219588 Mt CO2-eq
a5_fire_cons_estimate = (a5_fire_2015_bank/(1 - fire_ems_factor)) - a5_fire_2014_bank
    # = 31.544 # Mt CO2-eq

# Fill the data frame 2014 spot for demand 
data_frames[('exp_growth', 'NA5', 'FIRE')].loc[2014, 'demand'] = na5_fire_cons_estimate
data_frames[('exp_growth', 'A5', 'FIRE')].loc[2014, 'demand'] = a5_fire_cons_estimate



# Consider adding SOLVENTS to the sectors 


# Extrapolate 2015 Consumption for NA5 and A5 countries as a total of the 6 R/AC sectors 

# Generate a consumption estimate (2014) of R/AC consumption by subtracting the 
#   non R/AC sectors from the total HFC consumption.  
na5_2014_RAC_cons_estimate = na5_historical_consumption[22] - (
    data_frames[('exp_growth', 'NA5','FOAMS')].loc[2014, 'demand'] 
    + data_frames[('exp_growth', 'NA5', 'FIRE')].loc[2014,'demand'])

a5_2014_RAC_cons_estimate = a5_historical_consumption[22] - (
    data_frames[('exp_growth', 'A5', 'FOAMS')].loc[2014, 'demand'] 
    + data_frames[('exp_growth', 'A5', 'FIRE')].loc[2014, 'demand'])

na5_2015_cons_estimate = linearExtrapolation(2013, 2014, 2015, 
    na5_historical_consumption[21], na5_historical_consumption[22])
a5_2015_cons_estimate = linearExtrapolation(2013, 2014, 2015, 
    a5_historical_consumption[21], a5_historical_consumption[22])

# Now, use these R/AC total consumption estimates with the sector fractions/percents
#  to model the breakdown of sectors in consumption for each region. 

# C. Fill 2014 demand estimates by running a loop for each sector that applies the percentage
# breakdowns for the sectors to the total R/AC consumption estimates, for each region.
for region in region_List :
    for sector in sector_List :
        # Sector percentages only defined for R/AC sectors: 
        if sector != 'FOAMS' and sector != 'FIRE' :
            if region == 'NA5' :
                demand_2014_estimate = na5_2014_RAC_cons_estimate
            elif region == 'A5' : 
                demand_2014_estimate = a5_2014_RAC_cons_estimate

            # Apply the sector fraction to the total estimate for each region. 
            data_frames[('exp_growth', region, sector)].loc[2014, 'demand'] = (
                sector_percents.get((sector, region))[1] * demand_2014_estimate)
            # Estimates are in [tonnes]

# Now that the 2014 estimates are filled in, we can set up growth rate and year parameters and 
# then successfully run the exponential model. 

# Create a dictionary to contain exponential growth parameters.
# This dictionary will be used with the exponential growth model to model the exponential growth
#   secnario. The dictionary "keys" will be the sector an region, and the corresponding value will
#   be an array of the form: [growth rate, first_year, last_year, growth_rate, first_year, ...
#   last_year, ... until you are out of exponential growth parameter data for ranges of years]


exp_growth_params = {('MAC', 'NA5') : [0.0054, 2014, 2020, 0.03, 2020, 2050], 
    ('MAC', 'A5') : [0.05, 2014, 2050], ('SAC', 'NA5') : [0.012, 2014, 2020, 0.03, 2020, 2050], 
    ('SAC', 'A5') : [0.01, 2014, 2050], ('DOM', 'NA5') : [0.016, 2014, 2020, 0.03, 2020, 2050], 
    ('DOM', 'A5') : [0.058, 2014, 2050], ('COM', 'NA5') : [0.021, 2014, 2020, 0.03, 2020, 2050],
    ('COM', 'A5') : [0.018, 2014, 2020, 0.045, 2020, 2050], 
    ('IND', 'NA5') : [0.051, 2014, 2020, 0.04, 2020, 2050], 
    ('IND', 'A5') : [0.018, 2014, 2020, 0.037, 2020, 2050], 
    ('TRANS', 'NA5') : [0.02, 2014, 2020, 0.03, 2020, 2050], 
    ('TRANS', 'A5') : [0.018, 2014, 2020, 0.045, 2020, 2050], 
    ('FIRE', 'NA5') : [na5_fire_growth_rate, 2014, 2050], 
    ('FIRE', 'A5') : [a5_fire_growth_rate, 2014, 2050], 
    ('FOAMS', 'NA5') : [na5_foam_growth_rate, 2014, 2050], 
    ('FOAMS', 'A5') : [a5_foam_growth_rate, 2014, 2050]}


# Exponential Modeling 

# D. Run these for loops to fill the exp_growth scenario with the data by using the exponential
# growth model using parameter data for each sector and region for different ranges of years. 
for sector in sector_List :
    for region in region_List : 
        # Simplify the data frame syntax to a current data frame 
        current_data_frame = data_frames[('exp_growth', region, sector)]

        # Get the parameter data for this sector/region. 
        param_data = exp_growth_params.get((sector, region))

        # Calculate the number of growth periods for the given sector/region 
        num_periods = int(len(param_data))/3
        # Loop through each period and call the exponential growth function. Insert the 
        #   demand into the corresponding years of the data frame. 
        for period in list(range(1, int(num_periods) + 1)):
            # Each period has a growth rate and first and last year from the parameter data
            t_0 = param_data[3 * (period) - 2] # First year is always in slot 1, 4, 7, etc.
            t_f = param_data[3 * (period) - 1] # Last year always in slot 2, 5, 8, etc. 
            growth_rate =  param_data[3 * (period) - 3] # growth rate always in slot [0, 3, 6,etc]
            initial_val = current_data_frame.loc[t_0, 'demand']

            # Fill the data frame's demand for this period using exponential growth
            current_data_frame.loc[t_0:t_f, 'demand'] = exponentialGrowth(initial_val, 
                growth_rate, t_0, t_f)
            # Set the data frame equal to the current data frame for that period 
            demand = current_data_frame.loc[t_0:t_f, 'demand'] 
            data_frames[('exp_growth', region, sector)].loc[t_0:t_f, 'demand'] = demand

            # For foams and fire: 
            # Set the BAU data frame equal to the exponential growth data frame because of lack 
            #   of data for the interpolation BAU case. 
            if (sector == 'FOAMS') or (sector == 'FIRE') : 
                data_frames[('BAU', region, sector)]['demand'] = demand


######## Scenario 2 (linear interpolation of 5-year TEAP demand estimates) - TEAP 2016


# E. Interpolate and fill BAU data frames with interpolated demand for R/AC Sectors
# Run these for loops to go through the data and fill in the estimates. 
for sector in sector_List :
    if (sector != 'FIRE' and sector != 'FOAMS') : 
        for region in region_List :
            for HFC in sector_HFC_lists[(sector)]:
                # get dictionary of estimates from 2015 to 2050 from TEAP 2016 data
                demand_estimates = RAC_demand_estimates[(sector, region, HFC)]
                # Extrapolate a value for 2014 demand using 2015 and 2020 demand estimates.
                    # only if the 2015 estimate is non-zero should this occur
                if (demand_estimates[0] != 0): 
                    demand_2014_estimate = linearExtrapolation(
                        2015, 2020, 2014, demand_estimates[0], demand_estimates[1])
                else:
                    demand_2014_estimate = 0
                # Insert the 2014 estimate with the rest of the estimates 
                demand_estimates.insert(0, demand_2014_estimate)
                # Interpolate the demand 
                interpolated_demand = np.interp(
                    list(years_range), estimate_years_TEAP, demand_estimates)
                # Insert the interpolated demand into the dataframe 
                HFC_data_frames[('BAU', region, sector, HFC)]['demand'] = interpolated_demand
                # data_frames[('BAU', region, sector)]['demand'] = interpolated_demand



# F. sum the demand of each sector for each region, needed to model the demand from india proposal 
# Sum the HFC demand to get the demand for each sector 

for scenario in scenario_List:
    if (scenario == 'BAU') or (scenario == 'exp_growth') :
        for region in region_List:
            summed_sectors_data_frames[scenario, region]['demand'] = 0 
            # must set equal to 0, otherwise "+=" doesnt work
            for sector in sector_List:
                if (sector != 'FOAMS') and (sector != 'FIRE') : 
                    data_frames[(scenario, region, sector)]['demand'] = 0
                    for HFC in sector_HFC_lists[(sector)]: 
                        # Sum across all HFC's per sector to generate a sector estimate of total HFC 
                        # demand. 
                        data_frames[(scenario, region, sector)]['demand'] += HFC_data_frames[
                            (scenario, region, sector, HFC)]['demand']

                    summed_sectors_data_frames[scenario, region]['demand'] += data_frames[
                            (scenario, region, sector)]['demand']


############# Policy Scenarios ###############

year = list(years_range)


# Create a dictionary to store the "last years" of each policy
    # The last year is the last year where the demand estimates change
    # they then stay constant with that last year's value until 2050 
last_years_dict = {}

# Fill the dictionary with each policy's last year for each region
last_years_dict.update({
    ('NA5','NA Proposal') : 2036, ('A5','NA Proposal') : 2046,
    ('NA5','EU Proposal') : 2034, ('A5','EU Proposal') : 2034,
    ('NA5','India Proposal') : 2035, ('A5','India Proposal') : 2050,
    ('NA5','Kigali Proposal') : 2036, ('A5', 'Kigali Proposal') : 2045
    })



# Kigali Amendemnt 


# Generate HFC demand fractions that represent the demanded amount of a specific HFC within a given
# sector. We need ones that represent the burden in Mt CO2-eq (the ones for tonnes are already
# calculated.)

# Multiply the above data (RAC demand estimates for HFC usage in each sector) by the GWP
#   to get Mt CO2-eq estimates, and then divide that by the total Mt CO2-eq HFC usage in 
#   that sector.

# Create an empty dictionary to hold the HFC fractions for a given region and sector and HFC
HFC_fracs_dict_CO2_eq = {}

# Section G.2
for region in region_List : 
    for sector in sector_List : 
        if (sector != 'FIRE') and (sector != 'FOAMS') :
            # Get the total HFC demand (Mt CO2-eq) in that sector for the region from main.py
            total_demand_CO2_eq = main.data_frames[('BAU', region, sector)]['demand']
            # Loop through dfferent HFC's to generate the HFC fractions 
            for HFC in sector_HFC_lists[(sector)]: 
                # Get HFC demand (For each HFC) in tonnes 
                HFC_demand_tonnes = HFC_data_frames[('BAU', region, sector, HFC)]['demand']
                # Get the GWP 
                GWP = GWP_dictionary[(HFC)]
                # Multiply by the GWP to convert to Mt CO2-eq
                HFC_demand_CO2_eq = [(GWP * x) * (10**(-6)) for x in HFC_demand_tonnes] 
                # Now in Mt CO2-eq 
                # Generate the fraction by taking the ratio of the given HFC demand to the 
                #   total sector demand. 
                HFC_fractions_CO2_eq = [x / y for x,y in zip(
                    HFC_demand_CO2_eq, total_demand_CO2_eq)]
                # Put these fractions in the dictionary to be used for later 
                HFC_fracs_dict_CO2_eq[(region, sector, HFC)] = HFC_fractions_CO2_eq
                # Fractions represent 2014 - 2050 (For each index) fraction of MtCO2-eq 
                #   in a sector for an HFC 


# Section G.3
# Apply the sector percentages and HFC fractions to the Mt CO2-eq targets, 
#   imported from main.py (Mt CO2-eq).
# Create a dictionary of specific HFC usage for a given sector  
HFC_estimates = {}
for scenario in scenario_List : 
    if 'Kigali Proposal' == scenario :
        for region in region_List : 
            last_year = last_years_dict[(region, scenario)]
            # Create an array of HFC demand usage for a sector, with the indices representing
            #   years from 2014 to 2030. 
            sector_estimates = []
            if (region == 'NA5') : 
                policy_targets = main.na5_Kigali_policy
            elif (region == 'A5') : 
                policy_targets = main.a5_Kigali_policy
            for sector in sector_List : 
                if (sector != 'FIRE') and (sector != 'FOAMS') : 
                    for HFC in sector_HFC_lists[(sector)] : 
                        HFC_estimates.update({(region, sector, HFC) : []})  
                        for t in range(2014, 2031):
                            # Get the sector percentage (for MtCO2-eq)
                            sector_percent = main.sector_percents[(sector, region)][t - 2014]
                            # Apply the fraction to generate an estimate of the sector total HFC 
                            #   usage 
                            sector_estimate = sector_percent * policy_targets[t - 2014]
                            # Add this to a list 
                            sector_estimates.append(sector_estimate)
                            # Apply the HFC CO2-eq fractions to these estimates to generate specific
                            #   HFC usage for a sector. 

                            # Get the appropriate fraction from the dictionary 
                            HFC_fraction = HFC_fracs_dict_CO2_eq[(region, sector, HFC)][t - 2014]
                            # Apply the fraction 
                            HFC_estimate = HFC_fraction * sector_estimates[t - 2014]
                            # Create the list in a dictionary 

                            # Add the estimate to the list (Mt CO2-eq)
                            HFC_estimates[(region, sector, HFC)].append(HFC_estimate)

                    for HFC in sector_HFC_lists[(sector)] :     
                        # Extrapolate the remaining HFC estimates (2031 - last_year)
                        for t in range(2031, last_year + 1): 
                            HFC_estimates[(region, sector, HFC)].append(linearExtrapolation(
                                t - 2, t - 1, t, 
                                HFC_estimates[(region, sector, HFC)][t - 2016], 
                                HFC_estimates[(region, sector, HFC)][t - 2015]))
                        # fill in the remaining demand with the last value, as a constant
                        for t in range(last_year + 1, 2051) : 
                            HFC_estimates[(region, sector, HFC)].append(
                                HFC_estimates[(region, sector, HFC)][last_year - 2015])

                    # After HFC Mt CO2-eq estimates are generated from 2014 - 2050, convert back to 
                    # tonnes using the GWP 
                    for HFC in sector_HFC_lists[(sector)] : 
                        GWP = GWP_dictionary[(HFC)]
                        # Convert back to tonnes by dividing by the GWP for the HFC
                        HFC_estimates_tonnes = [
                            (x * (10**(6)))/ GWP for x in HFC_estimates[(region, sector, HFC)]]
                        # Put these estimates in the dictionary for the proposal 
                        HFC_data_frames[('Kigali Proposal', region, sector, HFC)]['demand'] = (
                            HFC_estimates_tonnes)




# 2024 freeze for Article 5 parties (developing countries and china) 
# reduction in 2019 for most NOn-ARticle 5 countries 
    # Reduce by 10% by 2019, and 85% by 2036 based on consumption and production levels in 2011-2013. 
        # Non-A5 baseline, avg. of 2011-2013 consumption? 
    # Article 5, freeze in 2024, and reduction of 80% by 2035, based on a baseline from consumption 
    # levels from 2020-2022. 




projected_years = [2015, 2020, 2025, 2030]


### Sectorized breakdown for each policy scenario 

# Using the sectorized percentages in the dictionary, breakdown demand by sector 
# by applying percentages in appropriate years.

policies_dict = {}

     
scenario_List.remove('exp_growth') 
scenario_List.remove('India Proposal')
scenario_List.remove('NA Proposal')
scenario_List.remove('EU Proposal')

rec_rates = [0, 0.20]
# rec_rate = 0.20

# Assuming a 15% annual servicing of the bank from a TEAP report (2015?)

fixed_serv_frac = 0.15
fixed_efficiency_frac = 0.9999       
    #  Sum everything at the end to generate regional and global estimates of flows.
def calculate_HFC_flows(scenario_List, region_List, vars_list, 
        old_frames, HFC_data_frames, ems_factors_dict, sector_List, servc_demand_estimates, 
            fixed_serv_frac, fixed_efficiency_frac, recycling_rate, years_range) :

    unfilled_frames = HFC_data_frames.copy()
    sectors_data = {}
    summed_sectors_data = {}
    global_data = {}
    rec_rate = recycling_rate

    for scenario in scenario_List:
        global_data.update({(scenario) : pd.DataFrame(
                columns = vars_list, 
                index = years_range)})

        for region in region_List:
            summed_sectors_data.update({(scenario, region) : pd.DataFrame(
                columns = vars_list, 
                index = years_range)})

            for sector in sector_List : 
                sectors_data.update({(scenario, region ,sector) : pd.DataFrame(
                    columns = vars_list,
                    index = years_range)})

    for scenario in scenario_List:
        for variable in vars_list:
            # set each variable equal to 0 so the += works (doesn't work with NaN values)
            global_data[(scenario)][variable] = 0

        for region in region_List:
            for variable in vars_list:
                # set each category (variable) equal to 0 in the empty data frames 
                summed_sectors_data[(scenario, region)][variable] = 0

            for sector in sector_List:
                # Determine appropriate emissions factor 
                for variable in vars_list: 
                    sectors_data[(scenario, region, sector)][variable] = 0   

                ems_fac = ems_factors_dict.get((sector, region))
                if sector != 'FOAMS' and sector != 'FIRE' :
                    for HFC in sector_HFC_lists[(sector)] : 
                        # Store the current data frame into a variable for easier readability
                        current_data_frame = HFC_data_frames[(scenario, region, sector, HFC)]
                        
                        # Calculate 2014 Bank estimate using algebraic manipulation
                        current_data_frame.loc[2014, 'bank'] = (
                            (current_data_frame.loc[2015, 'bank'] / (1 - ems_fac)) 
                            - current_data_frame.loc[2014, 'demand'])

                        for t in range(2014,2051):
                            # For every year, store the variables needed for calculation
                            bank = current_data_frame.loc[t,'bank']
                            demand = current_data_frame.loc[t,'demand']
                            # Get the servicing demand for a given R/AC sector in year "t"
                            if sector != 'FOAMS' and sector != 'FIRE' :
                                servicing_demand = servc_demand_estimates.get(
                                    (sector, region, HFC))[t - 2014]

                            # Get the current year's BAU bank value, used in the recovery function. 
                            BAU_bank = HFC_data_frames[('BAU', region, sector, HFC)].loc[t, 'bank']
                            if BAU_bank != 0 :
                                current_data_frame.loc[t, 'recovery'] = calcRecovery(sector, bank, 
                                fixed_efficiency_frac, fixed_serv_frac, 
                                scenario, servicing_demand, BAU_bank)
                            else: 
                                current_data_frame.loc[t, 'recovery'] = 0

                        # Calculate Recovery depending on which scenarios and sectors we're in
                        

                        # Calculate a recycling rate (as a fraction of emissions) that corresponds to
                        #   an amount of recycling that is 20% of servicing. 
                            # Upper bound of recycling scenario = 20% 
                            if ((bank + demand) != 0):
                                rec_fac = (rec_rate * (current_data_frame.loc[t, 'recovery'])
                                    ) / ((bank + demand) * (ems_fac))   
                            else: # Will divide by zero 
                                rec_fac = 0          

                            # Calculate Emissions and store emissions in the data frame    
                            emissions = calcEmissions(demand, bank, ems_fac, rec_fac)         
                            current_data_frame.loc[t, 'emissions'] = emissions

                            # Calculate Recycling
                            recycling = calcRecycling(demand, bank, ems_fac, rec_fac)
                            current_data_frame.loc[t,'recycling'] = recycling

                            # Calculate next year's Bank (if not at an time bounds)
                            if (t != 2050) and (t != 2014) :
                                next_bank = calcNextBank(demand, bank, ems_fac)
                                current_data_frame.loc[t + 1,'bank'] = next_bank

                        # Calculate Destruction
                        current_data_frame['destruction'] = (current_data_frame['recovery'] 
                            - current_data_frame['recycling'])

                        # Calculate Production
                        current_data_frame['production'] = (current_data_frame['demand'] 
                            - current_data_frame['recycling'])

                        # Convert to Mt CO2-eq if desired 
                        #current_data_frame.loc[2014:2050] = current_data_frame.loc[2014:2050] * (
                            #GWP_dictionary[(HFC)] * (10**(-6))) # Mt CO2-eq

                        HFC_data_frames[(scenario, region, sector, HFC)] = current_data_frame

                        for variable in vars_list: 
                            sectors_data[(scenario, region, sector)][variable] += (
                                current_data_frame[variable])

                    for variable in vars_list:
                        # Sum all of the flows for each sector and place into these data frames 
                        summed_sectors_data[(scenario, region)][variable] += (
                            sectors_data[(scenario, region, sector)][variable])                    

            # sum the regions (NA5 and A5) to get global estimates 
            # for each variable (banks, demand, emissions, etc.)
            for variable in vars_list :
                global_data[(scenario)][variable] += summed_sectors_data[(
                    scenario, region)][variable]



    # Set the correct dictionary entry equal to the current data frame
    HFC_data_frames_dict[(rec_rate)] = HFC_data_frames
    data_frame_dict[(rec_rate)] = sectors_data
    summed_d_frames_dict[(rec_rate)] = summed_sectors_data
    global_d_frames_dict[(rec_rate)] = global_data
    data_frames = unfilled_frames.copy()
    # print(data_frame_dict[(rec_rate)][('BAU', 'A5', 'SAC')])





# # Create a dictionary that will store the data frames for different recycling rates
# # Initialize with the same data frame for both reycling rates. 
HFC_data_frames_dict = {rec_rates[0] : {}, rec_rates[1] : {}}
data_frame_dict = {rec_rates[0] : {}, rec_rates[1] : {}}
summed_d_frames_dict = {rec_rates[0] : {}, 
    rec_rates[1] : {}}
global_d_frames_dict = {rec_rates[0] : {}, 
    rec_rates[1] : {}}

# # Use the function for all the recycling rates and fill the dictionaries for each recycling
# #   rate. 

# # Make a copy of the unfilled data frames (i.e., filled with just demand)
old_frames = copy.deepcopy(HFC_data_frames)       

for recycling_rate in rec_rates :
    # Run the function for a given recycling rate
    # The following if statement is a temporary fix, generates correct results incorrectly. 
    
    # Old_frames are not supposed to change, they are supposed to be an unchanging input to 
    # the function; however, all the data frames come out as they are supposed to. 
    if recycling_rate == 0.20 :
        HFC_data_frames = old_frames

    calculate_HFC_flows(scenario_List, region_List, vars_list, 
        old_frames, HFC_data_frames, ems_factors_dict, sector_List, servc_demand_estimates, 
            fixed_serv_frac, fixed_efficiency_frac, recycling_rate, years_range)


def calc_global_cum_mitigation(global_d_frames_dict, scenarios, rec_rates) : 

    # This function calculates the global mitigation benefits occurring from the difference in 
    # recycling rates. This is represented by the difference in emissions or production 
    # or recycling between the two scenarios (everything with max recycling and everything
    # with lower bound recycling). This function returns a dictionary with amounts of mitigation 
    # achieved across the different scenarios, through recycling. 
    # Each cumulative mitigation represents cumulative emissions from 2014 to 2050. The 
    # calculated mitigation represents cumulative emissions mitigated by 2050 starting in 2014. 

    lower_bound_rec_rate = rec_rates[0]
    upper_bound_rec_rate = rec_rates[1]

    global_mitigation = {}
 
    for scenario in scenarios : 
        # Initialize each mitigation value to 0 for each scenario.
        global_mitigation.update({(scenario) : 0})

        # Calculate cumulative emissions for each scenario: 

        lower_bound_emissions = global_d_frames_dict[(
            upper_bound_rec_rate)][(scenario)]['emissions']
        lower_bound_cumulative_emissions = sum(lower_bound_emissions)

        upper_bound_emissions = global_d_frames_dict[(
            lower_bound_rec_rate)][(scenario)]['emissions']
        upper_bound_cumulative_emissions = sum(upper_bound_emissions)

        # Calculate global mitigation by subtracting the two recycling scenarios.
        cumulative_mitigation = upper_bound_cumulative_emissions - lower_bound_cumulative_emissions
        global_mitigation[(scenario)] = cumulative_mitigation 

    return global_mitigation

global_cumulative_mitigation = calc_global_cum_mitigation(global_d_frames_dict, 
     scenario_List, rec_rates)



def calc_region_cum_mitigation(summed_d_frames_dict, scenarios, regions, rec_rates) :
    
    # This function calculates the mitigation benefits for each region (NA5 and A5) from the
    # difference in upper and lower bound recycling rates. This is represented by the difference
    # in emissions, production, or recycling with different reycling rates. 
    # This function returns a dictionary with cumulative mitigation values (2014 - 2050) for 
    # each scenario and region for those scenarios. 

    regional_cumulative_mitigation = {}

    lower_bound_rec_rate = rec_rates[0]
    upper_bound_rec_rate = rec_rates[1]

    for scenario in scenarios : 
        for region in regions : 
            # Initialize each mitigation value to 0 for each scenario/region
            regional_cumulative_mitigation.update({(scenario, region) : 0})

            # Calculate cumulative emissions for each (lower and upper bound) recycling scenario
            lower_bound_emissions = summed_d_frames_dict[(
                upper_bound_rec_rate)][(scenario, region)]['emissions']
            lower_bound_cumulative_emissions = sum(lower_bound_emissions)

            upper_bound_emissions = summed_d_frames_dict[(
                lower_bound_rec_rate)][(scenario, region)]['emissions']
            upper_bound_cumulative_emissions = sum(upper_bound_emissions)

            # Calculate global mitigation by subtracting the two recycling scenarios.
            cumulative_mitigation = upper_bound_cumulative_emissions - lower_bound_cumulative_emissions
            regional_cumulative_mitigation[(scenario, region)] = cumulative_mitigation

    return regional_cumulative_mitigation

regional_cumulative_mitigation = calc_region_cum_mitigation(summed_d_frames_dict, 
     scenario_List, region_List, rec_rates)



def calc_sector_cum_mitigation(data_frame_dict, scenarios, regions, sectors, rec_rates) : 

    # This function calculates the mitigation benefits for each sector, in each region and
    # scenario, for each recycling scenario (lower and upper bound recycling rates). This is 
    # represented by the difference in emissions, production, or recycling, which are cumulative
    # amounts from 2014 - 2050. 

    sector_cumulative_mitigation = {}

    lower_bound_rec_rate = rec_rates[0]
    upper_bound_rec_rate = rec_rates[1]

    for scenario in scenarios : 
        for region in regions : 
            for sector in sectors : 
                # Initialize each mitigaiton value to 0 
                sector_cumulative_mitigation.update({(scenario, region, sector) : 0 })

                # Calculate cumulative emissions for upper and lower bound recycling scenarios
                lower_bound_emissions = data_frame_dict[(
                    upper_bound_rec_rate)][(scenario, region, sector)]['emissions']
                low_bound_cumulative_emissions = sum(lower_bound_emissions)

                upper_bound_emissions = data_frame_dict[(
                    lower_bound_rec_rate)][(scenario, region, sector)]['emissions']
                up_bound_cumulative_emissions = sum(upper_bound_emissions)

                # Calculate cumulative mitigation by subtracting the two cumulative emissions
                cumul_mitigation = up_bound_cumulative_emissions - low_bound_cumulative_emissions
                sector_cumulative_mitigation[(scenario, region, sector)] = cumul_mitigation

    return sector_cumulative_mitigation


sector_cumulative_mitigation = calc_sector_cum_mitigation(data_frame_dict, scenario_List, 
     region_List, sector_List, rec_rates)




# Plot results:
matplotlib.style.use('ggplot')
matplotlib.rcParams.update({'font.size': 16}) #10 
matplotlib.rcParams.update({'legend.fontsize': 14}) #9
matplotlib.rcParams.update({'figure.autolayout': True})
matplotlib.rcParams.update({'mathtext.default': 'regular'}) 


# Calculate and plot mitigated Emissions vs. recycling by subtracting policy emissions 
#   from the BAU emissions (use interp scenario). 

# def plot_cumulative_policy_mitigation(
#     desired_vars, years_range, global_data_frames, scenario_List, desired_unit) :
#     # The inputs to this function are the dseired variables as a list of strings. 
#     # For example, ['emissions', 'production']. These strings need to match the variable names 
#     # of the data frames ("demand", "emissions", "production", "bank", etc.). The desired 
#     # unit is a string that denotes the units of the flows, for example 'Gt CO2-eq'
#     # This function plots global cumulative mitigation. 

#     # Define our legend titles given the desired variables 
#     legend_titles = []
#     for variable in desired_vars : 
#         title = 'Cumulative Mitigated ' + variable.title()
#         legend_titles.append(title)

#     for scenario in scenario_List:
#         # Plots only the policy mitigated variables 
#         if 'Proposal' in scenario_List :
#             plot = pd.DataFrame(
#                 columns = legend_titles,
#                 index = years_range
#                 )
#             for var in desired_vars :
#                 # Mitigation calculated as the difference between the BAU scenario and the policy
#                 #   scenarios. 
#                 mitigated_var = [a - b for a,b in zip(global_data_frames[('BAU')][var], 
#                     global_data_frames[(scenario)][var])]
#                 # Calculate Cumulative Mitigated Variables
#                 cumulative_mitigated_var = np.cumsum(mitigated_var)
#                 if desired_unit == 'Gt CO2-eq' : 
#                     # Convert to [Gt CO2-eq]
#                     cumulative_mitigated_var = [x * (10**(-3)) for x in cumulative_mitigated_var]
#                     y_label = 'Gt CO$_2$-eq'

#                 print(var + ' - ' + scenario_List[scenario]) #+ ' - ' + region_List[region])
#                 print( sum(mitigated_var)*(10**(-3)) ) # Gt CO2-eq
#                 plot[legend_titles(var)] = cumulative_mitigated_var
#                 # Plot against Recovery
#                 plot['Cumulative Recovery'] = [x*(10**(-3)) for x in np.cumsum(
#                     global_data_frames[('BAU')]['recovery'])]
#                 p1 = plot.plot()
#                 title = 'Mitigated ' + var.title() + ' : Policy Vs. End-of-Life Practices'
#                 filename = 'mitigation_' + scenario + '.pdf'
#                 plt.title(title)
#                 plt.xlabel('Year')
#                 plt.ylabel(y_label)
#                 plt.savefig(filename)

# plot_cumulative_policy_mitigation(['emissions', 'production'], years_range, 
#     global_data_frames, scenario_List, 'Gt CO2-eq')


# # Plotting each variable in each scenario. 
# # Each Plot contains one variable for all scenarios for one region
# def plot_vars_per_scenario(
#     desired_vars, desired_regions, summed_sectors_data_frames, 
#     scenario_List, years_range, desired_unit) : 
#     # This function plots a variable across each scenario for a given region, for as many 
#     #   regions as specified by the regions input vector (e.g. regions = ['NA5', 'A5']). 
#     # i.e., the same variable is plotted for each scenario on the same axis. So the legend
#     # consists of the different scenarios. 
#     # The desired unit input is a string for the desired input, for example, 'Mt CO2-eq'
#     # Default unit is Mt CO2-eq
#     y_label = 'Mt CO$_2$-eq'
#     for var in desired_vars:
#         if var == 'emissions' : 
#             for region in desired_regions:
#                 plot = pd.DataFrame(
#                     columns = scenario_List, 
#                     index = years_range
#                     )
#                 for scenario in scenario_List:
#                     data = summed_sectors_data_frames[(scenario, region)][var]
#                     # Convert if necessary
#                     if desired_unit == 'Gt CO2-eq' : 
#                         data = [x * 10**(-3) for x in data]
#                         y_label = 'Gt CO$_2$-eq'
#                     # fill the plot's data frame with the vectors we want to be plotted  
#                     plot[scenario] = summed_sectors_data_frames[(scenario, region)][var]
#                 file_name = 'total_' + var + '_' + region + '.pdf'
#                 title = 'HFC ' + var.title() + ' for ' + region + ' Countries'
#                 p1 = plot.plot()
#                 plt.title(title)
#                 plt.xlabel('Year')
#                 plt.ylabel(y_label)
#                 plt.savefig(file_name)

# plot_vars_per_scenario(['bank', 'emissions', 'recovery'], ['NA5'], summed_sectors_data_frames,
#     scenario_List, years_range, 'Mt CO2-eq')

# plt.close('all')
# p1 = plot.plot() #kind = 'area')

# General script for plotting one or more variable on the same axes, 
#   generating a plot for each scenario and for each region. 
# Plot Emissions and Recycling on the same axes; generate one plot for each scenario, 
# for each region, and then global. 

# scenario_List.remove('NA Proposal')
# scenario_List.remove('India Proposal')
# scenario_List.remove('EU Proposal')


desired_vars = 'emissions'

# plot2 = pd.DataFrame(
#     columns = ('Bank','Cumulative Emissions'), 
#     index = range(2014, 2051)
#     )
# plot2['Bank'] = flows['bank']
# plot2['Cumulative Emissions'] = np.cumsum(flows['emissions'])

# p2 = plot2.plot()
# plt.xlabel('Year')
# plt.ylabel('Mt CO$_2$-eq')
# plt.gca().set_ylim([0, 3e4])
# plt.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))

# plt.savefig('banks.pdf')



# emissions_plot = pd.DataFrame(
#     columns = scenario_List,
#     index = years_range     
#    )

# for scenario in scenario_List:
#     emissions_plot[scenario] = global_d_frames_dict[0][(scenario)]['emissions']    

# p1 = emissions_plot.plot()    
# plt.title('Global Emissions (Lower Bound Recycling Rates)')
# plt.xlabel('Year')
# file_name = 'Global_Emissions_Plots_LBR.pdf'
# plt.ylabel('Mt CO$_2$-eq')
# plt.savefig(file_name)

# emissions_plot = pd.DataFrame(
#     columns = scenario_List,
#     index = years_range     
#    )

# for scenario in scenario_List:
#     emissions_plot[scenario] = global_d_frames_dict[0.20][(scenario)]['emissions']    

# p1 = emissions_plot.plot()    
# plt.title('Global Emissions (Upper Bound Recycling Rates)')
# plt.xlabel('Year')
# file_name = 'Global_Emissions_Plots_UBR.pdf'
# plt.ylabel('Mt CO$_2$-eq')
# plt.savefig(file_name)






# for scenario in scenario_List:
#     for region in region_List:
#         plot = pd.DataFrame( 
#             columns = desired_vars, 
#             index = years_range
#             )
#         file_name = ''
#         title = 'HFC Material Flows: ' + scenario.title() + ' (' + region + ')'
#         for var in desired_vars :
#             # fill plot's data frame with vectors we want to plot
#             plot[var] = summed_sectors_data_frames[(scenario, region)][var]
#             file_name = file_name + var + '_' 
#             #if var == len(vars_to_plot) - 1 : 
#                 #title = title + var.title() + ' (' + region + ') : ' + scenario.title()
#             #else: 
#                 #title = title + var.title() + ' and '
#         file_name = file_name + region + '_' + scenario + '.pdf'
#         p1 = plot.plot()
#         plt.title(title)
#         plt.xlabel('Year')
#         plt.ylabel('Mt CO$_2$-eq')
#         plt.savefig(file_name)


# For BAU, plot emissions and servicing demand or just demand in all sectors, 
# summed for both regions. 
# Highlight opportunities to increase EOL activities in SAC and other major use sectors 


# for var in desired_vars:
#     if (var == 'recycling') : or (var == 'emissions') :
#         plot = pd.DataFrame(
#             columns = sector_List,
#             index = years_range
#             )
#         for sector in sector_List:
#             a = 0
#             for region in region_List:
#                 a += data_frames[('BAU', region, sector)][var]
#             plot[sector_List[sector]] = a # Global sectorized time series for BAU
#         file_name = 'bau_sector_' + var + '.pdf'
#         title = 'Global HFC ' + var.title() + ' By Sector (BAU)'
#         p1 = plot.plot()
#         plt.title(title)
#         plt.xlabel('Year')
#         plt.ylabel('Mt CO$_2$-eq')
#         plt.savefig(file_name)

# sum for each region, then add sector to plot 




#plt.close('all')
## Global flows 
# for scenario in scenario_List:
#     plot = pd.DataFrame( 
#             columns = desired_vars, 
#             index = years_range
#             )
#     file_name = 'glob_material_flows_' + scenario + '.pdf'
#     title = 'Global HFC Material Flows: ' + scenario
#     for var in desired_vars:
#         plot[var] = global_data_frames[(scenario)][var]
#     p1 = plot.plot()
#     plt.title(title)
#     plt.xlabel('Year')
#     plt.ylabel('Mt CO$_2$-eq')
#     plt.savefig(file_name)



# Morgan's work from before that I did not modify or address. 

#plot2 = pd.DataFrame(
#    columns = ('Bank','Cumulative Emissions'), 
#    index = range(2014, 2051)
#    )
#plot2['Bank'] = policy_flows['bank']
#plot2['Cumulative Emissions'] = np.cumsum(policy_flows['emissions'])

#p2 = plot2.plot()
#plt.xlabel('Year')
#plt.ylabel('Mt CO$_2$-eq')
#plt.gca().set_ylim([0, 3e4])
#plt.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))



#plt.savefig('banks.pdf')
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

