
import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') #fixes framework problem with GUI
import matplotlib.pyplot as plt

# Create data frames to model material flows of HFCs:
policy_flows = pd.DataFrame(
    columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery'), 
    index = range(2014, 2051)
    )

na5_policy_mac_flows = pd.DataFrame(
    columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery'), 
    index = range(2015, 2051)
    )

a5_policy_mac_flows = pd.DataFrame(
    columns = ('demand', 'bank', 'emissions', 'recycling', 'production','recovery'), 
    index = range(2015, 2051)
    )

# scenario 1 (Exponential Growth; TEAP Growth Rates)

# MAC: Motor (Vehicle) Air Conditioning

a5_mac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_mac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

# SAC: Stationary Air Conditioning

a5_sac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_sac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )
 
# DOM: Domestic Refrigeration

a5_DOM_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_DOM_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

# TRANS: Transport Refrigeration

a5_TRANS_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_TRANS_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

# IND: Industrial Refrigeration

a5_IND_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_IND_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

# COM: Commercial Refrigeration

a5_COM_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )

na5_COM_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production','recycling'),
    index = range(2015,2051)
    )


# Linear Extrapolation 
a5_bau_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production','recycling'),
   index = range(2015,2051)
   )

na5_bau_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production','recycling'),
   index = range(2015,2051)
   )

# scenario 2: linear extrapolation growth scenario 
a5_mac_scen2_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production','recycling'),
   index = range(2015,2051)
   )

na5_mac_scen2_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production','recycling'),
   index = range(2015,2051)
   )

# scenario 3: growth using TEAP demand percentages; interpolation and extrapolation 
a5_mac_scen3_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production'),
   index = range(2010,2051)
   )

na5_mac_scen3_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production'),
   index = range(2010,2051)
   )

# Policy targets for A5 (Article 5) and NA5 (Non Article 5) countries (taken from the EU proposal):
na5_policy_years = [2014, 2019, 2034, 2050]
na5_policy_targets = [695.5, 520.6, 91.9, 91.9] # [Mt CO2-eq]
a5_policy_years = [2014, 2019, 2040, 2050]
a5_policy_targets = [537.8, 896.3, 134.4, 134.4] # [Mt CO2-eq]

# Reported Consumption from Excel Spreadsheet for A5 and NA5 Countries t: [1992,2014]  [Mt CO2-eq]
na5_historical_consumption = [1.13,14.81,32.68,42.78,47.30,58.57,77.05,107.78,152.24,166.05,198.82,240.64,278.20,316.42,345.07,379.10,416.99,460.90,495.30,595.63,670.99,694.67,695.46]
a5_historical_consumption = [0.02,0.41,0.93,1.66,2.62,3.64,4.59,5.90,7.88,14.21,22.04,29.68,39.55,52.76,91.97,126.79,149.58,184.90,243.65,343.74,397.54,466.01,537.83]

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


# Extrapolate the 2015 and 2016 total consumption for na5 and a5 countries 

na5_bau_flows.loc[2015,'demand'] = linearExtrapolation(2013,2014,2015,694.67,695.46)
a5_bau_flows.loc[2015,'demand'] = linearExtrapolation(2013,2014,2015,466.01,537.83)
na5_bau_flows.loc[2016,'demand'] = linearExtrapolation(2014,2015,2016,695.46,na5_bau_flows.loc[2015,'demand'])
a5_bau_flows.loc[2016,'demand'] = linearExtrapolation(2014,2015,2016,537.83,a5_bau_flows.loc[2015,'demand'])


na5_2015_emissions_estimate = 328 # Mt CO2-eq (TEAP 2009 updated supplement)
a5_2015_emissions_estimate = 131 # Mt CO2-eq (TEAP 2009 updated supplement)

#### Based on checking these numbers from the TEAP 2009 updated supplement with the reports
#### it seems that these bank and emissions estimates are generally underestimating by about 100 Mt CO2-eq, so they will be semi-accurate placeholders for now


