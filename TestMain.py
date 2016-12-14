
import pandas as pd
import main
from unittest import TestCase

# Test the code at smaller levels. 
	# Example: Interpolation. 
		# Do it prospectively rather than introspectively. 
	# Formalize any sort of checking processes you're already doing 
	# Refactoring (current task); 
# Nose: searches for anything thats a test 
	# pip3 or pip install nose 


class TestMain(TestCase):

	def test_linearExtrap(self):
		# Check to see if linear Extrapolation works for a general case
		self.assertAlmostEqual(main.linearExtrapolation(1, 2, 3, 1, 2), 3, 5)

		# Check one of the interpolated servicing demand estimates from one of the sectors 
		# and regions. If this checks, we are assuming that the other sectors and regions 
		# are done correctly. This is a fair assumption because this process is done by loop.  
	
	def test_interpolate_servicing_demand(self):
	 	self.assertAlmostEqual(main.servc_demand_estimates.get(('SAC', 'A5'))[34], 1220.0606, 3)

	def test_interpolate_sector_prcnts(self):
	 	self.assertAlmostEqual(main.sector_percents.get(('IND', 'NA5'))[14], 
	 		0.02322000, 3)

	def test_exp_modeled_foams_demand(self):
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('BAU', 'A5', 'FOAMS')].loc[2037, 'demand'], 
			240.66735561, 3)

	def test_estimate2015Banks(self):
		# Checks one of the calculated 2015 bank estimates. This test assumes that, if passing, 
		# all the other points in the test behave similarly. i.e., if this test pasts, then all
		# of the values calculated are correct for this function. 
		# I feel that this is a fair assumption because the function is structured using loops, so 
		# the code is the same for all of the scenarios, regions, and sectors. 
		self.assertAlmostEqual(main.data_frame_dict[(0.20)][(
			'India Proposal', 'A5', 'DOM')].loc[2015, 'bank'], 198.549225, 3)

	def test_emissionsSample(self):
		# Checks whether the emissions calculation is running correctly by checking equality for 
		# a given data point. For this test, we use 'A5', 'NA Proposal', for the 'SAC' sector in
		# 2045. 
		self.assertAlmostEqual(main.data_frame_dict[(0.20)][(
			'NA Proposal', 'A5', 'SAC')].loc[2045,'emissions'], 113.67411185, 3)

	def test_calcEmissions(self):
		# Checks the function used to calculate emissions to ensure that the function is working
		# as intended. 
		self.assertAlmostEqual(main.calcEmissions(20, 30, 0.30, 0.10), 13.5, 5) 

	def test_calcRecycling(self):
		# Checks the function used to calculate recycling to ensure that the function is working
		# as intended, using arbitrary numbers
		self.assertAlmostEqual(main.calcRecycling(250, 659, 0.05, 0.025), 1.13625, 3)

	def test_calcNextYearsBank(self): 
		# Checks the function used to calculate the next year's bank from a current year's demand
		# and bank estimates (and emissions factor). 
		self.assertAlmostEqual(main.calcNextBank(251, 394, 0.10), 580.5, 3)

	def test_bankSample(self):
		# Checks whether the bank calculation is running correctly by checking equality for a 
		# given data point. For this test, we use 'A5', 'EU Proposal', for the 'FOAMS' sector in
		# 2031.
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('EU Proposal', 'A5', 'FOAMS')].loc[2031, 'bank'], 
			474.13138605766, 3)

	def test_recoveryFoamsSample(self):
		# Checks whether the recovery calculation is running correctly by checking equality for
		# a given data point in BAU. This test deals with the foams and fire sector, so if this 
		# test fails, check the if-statement for recovery that is for foams/fire. 
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('BAU', 'NA5', 'FOAMS')].loc[2029, 'recovery'], 
			173.9141430618, 3)

	def test_recoveryPolicySample(self):
		# Checks whether the recovery calculation is running correctly for the Policy scenarios
		# by checking equality for a given data point in the BAU. This test deals with the 
		# policy scenario "elif-statement" for recovery, so it needs its own test. 
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('India Proposal', 'A5', 'DOM')].loc[2046, 'recovery'],
			1.345365405, 3)

	def test_recoveryBAUSample(self):
		# Checks whether the recovery calculation is running correctly by checking equality for
		# a given data point in BAU. This test deals with the R/AC sectors, and represents the 
		# 'else statement' part of the recovery calculation. 
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('BAU', 'A5', 'SAC')].loc[2022, 'recovery'], 
			275.3860000, 3)
		
	def test_recyclingSample(self):
		# Checks whether the recycling calculation is running correctly by checking equality 
		# for a given data point. Passing this test implies that a complementary test of 
		# destruction would pass since this model has defined destruction as a function of
		# recycling. 
		self.assertAlmostEqual(
			main.data_frame_dict[(0.20)][('EU Proposal', 'NA5', 'IND')].loc[2036, 'recycling'], 
			0.56804881, 3)

	def test_sumsOfFrames(self):
		# Checks to see if the data frames were summed without any problem. 
		# Global_data_frames are comprised of sums of summed_sector_data_frames, which are comprised
		# of sums of data_frames. So testing the global_data_frames would imply that the 
		# summed_sector_data_frames were formed correctly through the correct summation of 
		# data frames. 
		self.assertAlmostEqual(main.global_d_frames_dict[(0.20)][('NA Proposal')].loc[2019, 'bank'], 
			7649.549265634, 3)

	def test_global_cum_mitigation(self):
		# Checks to see if the global cumulative mitigation estimates for each scenario are 
		# being calculated correctly. 
		self.assertAlmostEqual(main.global_cumulative_mitigation[('BAU')], 14168.92044, 3)

	def test_region_cum_mitigation(self):
		# Checks to see if the regional cumulative mitigation estimates for each scenario are 
		# being calculated correctly. 
		self.assertAlmostEqual(
			main.regional_cumulative_mitigation[('NA Proposal', 'A5')], 3103.41340921216, 3)	

	def test_sector_cum_mitigation(self):
		# Checks to see if the regional cumulative mitigation estimates for each scenario are 
		# being calculated correctly. 
		self.assertAlmostEqual(
			main.sector_cumulative_mitigation[('India Proposal', 'NA5','MAC')], 243.2615504, 3)		


#if __name__ == '__main__':
#    unittest.main()