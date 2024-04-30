import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)

from get_number_of_solar_panels import get_number_of_solar_panels

from price_calculation_v2 import get_electricity_bill

from financial_functions import get_financials


def run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,EV_case,PV_data,Inverter_data,Battery_data,EV_data):
    """# Defining system parameters"""

    # Chosen optimal solar angles
    optimal_south_tilt_angle = 40
    optimal_east_west_tilt_angle = 10
    gable_angle = 45

    #PV data
    l_roof = 10
    w_roof = 8
    l_panel = PV_data['l_panel_option']
    w_panel = PV_data['w_panel_option']
    A = l_panel*w_panel
    n = get_number_of_solar_panels(Southern_orientation_case, Flat_roof_case, w_roof, l_roof, w_panel, l_panel,PV_data['P_PV_peak_option'],Inverter_data['P_inverter_max_option'])                           #Amount of solar panels

    P_PV_peak = PV_data['P_PV_peak_option']

    eta_cell = PV_data['eta_cell_option']
    eta_shade = 1
    eta_obstruct = 1

    beta_ref = PV_data['beta_ref_option']
    T_ref = 25                                # [degrees]
    eta_degrad = 1                            #approximation

    PV_price = PV_data['PV_price_option']
    PV_lifetime = PV_data['PV_lifetime_option']

    #inverter data
    #Inverter efficiencies
    eta_inverter = Inverter_data['eta_inverter_option']
    P_inverter_max = Inverter_data['P_inverter_max_option']

    inverter_price = Inverter_data['inverter_price_option']
    inverter_lifetime = Inverter_data['inverter_lifetime_option']

    #Battery data
    P_bat_charge_max = Battery_data['P_bat_charge_max_option'] #W
    P_bat_discharge_max = Battery_data['P_bat_discharge_max_option'] #W (From inverter datasheets??)
    E_bat_max = Battery_data['E_bat_max_option'] #kWh (medium battery)
    eta_bat = Battery_data['eta_bat_option']

    battery_price = Battery_data['battery_price_option']
    battery_lifetime = Battery_data['battery_lifetime_option']

    #EV data
    EV_average_distance_traveled_per_day = EV_data['EV average distance traveled per day']
    EV_average_energy_consumption = EV_data['EV average energy consumption']
    EV_average_home_arrival_time_index = EV_data['EV average home arrival time index']
    EV_P_charge_max = EV_data['Max charge speed']


    """# Download data"""
    #Cell temperature data
    T_CommRoof = np.load(project_dir+'/Data_processing/Output_data/processed_T_CommRoof_data.npy')
    T_RV = np.load(project_dir+'/Data_processing/Output_data/processed_T_RV_data.npy')

    # split 1: 2^1
    #load data
    #from single GTI files
    if Flat_roof_case:
        T_cell = T_CommRoof

        if Southern_orientation_case:
            GTI_S = np.load(project_dir+\
                        f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_south_tilt_angle}.npy')
            GTI = GTI_S[1,:].reshape(365,24,60)
        else:
            GTI_EW = np.load(project_dir+\
                        f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_east_west_tilt_angle}.npy')
            GTI_E = GTI_EW[0,:].reshape(365,24,60)
            GTI_W = GTI_EW[2,:].reshape(365,24,60)
            GTI = (GTI_E+GTI_W)/2

    else:
        T_cell = T_RV

        south_tilt_angle = gable_angle
        east_west_tilt_angle = gable_angle
        if Southern_orientation_case:
            GTI_S = np.load(project_dir+\
                        f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{gable_angle}.npy')
            GTI_S = GTI_S[1,:].reshape(365,24,60)
            GTI_N = np.load(project_dir+\
                        f'/effective_irradiance/Output_data/total_irradiance_per_angle_N/total_irradiance_for_tilt_angle_45.npy')
            GTI_N = GTI_N[1,:].reshape(365,24,60)
            GTI = (GTI_S + GTI_N)/2

        else:
            GTI_EW = np.load(project_dir+\
                        f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{gable_angle}.npy')
            GTI_E = GTI_EW[0,:].reshape(365,24,60)
            GTI_W = GTI_EW[2,:].reshape(365,24,60)
            GTI = (GTI_E+GTI_W)/2


    # P_load = np.load(project_dir+'/Data_processing/Output_data/processed_load_data.npy')
    processed_load_data_df = pd.read_csv(project_dir+'/Data_processing/Output_data/processed_load_data_df.csv')
    P_load_array = processed_load_data_df['load data'].to_numpy()*1000 #Watt

    if EV_case == 1:
        #Build EV load profile
        EV_load_array = np.zeros((365,96))
        charge_time = np.floor(EV_average_energy_consumption*EV_average_distance_traveled_per_day/EV_P_charge_max).astype(int)*4
        EV_load_array[:,EV_average_home_arrival_time_index:EV_average_home_arrival_time_index+charge_time] = EV_P_charge_max*1000 #W
        EV_load_array = EV_load_array.reshape(365*96)
        P_load_array = P_load_array + EV_load_array


    """# Power modeling calculations"""

    #Cases are binary permutations of (roof_tilt,orientation,battery use)=2^3=8 cases

    eta_temp = 1 - beta_ref*(T_cell-T_ref)
    eta_panel = eta_cell * eta_shade * eta_obstruct * eta_temp * eta_degrad
    eta_panel = eta_panel.reshape(365,24,60)
    # print(eta_panel.shape)

    P_sun = GTI                                                     #(365,24,60)
    P_panel = P_sun*eta_panel                                           #Element wise product

    #PV panel max implementation
    P_panel[P_panel>=P_PV_peak] = P_PV_peak

    P_inverter = eta_inverter*P_panel*n*A
    P_inverter_array = P_inverter[:,:,::15].reshape(365*96)


    delta_t = 15*60

    # split 3: 2^3
    if not Battery_case:
        P_offtake_array = P_load_array - P_inverter_array
        P_injection_array = - P_offtake_array
        P_direct_consumption_array = P_inverter_array - P_injection_array
        E_battery_array = np.zeros(P_inverter_array.shape[0])

    else:
        E_bat = 0

        P_offtake_array = np.zeros(P_inverter_array.shape[0])
        P_injection_array = np.zeros(P_inverter_array.shape[0])
        P_direct_consumption_array = np.zeros(P_inverter_array.shape[0])
        E_battery_array = np.zeros(P_inverter_array.shape[0])

        for t in range(P_inverter_array.shape[0]):
            # print(t)
            if P_inverter_array[t] > P_inverter_max:
                P_inverter = P_inverter_max
            else:
                P_inverter = P_inverter_array[t]
            P_load = P_load_array[t]

            if P_inverter > P_load:
                P_direct_consumption = P_load                           #Consume
                P_excess = P_inverter - P_load
                P_offtake = 0

                if E_bat < E_bat_max:                                   #battery not full yet

                    P_charge_max = np.min([P_bat_charge_max,(E_bat_max-E_bat)*3600*1000/delta_t])

                    if P_excess > P_charge_max:
                        P_bat_charge = P_charge_max
                        E_bat += (P_bat_charge/1000)*(delta_t/3600)                   #charge battery
                        P_injection = P_excess - P_bat_charge/eta_bat
                    else:
                        P_bat_charge = P_excess
                        E_bat += (P_bat_charge/1000)*(delta_t/3600)*eta_bat          #charge battery
                        P_injection = 0
                else:
                    P_injection = P_excess                              #inject when battery is full
            else:                                                       #Load demand is greater then generation
                P_direct_consumption = P_inverter
                P_short = P_load - P_inverter
                P_injection = 0
                if E_bat>0:                                             #battery not empty yet
                    P_discharge_max = np.min([P_bat_discharge_max,E_bat*3600*1000/delta_t])
                    if P_short > P_discharge_max:
                        P_bat_discharge = P_discharge_max
                        E_bat -= (P_bat_discharge/1000)*(delta_t/3600)                #discharge battery
                        P_offtake = P_short - P_bat_discharge*eta_bat
                    else:
                        P_bat_discharge = P_short
                        E_bat -= (P_bat_discharge/1000)*(delta_t/3600)/eta_bat        #discharge battery
                        P_offtake = 0
                P_offtake = P_short

            P_offtake_array[t] = P_offtake
            P_injection_array[t] = P_injection
            P_direct_consumption_array[t] = P_direct_consumption
            E_battery_array[t] = E_bat
    P_offtake = P_offtake_array.reshape(365,96)
    P_injection = P_injection_array.reshape(365,96)
    P_direct_consumption = P_direct_consumption_array.reshape(365,96)
    P_inverter = P_inverter_array.reshape(365,96)
    P_load = P_load_array.reshape(365,96)
    E_battery = E_battery_array.reshape(365,96)

    return P_offtake, P_injection, P_direct_consumption, P_inverter, P_load, E_battery