## Extrapolate Consumption, Emissions, Banks for 2015-2050 BAU for NA5 and A5 Countries Separately
for t in range(2017,2051) :
    # Calculate consumption 
    na5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_bau_flows.loc[t-2,'demand'],na5_bau_flows.loc[t-1,'demand'])
    a5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_bau_flows.loc[t-2,'demand'],a5_bau_flows.loc[t-1,'demand'])


##### Scenario 1: Model growth of each sector using exponential growth

# Note: Sector bank percentages from TEAP 2009 report are based on the modeled banks in tonnes, no data was provided
# for modeled banks in tCO2-eq, so these percentages are prone to error 

### Assuming a 15% annual servicing of the bank

servicing_pcnt = 0.15


### MAC
    #assume constant percentage break downs for total consumption into sectors
    #assume growth rates do not change (may relax later)
    #assume 2015 percentage break down applies to 2015 and 2016 so that 2 points can be generated for 
    #linear extrapolation 

na5_2016_mac_consumption_estimate = (0.1776)*na5_bau_flows.loc[2016,'demand'] # [Mt CO2-eq]
a5_2016_mac_consumption_estimate = (0.144)*a5_bau_flows.loc[2016,'demand'] # [Mt CO2-eq]

na5_2015_mac_consumption_estimate = (0.1776)*na5_bau_flows.loc[2015,'demand'] # [Mt CO2-eq]
a5_2015_mac_consumption_estimate = (0.144)*a5_bau_flows.loc[2015,'demand'] # [Mt CO2-eq]

a5_mac_scen2_flows.loc[2015,'demand'] = a5_2015_mac_consumption_estimate 
na5_mac_scen2_flows.loc[2015,'demand'] = na5_2015_mac_consumption_estimate

a5_mac_scen2_flows.loc[2016,'demand'] = a5_2016_mac_consumption_estimate
na5_mac_scen2_flows.loc[2016,'demand'] = na5_2016_mac_consumption_estimate


    # BAU exponentially model consumption for MAC
na5_mac_flows['demand'] = exponentialGrowth(na5_2015_mac_consumption_estimate,0.04,2015,2050) # [Mt CO2-eq]
a5_mac_flows['demand'] = exponentialGrowth(a5_2015_mac_consumption_estimate,0.07,2015,2050) # [Mt CO2-eq]


# MAC bank estimates BAU 
    # To estimate the bank of MAC HFC's, the sector bank percentages from TEAP 2009 report are applied to the 
    # overall bank estimates (3191, 1127) (NA5, A5 Countries)
na5_mac_flows.loc[2015,'bank'] = 3191*0.325942 # Mt CO2-eq (TEAP 2009 updated supplement)
a5_mac_flows.loc[2015,'bank'] = 1127*0.250457 # Mt CO2-eq (TEAP 2009 updated supplement)


##ignore scen2 flows for now
na5_mac_scen2_flows.loc[2015,'bank'] = 3191*0.325942
a5_mac_scen2_flows.loc[2015,'bank'] = 1127*0.250457

na5_policy_mac_flows.loc[2015,'bank'] = 3191*0.325942
a5_policy_mac_flows.loc[2015,'bank'] = 1127*0.250457

mac_na5_ems_factor = 0.15175
mac_a5_ems_factor = 0.15

for t in range(2015,2051) :
    # calculate emissions; Emissions Factor for NA5 MAC = 0.15175 (an average of factors for EU, USA, Japan, "Rest OECD")
        #Emissions factor for A5 MAC = 15% (VELDERS 2015si)
    na5_mac_flows.loc[t,'emissions'] = (mac_na5_ems_factor)*(na5_mac_flows.loc[t,'demand'] + na5_mac_flows.loc[t,'bank'])
    a5_mac_flows.loc[t,'emissions'] = (mac_a5_ems_factor)*(a5_mac_flows.loc[t,'demand'] + a5_mac_flows.loc[t,'bank'])

    # calculate Recovery
    na5_mac_flows.loc[t,'recovery'] = (servicing_pcnt)*(na5_mac_flows.loc[t,'bank'])
    a5_mac_flows.loc[t,'recovery'] = (servicing_pcnt)*(na5_mac_flows.loc[t,'bank'])

    # calculate next year's bank
    if t != 2050 :
        na5_mac_flows.loc[t+1,'bank'] = (1-mac_na5_ems_factor)*(na5_mac_flows.loc[t,'demand'] + na5_mac_flows.loc[t,'bank'])
        a5_mac_flows.loc[t+1,'bank'] = (1-mac_a5_ems_factor)*(a5_mac_flows.loc[t,'demand'] + a5_mac_flows.loc[t,'bank'])



