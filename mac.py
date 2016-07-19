import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') #fixes framework problem with GUI
import matplotlib.pyplot as plt

# Create data frame to model material flows of HFCs:
flows = pd.DataFrame(
    columns = ('demand', 'bank', 'emissions', 'recycling', 'production'), 
    index = range(2014, 2051)
    )

# Policy targets for A5 and NA5 countries (taken from the EU proposal):
na5_policy_years = [2014, 2019, 2034, 2050]
na5_policy_targets = [695.5, 520.6, 91.9, 91.9] # [Mt CO2-eq]
a5_policy_years = [2014, 2019, 2040, 2050]
a5_policy_targets = [537.8, 896.3, 134.4, 134.4] # [Mt CO2-eq]

# Interpolate policy targets (linear interpolation):
year = list(range(2014, 2051))
na5_policy = np.interp(year, na5_policy_years, na5_policy_targets)
a5_policy = np.interp(year, a5_policy_years, a5_policy_targets)
global_policy = [sum(x) for x in zip(na5_policy, a5_policy)]

# Fill in policy target in data frame:
flows['demand'] = global_policy

# Fill in initial size of bank [Mt CO2-eq] and recycling:
flows.loc[2014, 'bank'] = 5000

# Calculate stocks and flows year-by-year:
ems_fac = 0.30 # emissions factor with range 0.15-0.3
rec_fac = 0.4 # recycling factor (as a fraction of emissions factor)

for t in range(2014, 2050):
    # Calculate emissions:
    flows.loc[t, 'emissions'] = ems_fac * (1 - rec_fac) * (
        flows.loc[t, 'demand'] + flows.loc[t, 'bank'])
    # Calculate recycling:
    flows.loc[t, 'recycling'] = ems_fac * rec_fac * (
        flows.loc[t, 'demand'] + flows.loc[t, 'bank'])
    # Calculate bank:
    flows.loc[t + 1, 'bank'] = (1 - ems_fac) * (
        flows.loc[t, 'demand'] + flows.loc[t, 'bank'])

flows.loc[2050, 'emissions'] = ems_fac * (1 - rec_fac) * (
    flows.loc[2050, 'demand'] + flows.loc[2050, 'bank'])
flows.loc[2050, 'recycling'] = ems_fac * rec_fac * (
    flows.loc[2050, 'demand'] + flows.loc[2050, 'bank'])

flows['production'] = flows['demand'] - flows['recycling']

emissions = sum(flows['emissions'])
recycling = sum(flows['recycling'])

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
plot1['Production'] = flows['production']
plot1['Recycling'] = flows['recycling']

p1 = plot1.plot(kind = 'area')
plt.xlabel('Year')
plt.ylabel('Mt CO$_2$-eq')
plt.savefig('demand.pdf')

plot2 = pd.DataFrame(
    columns = ('Bank','Cumulative Emissions'), 
    index = range(2014, 2051)
    )
plot2['Bank'] = flows['bank']
plot2['Cumulative Emissions'] = np.cumsum(flows['emissions'])

p2 = plot2.plot()
plt.xlabel('Year')
plt.ylabel('Mt CO$_2$-eq')
plt.gca().set_ylim([0, 3e4])
plt.ticklabel_format(style = 'sci', axis = 'y', scilimits = (0, 0))

plt.savefig('banks.pdf')