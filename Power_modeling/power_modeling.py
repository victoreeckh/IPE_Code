import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)


"""# Defining system parameters"""
Flat_roof = True
Battery_case = False
Southern_orientation_case = True
# east_west_tiltWest_orientation_case



"""# Defining system parameters"""

# Chosen optimal solar angles
optimal_south_tilt_angle = 40
optimal_east_west_tilt_angle = 10

n = 8                           #Amount of solar panels
A = 1                           #Surface area of panels

#PV efficiencies
eta_cell = np.average([20.46,23])/100
eta_shade = 1
eta_obstruct = 1

beta_ref = -0.29/100                      #see manufacturer datasheets-> welke?
T_ref = 25                                # [degrees]

eta_degrad = 1                            #approximation

#Inverter efficiencies
eta_inverter = 0.95
P_inverter_max = 1e20

"""# Download data"""

#from single GTI files
GTI_EW = np.load(project_dir+\
            f'/effective irradiance /Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_east_west_tilt_angle}.npy')
GTI_E = GTI_EW[0,:]
GTI_W = GTI_EW[2,:]

GTI_S = np.load(project_dir+\
            f'/effective irradiance /Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_south_tilt_angle}.npy')
GTI_S = GTI_S[1,:]

#Cell temperature data
T_CommRoof = np.load(project_dir+'/Data_processing/Output_data/processed_T_CommRoof_data.npy')
T_RV = np.load(project_dir+'/Data_processing/Output_data/processed_T_RV_data.npy')

"""# Power modeling calculations"""

#Cases are binary permutations of (roof_tilt,orientation,battery use)=2^3=8 cases

if Flat_roof:
    T_cell = T_CommRoof
else:
    T_cell = T_RV

if Southern_orientation_case:

    P_sun = GTI_S*n*A                                                   #(365,24,60)

    if not Battery_case:


        #all are (365,24,60) ndarrays

        eta_temp = 1 - beta_ref*(T_cell-T_ref)
        eta_panel = eta_cell * eta_shade * eta_obstruct * eta_temp * eta_degrad

        P_panel = P_sun*eta_panel                                       #Element wise product
        P_inverter = eta_inverter*P_panel