# note: having the (1-ems_factor) attached to the bank calculation is the same as separately calculating emissions and subtracting them out

# still scenario 1: exponential modeling
##################### SAC: Stationary Air Conditioning

a5_sac_flows.loc[2015,'demand'] = a5_bau_flows.loc[2015,'demand']*0.5017 # [Mt CO2-eq]
na5_sac_flows.loc[2015,'demand'] = na5_bau_flows.loc[2015,'demand']*0.513 # [Mt CO2-eq]

#extrapolate consumption exponentially; TEAP growth rates for NA5 countries are a non-weighted average of the given growth rates
    # assumes equal weighting for NA5 Countries: Something to relax in the future? Weighted average? or break up by country?

na5_sac_flows['demand'] = exponentialGrowth(na5_sac_flows.loc[2015,'demand'],0.026,2015,2050)
a5_sac_flows['demand'] = exponentialGrowth(a5_sac_flows.loc[2015,'demand'],0.057,2015,2050)
 
# Estimate SAC Bank by applying a sector percentage to overall bank estimate 

na5_sac_flows.loc[2015,'bank'] = (0.393038)*3191
a5_sac_flows.loc[2015,'bank'] = (0.258529)*1127

sac_na5_ems_factor = 0.07125 # equally weighted average of 4 groups that are NA5 countries (Velders 2015si)
sac_a5_ems_factor = 0.0665 # equally weighted average of 2 groups that make up A5 countries (Velders 2015si)


for t in range(2015,2051):
    # Calculate emissions
    na5_sac_flows.loc[t,'emissions'] = (sac_na5_ems_factor)*(na5_sac_flows.loc[t,'bank'] + na5_sac_flows.loc[t,'demand'])
    a5_sac_flows.loc[t,'emissions'] = (sac_a5_ems_factor)*(a5_sac_flows.loc[t,'bank'] + a5_sac_flows.loc[t,'demand'])
    # Calculate Bank
    if t != 2050 :
        na5_sac_flows.loc[t+1,'bank'] = (1 - sac_na5_ems_factor)*(na5_sac_flows.loc[t,'bank'] + na5_sac_flows.loc[t,'demand'])
        a5_sac_flows.loc[t+1,'bank'] = (1 - sac_a5_ems_factor)*(a5_sac_flows.loc[t,'bank'] + a5_sac_flows.loc[t,'demand'])




#################### Domestic Refrigeration Sector (DOM)

# Generate consumption estimates for this sector as a percentage of total demand
na5_DOM_flows.loc[2015,'demand'] = na5_bau_flows.loc[2015,'demand']*0.0037
a5_DOM_flows.loc[2015,'demand'] = a5_bau_flows.loc[2015,'demand']*0.0387

# Extrapolate the rest of consumption for the sector using exponential growth
# growth rates are averages of the growth rates for the groups of countries within the NA5 and A5 groupings
na5_DOM_flows['demand'] = exponentialGrowth(na5_DOM_flows.loc[2015,'demand'],0.016,2015,2050)
a5_DOM_flows['demand'] = exponentialGrowth(a5_DOM_flows.loc[2015,'demand'],0.034,2015,2050)

# Estimate DOM bank by applying a sector percentage to total bank estimate 

na5_DOM_flows.loc[2015,'bank'] = (0.052884)*(3191)
a5_DOM_flows.loc[2015,'bank'] = (0.176175)*(1127)

dom_na5_ems_factor = 0.025
dom_a5_ems_factor = 0.025

# estimate the remaining variables through material flows

