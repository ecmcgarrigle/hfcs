
import pandas as pd
import numpy as np
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') #fixes framework problem with GUI
import matplotlib.pyplot as plt

# Create data frames to model material flows of HFCs:
policy_flows = pd.DataFrame(
    columns = ('demand', 'bank', 'emissions', 'recycling', 'production'), 
    index = range(2014, 2051)
    )

a5_mac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production'),
    index = range(2015,2051)
    )

na5_mac_flows = pd.DataFrame(
    columns = ('demand','bank','emissions','recovery','production'),
    index = range(2015,2051)
    )
 
a5_bau_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production'),
   index = range(2015,2051)
   )

na5_bau_flows = pd.DataFrame(
   columns = ('demand','bank','emissions','recovery','production'),
   index = range(2015,2051)
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
na5_bau_flows.loc[2016,'demand'] = linearExtrapolation(2014,2015,2016,695.46,na5_2015_consumption_estimate)
a5_bau_flows.loc[2016,'demand'] = linearExtrapolation(2014,2015,2016,537.83,a5_2015_consumption_estimate)


na5_2015_emissions_estimate = 328 # Mt CO2-eq (TEAP 2009 updated supplement)
a5_2015_emissions_estimate = 131 # Mt CO2-eq (TEAP 2009 updated supplement)

#### Based on checking these numbers from the TEAP 2009 updated supplement with othe reports
#### it seems that these bank and emissions estimates are generally underestimating by about 100 Mt CO2-eq, so they will be semi-accurate placeholders for now


## Extrapolate Consumption, Emissions, Banks for 2015-2050 BAU for NA5 and A5 Countries Separately
for t in range(2017,2051):
    # Calculate consumption 
    na5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,na5_bau_flows.loc[t-2,'demand'],na5_bau_flows.loc[t-1,'demand'])
    a5_bau_flows.loc[t,'demand'] = linearExtrapolation(t-2,t-1,t,a5_bau_flows.loc[t-2,'demand'],a5_bau_flows.loc[t-1,'demand'])


# Model growth of each sector using exponential growth

# MAC
    #assume constant percentage break downs for total consumption into sectors
    #assume growth rates do not change (may relax later)

na5_2015_mac_consumption_estimate = (0.1776)*na5_2015_consumption_estimate # [Mt CO2-eq]
a5_2015_mac_consumption_estimate = (0.144)*a5_2015_consumption_estimate # [Mt CO2-eq]

    # BAU exponentially model consumption for MAC
na5_mac_flows['demand'] = exponentialGrowth(na5_2015_mac_consumption_estimate,0.04,2015,2050) # [Mt CO2-eq]
a5_mac_flows['demand'] = exponentialGrowth(a5_2015_mac_consumption_estimate,0.07,2015,2050) # [Mt CO2-eq]

# MAC bank estimates BAU 
na5_mac_flows.loc[2015,'bank'] = 3191 # Mt CO2-eq (TEAP 2009 updated supplement)
a5_mac_flows.loc[2015,'bank'] = 1127 # Mt CO2-eq (TEAP 2009 updated supplement)

mac_na5_ems_factor = 0.15175
mac_a5_ems_factor = 0.15

for t in range(2015,2050):
    # calculate emissions; Emissions Factor for NA5 MAC = 0.15175 (an average of factors for EU, USA, Japan, "Rest OECD")
        #Emissions factor for A5 MAC = 15% (VELDERS 2015si)
    na5_mac_flows.loc[t,'emissions'] = (mac_na5_ems_factor)*(na5_mac_flows.loc[t,'demand'] + na5_mac_flows.loc[t,'bank'])
    a5_mac_flows.loc[t,'emissions'] = (mac_a5_ems_factor)*(a5_mac_flows.loc[t,'demand'] + a5_mac_flows.loc[t,'bank'])

    # calculate next year's bank
    na5_mac_flows.loc[t+1,'bank'] = (1-mac_na5_ems_factor)*(na5_mac_flows.loc[t,'demand'] + na5_mac_flows.loc[t,'bank'])
    a5_mac_flows.loc[t+1,'bank'] = (1-mac_a5_ems_factor)*(a5_mac_flows.loc[t,'demand'] + a5_mac_flows.loc[t,'bank'])

na5_mac_flows.loc[2050,'emissions'] = (mac_na5_ems_factor)*(na5_mac_flows.loc[2050,'demand'] + na5_mac_flows.loc[2050,'bank'])
a5_mac_flows.loc[2050,'emissions'] = (mac_a5_ems_factor)*(a5_mac_flows.loc[2050,'demand'] + a5_mac_flows.loc[2050,'bank'])


# note: having the (1-ems_factor) attached to the bank calculation is the same as subtracting out emissions



##Policy Scenario
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

na5_policy_mac = np.interp(year,projected_years,na5_policy_targets_mac) # [MtCO2eq]
a5_policy_mac = np.interp(year,projected_years,a5_policy_targets_mac) # [MtCO2eq]
global_policy_mac = na5_policy_mac + a5_policy_mac 


#HFC-134a is phased out in new EU vehicles as of 2017, so demand decreases between 2015 and 2020 
#Phase out in new SAC equipment with HFC's with GWP's > 2500 by 2020 from EU



# Fill in policy target in data frame:
policy_flows['demand'] = global_policy

# Fill in initial size of bank [Mt CO2-eq] and recycling:
policy_flows.loc[2014, 'bank'] = 5000

# Calculate stocks and flows year-by-year:
ems_fac = 0.30 # emissions factor with range 0.15-0.3
rec_fac = 0.4 # recycling factor (as a fraction of emissions factor)

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