for t in range(2015,2051):
    # Calculate emissions
    na5_DOM_flows.loc[t,'emissions'] = (dom_na5_ems_factor)*(na5_DOM_flows.loc[t,'demand'] + na5_DOM_flows.loc[t,'bank'])
    a5_DOM_flows.loc[t,'emissions'] = (dom_a5_ems_factor)*(a5_DOM_flows.loc[t,'demand'] + a5_DOM_flows.loc[t,'bank'])

    # Calculate bank
    if t != 2050 :
        na5_DOM_flows.loc[t+1,'bank'] = (1 - dom_na5_ems_factor)*(na5_DOM_flows.loc[t,'demand'] + na5_DOM_flows.loc[t,'bank'])
        a5_DOM_flows.loc[t+1,'bank'] = (1 - dom_a5_ems_factor)*(a5_DOM_flows.loc[t,'demand'] + a5_DOM_flows.loc[t,'bank'])



################# Commercial Refrigeration Sector (COM)

# estimate Commercial refrigeration consumption as a percentage of total consumption
na5_COM_flows.loc[2015,'demand'] = na5_bau_flows.loc[2015,'demand']*(0.2537)
a5_COM_flows.loc[2015,'demand'] = a5_bau_flows.loc[2015,'demand']*(0.28)


# Extrapolate Consumption using exponential growth

na5_COM_flows['demand'] = exponentialGrowth(na5_COM_flows.loc[2015,'demand'],0.021,2015,2050)
a5_COM_flows['demand'] = exponentialGrowth(a5_COM_flows.loc[2015,'demand'],0.039,2015,2050)

# Estimate COM Bank in 2015 using percentage of the total bank

na5_COM_flows.loc[2015,'bank'] = 3191*(0.169199)
a5_COM_flows.loc[2015,'bank'] = 1127*(0.285630)

# See Velders 2015si for these emissions factors 
com_na5_ems_factor = 0.13475
com_a5_ems_factor = 0.11

# Material Flows to estimate the remaning banks and emissions

for t in range(2015,2051): 
    # Calculate Emissions
    na5_COM_flows.loc[t,'emissions'] = (com_na5_ems_factor)*(na5_COM_flows.loc[t,'bank'] + na5_COM_flows.loc[t,'demand'])
    a5_COM_flows.loc[t,'emissions'] = (com_a5_ems_factor)*(a5_COM_flows.loc[t,'demand'] + a5_COM_flows.loc[t,'bank'])

    # Calculate Bank
    if t != 2050 :
        na5_COM_flows.loc[t+1,'bank'] = (1 - com_na5_ems_factor)*(na5_COM_flows.loc[t,'demand'] + na5_COM_flows.loc[t,'bank'])
        a5_COM_flows.loc[t+1,'bank'] = (1 - com_a5_ems_factor)*(a5_COM_flows.loc[t,'demand'] + a5_COM_flows.loc[t,'bank'])


############### Industrial Refrigeration (IND)

# estimate Industrial refrigeration consumption as a percentage of total consumption
na5_IND_flows.loc[2015,'demand'] = na5_bau_flows.loc[2015,'demand']*(0.0356)
a5_IND_flows.loc[2015,'demand'] = a5_bau_flows.loc[2015,'demand']*(0.0185)


# Extrapolate Consumption using exponential growth

na5_IND_flows['demand'] = exponentialGrowth(na5_IND_flows.loc[2015,'demand'],0.01,2015,2050)
a5_IND_flows['demand'] = exponentialGrowth(a5_IND_flows.loc[2015,'demand'],0.038,2015,2050)

# Estimate IND Bank in 2015 using percentage of the total bank

na5_IND_flows.loc[2015,'bank'] = 3191*(0.046744)
a5_IND_flows.loc[2015,'bank'] = 1127*(0.025824)

# See Velders 2015si for these emissions factors 
ind_na5_ems_factor = 0.0875
ind_a5_ems_factor = 0.11

# Material Flows to estimate the remaning banks and emissions

for t in range(2015,2051): 
    # Calculate Emissions
    na5_IND_flows.loc[t,'emissions'] = (ind_na5_ems_factor)*(na5_IND_flows.loc[t,'bank'] + na5_IND_flows.loc[t,'demand'])
    a5_IND_flows.loc[t,'emissions'] = (ind_a5_ems_factor)*(a5_IND_flows.loc[t,'demand'] + a5_IND_flows.loc[t,'bank'])

    # Calculate Bank
    if t != 2050 :
        na5_IND_flows.loc[t+1,'bank'] = (1 - ind_na5_ems_factor)*(na5_IND_flows.loc[t,'demand'] + na5_IND_flows.loc[t,'bank'])
        a5_IND_flows.loc[t+1,'bank'] = (1 - ind_a5_ems_factor)*(a5_IND_flows.loc[t,'demand'] + a5_IND_flows.loc[t,'bank'])



#####3####### Transport Refrigeration (TRANS) sector

# estimate transportation refrigeration consumption as a percentage of total consumption
na5_TRANS_flows.loc[2015,'demand'] = na5_bau_flows.loc[2015,'demand']*(0.0165)
a5_TRANS_flows.loc[2015,'demand'] = a5_bau_flows.loc[2015,'demand']*(0.0169)


# Extrapolate Consumption using exponential growth

na5_TRANS_flows['demand'] = exponentialGrowth(na5_TRANS_flows.loc[2015,'demand'],0.02,2015,2050)
a5_TRANS_flows['demand'] = exponentialGrowth(a5_TRANS_flows.loc[2015,'demand'],0.0425,2015,2050)

# Estimate COM Bank in 2015 using percentage of the total bank

na5_TRANS_flows.loc[2015,'bank'] = 3191*(0.012194)
a5_TRANS_flows.loc[2015,'bank'] = 1127*(0.003385)

# See Velders 2015si for these emissions factors (Velders 2015si)
trans_na5_ems_factor = 0.197
trans_a5_ems_factor = 0.197 ### No emissions factor given for A5/developing countries, so for now, will assume they are the same as NA5 as a place holder


# Material Flows to estimate the remaning banks and emissions

for t in range(2015,2051): 
    # Calculate Emissions
    na5_TRANS_flows.loc[t,'emissions'] = (trans_na5_ems_factor)*(na5_TRANS_flows.loc[t,'bank'] + na5_TRANS_flows.loc[t,'demand'])
    a5_TRANS_flows.loc[t,'emissions'] = (trans_a5_ems_factor)*(a5_TRANS_flows.loc[t,'demand'] + a5_TRANS_flows.loc[t,'bank'])

    # Calculate Bank
    if t != 2050 :
        na5_TRANS_flows.loc[t+1,'bank'] = (1 - trans_na5_ems_factor)*(na5_TRANS_flows.loc[t,'demand'] + na5_TRANS_flows.loc[t,'bank'])
        a5_TRANS_flows.loc[t+1,'bank'] = (1 - trans_a5_ems_factor)*(a5_TRANS_flows.loc[t,'demand'] + a5_TRANS_flows.loc[t,'bank'])




## Sum up all the sectors to obtain total demand/consumption for each group (NA5 and A5)












##### Scenario 2: Linear Extrapolation Consumption Growth (holding off for now)

# Extrapolate MAC HFC consumption using linear extrapolation

for t in range(2017,2051):
    na5_mac_scen2_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_mac_scen2_flows.loc[t-2,'demand'],na5_mac_scen2_flows.loc[t-1,'demand'])
    a5_mac_scen2_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_mac_scen2_flows.loc[t-2,'demand'],a5_mac_scen2_flows.loc[t-1,'demand'])

# Calculate emissions and banks based on material flows 

for t in range(2015,2051):
    # calculate emissions; Emissions Factor for NA5 MAC = 0.15175 (an average of factors for EU, USA, Japan, "Rest OECD")
        #Emissions factor for A5 MAC = 15% (VELDERS 2015si)
    na5_mac_scen2_flows.loc[t,'emissions'] = (mac_na5_ems_factor)*(na5_mac_scen2_flows.loc[t,'demand'] + na5_mac_scen2_flows.loc[t,'bank'])
    a5_mac_scen2_flows.loc[t,'emissions'] = (mac_a5_ems_factor)*(a5_mac_scen2_flows.loc[t,'demand'] + a5_mac_scen2_flows.loc[t,'bank'])

    # calculate next year's bank
    if t != 2050 :
        na5_mac_scen2_flows.loc[t+1,'bank'] = (1-mac_na5_ems_factor)*(na5_mac_scen2_flows.loc[t,'demand'] + na5_mac_scen2_flows.loc[t,'bank'])
        a5_mac_scen2_flows.loc[t+1,'bank'] = (1-mac_a5_ems_factor)*(a5_mac_scen2_flows.loc[t,'demand'] + a5_mac_scen2_flows.loc[t,'bank'])




#####Scenario 3: applying TEAP percentages for sector growth and interpolating between those points (just thought I'd try it out)

# MAC consumption estimates for 2010, 2015, 2020, 2025, and 2030; based on TEAP demand percentages by sector
na5_mac_consumption_estimates = [na5_historical_consumption[18]*0.269,na5_bau_flows.loc[2015,'demand']*0.1776,na5_bau_flows.loc[2020,'demand']*0.1478,na5_bau_flows.loc[2025,'demand']*0.1307,na5_bau_flows.loc[2030,'demand']*0.129]
a5_mac_consumption_estimates = [a5_historical_consumption[18]*0.2077,a5_bau_flows.loc[2015,'demand']*0.144,a5_bau_flows.loc[2020,'demand']*0.128,a5_bau_flows.loc[2025,'demand']*0.109,a5_bau_flows.loc[2030,'demand']*0.1026]
estimate_years = [2010,2015,2020,2025,2030]

# interpolate consumption from 2010 to 2030 (between the estimates)
na5_interp_mac = np.interp(list(range(2010,2031)),estimate_years,na5_mac_consumption_estimates)
a5_interp_mac = np.interp(list(range(2010,2031)),estimate_years,a5_mac_consumption_estimates)

# insert the interpolated data into the demand flows of "scenario 3"
for t in range (2010,2031):
    a5_mac_scen3_flows.loc[t,'demand'] = a5_interp_mac[t-2010]
    na5_mac_scen3_flows.loc[t,'demand'] = na5_interp_mac[t-2010]

# extrapolate the remaining demand (2031-2050)
for t in range(2031,2051):
    a5_mac_scen3_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_mac_scen3_flows.loc[t-2,'demand'],a5_mac_scen3_flows.loc[t-1,'demand'])
    na5_mac_scen3_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_mac_scen3_flows.loc[t-2,'demand'],na5_mac_scen3_flows.loc[t-1,'demand'])




## Policy Scenario
# Interpolate policy targets (linear interpolation):
year = list(range(2014, 2051))
na5_policy = np.interp(year, na5_policy_years, na5_policy_targets)
a5_policy = np.interp(year, a5_policy_years, a5_policy_targets)
global_policy = [sum(x) for x in zip(na5_policy, a5_policy)]


#these estimates assume the percentage breakdowns don't change with the policies 
    #should check whether the policies in EU proposal specificy any MAC percentages/breakdowns (placeholders for now)
#2015,2020,2025,2030

na5_policy_targets_mac = [na5_policy[1]*0.1776,na5_policy[6]*0.1478,na5_policy[11]*0.1307,na5_policy[16]*0.129]
a5_policy_targets_mac = [a5_policy[1]*0.144,a5_policy[6]*0.128,a5_policy[11]*0.109,a5_policy[16]*0.1026]

projected_years = [2015,2020,2025,2030]
na5_mac_cons_prcntgs = [0.1776,0.1478,0.1307,0.129]
a5_mac_cons_prcntgs = [0.144,0.128,0.109,0.1026]

## Attempt 1: 
# interpolate the mac consumption between 2015 and 2030
na5_policy_mac = np.interp(list(range(2015,2031)),projected_years,na5_policy_targets_mac) # [MtCO2eq]
a5_policy_mac = np.interp(list(range(2015,2031)),projected_years,a5_policy_targets_mac) # [MtCO2eq]
global_policy_mac = na5_policy_mac + a5_policy_mac 

#fill the data frames' demands between 2015 and 2030
for t in range(2015,2031):
    na5_policy_mac_flows.loc[t,'demand'] = na5_policy_mac[t-2015]
    a5_policy_mac_flows.loc[t,'demand'] = a5_policy_mac[t-2015]


# extrapolate the remaining mac consumption under the policy scenario
### Note: Extrapolation as such generates negative consumption results after 2036
for t in range(2031,2035):
    na5_policy_mac_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_policy_mac_flows.loc[t-2,'demand'],na5_policy_mac_flows.loc[t-1,'demand'])
    a5_policy_mac_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_policy_mac_flows.loc[t-2,'demand'],a5_policy_mac_flows.loc[t-1,'demand'])

for t in range(2035,2051):
    na5_policy_mac_flows.loc[t,'demand'] = na5_policy_mac_flows.loc[2034,'demand']
    a5_policy_mac_flows.loc[t,'demand'] = a5_policy_mac_flows.loc[2034,'demand']


## Attempt 2: 

# interpolate and extrapolate percentages for 2015-2050 to apply to policy consumption figures 
# interpolate 2015-2030
#na5_interp_mac_prcntgs = np.interp(list(range(2015,2031)),projected_years,na5_mac_cons_prcntgs)
#a5_interp_mac_prcntgs = np.intepr(list(range(2015,2031)),projected_years,a5_mac_cons_prcntgs)

# extrapolate 2031-2034 (constant after 2034)
#for t in range(2031,2035):



#HFC-134a is phased out in new EU vehicles as of 2017, so demand decreases between 2015 and 2020 
#Phase out in new SAC equipment with HFC's with GWP's > 2500 by 2020 from EU



# Fill in policy target in data frame:
policy_flows['demand'] = global_policy



# Fill in initial size of bank [Mt CO2-eq] and recycling:
policy_flows.loc[2014, 'bank'] = 5000

# Calculate stocks and flows year-by-year:
ems_fac = 0.30 # emissions factor with range 0.15-0.3
rec_fac = 0.4 # recycling factor (as a fraction of emissions factor)




# MVAC Banks, emissions, recycling, demand for policy scenario

for t in range(2015,2051):
    # Calculate emissions
    na5_policy_mac_flows.loc[t,'emissions'] = (mac_na5_ems_factor)*(na5_policy_mac_flows.loc[t,'demand'] + na5_policy_mac_flows.loc[t,'bank'])
    a5_policy_mac_flows.loc[t,'emissions'] = (mac_a5_ems_factor)*(a5_policy_mac_flows.loc[t,'demand'] + a5_policy_mac_flows.loc[t,'bank'])
    # Calculate next year's bank
    if t != 2050 :
    na5_policy_mac_flows.loc[t+1,'bank'] = (1-mac_na5_ems_factor)*(na5_policy_mac_flows.loc[t,'demand'] + na5_policy_mac_flows.loc[t,'bank'])
    a5_policy_mac_flows.loc[t+1,'bank'] = (1-mac_a5_ems_factor)*(a5_policy_mac_flows.loc[t,'demand'] + a5_policy_mac_flows.loc[t,'bank']) 





for t in range(2014, 2050):
    # Calculate emissions:
    policy_flows.loc[t, 'emissions'] = ems_fac * (1 - rec_fac) * (
        policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    # Calculate recycling:
    policy_flows.loc[t, 'recycling'] = ems_fac * rec_fac * (
        policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    # Calculate bank:
    policy_flows.loc[t + 1, 'bank'] = (1 - ems_fac) * (
        policy_flows.loc[t, 'demand'] + policy_flows.loc[t, 'bank'])
    #flows.loc[t+1,'bank'] = flows.loc[t,'demand'] + flows.loc[t,'bank'] - 


policy_flows.loc[2050, 'emissions'] = ems_fac * (1 - rec_fac) * (
    policy_flows.loc[2050, 'demand'] + policy_flows.loc[2050, 'bank'])
policy_flows.loc[2050, 'recycling'] = ems_fac * rec_fac * (
    policy_flows.loc[2050, 'demand'] + policy_flows.loc[2050, 'bank'])

policy_flows['production'] = policy_flows['demand'] - policy_flows['recycling']

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

