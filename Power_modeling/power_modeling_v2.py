import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)

from get_number_of_solar_panels import get_number_of_solar_panels

from price_calculation_v2 import get_electricity_bill

from financial_functions import get_financials


def run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,dynamic_tarrif_case,EV_case,PV_data,Inverter_data,Battery_data,EV_data):
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
    EV_average_home_departure_time_index = EV_data['EV average home departure time index']
    P_bat_EV_charge_max = EV_data['Max charge speed convertor']
    P_bat_EV_discharge_max = EV_data['Max charge speed convertor']
    E_bat_EV_max = EV_data['Max battery capacity']
    eta_bat_EV = EV_data['Convertor efficiency']



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
            # n = int(n/2)
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
            GTI_N = GTI_N.reshape(365,24,60)
            # GTI = (GTI_S + GTI_N)/2
            GTI = GTI_S

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
        charge_time = np.ceil(EV_average_energy_consumption*EV_average_distance_traveled_per_day/P_bat_EV_charge_max).astype(int)*4
        EV_load_array[:,EV_average_home_arrival_time_index:EV_average_home_arrival_time_index+charge_time] = P_bat_EV_charge_max*1000 #W
        EV_load_array = EV_load_array.reshape(365*96)
        P_load_array = P_load_array + EV_load_array

    if EV_case == 2:
        EV_load_array = np.zeros((365,96))
        if dynamic_tarrif_case == False:
            P_charge = np.min([EV_average_energy_consumption*EV_average_distance_traveled_per_day/9,P_bat_EV_charge_max])*1000              #W
            EV_load_array[:,0:7*4] = P_charge
            EV_load_array[:,22*4-1:] = P_charge
            EV_load_array = EV_load_array.reshape(365*96)
            P_load_array = P_load_array + EV_load_array
        else:
            charge_time = 24-(EV_average_home_arrival_time_index - EV_average_home_departure_time_index)/4
            P_charge = np.min([EV_average_energy_consumption*EV_average_distance_traveled_per_day/charge_time,P_bat_EV_charge_max])*1000              #W
            EV_load_array[:,0:EV_average_home_departure_time_index] = P_charge
            EV_load_array[:,EV_average_home_arrival_time_index:] = P_charge
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
        P_inverter[P_inverter>=P_inverter_max] = P_inverter_max
        P_difference = P_load_array - P_inverter_array
        P_offtake_array = np.maximum(P_difference,0)
        P_injection_array = -np.minimum(P_difference,0)
        P_direct_consumption_array = P_inverter_array - P_injection_array
        E_battery_array = np.zeros(P_inverter_array.shape[0])

    elif EV_case!=3:
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

    else:
        E_bat = 0
        E_bat_EV = 0

        P_offtake_array = np.zeros(P_inverter_array.shape[0])
        P_injection_array = np.zeros(P_inverter_array.shape[0])
        P_direct_consumption_array = np.zeros(P_inverter_array.shape[0])
        E_battery_array = np.zeros(P_inverter_array.shape[0])

        for t in range(P_inverter_array.shape[0]):
            P_load = P_load_array[t]

            t_day = t%96
            if t_day == EV_average_home_arrival_time_index:
                E_bat_EV = E_bat_EV_max - EV_average_energy_consumption*EV_average_distance_traveled_per_day        #kWh

            if (t_day > EV_average_home_arrival_time_index and t_day<96) or (t_day > 0 and t_day<EV_average_home_departure_time_index):
                charge_time_necessary = np.floor(E_bat_EV/P_bat_EV_charge_max).astype(int)*4
                if t_day>EV_average_home_arrival_time_index:
                    charge_time_available = (96-t_day)+EV_average_home_departure_time_index
                else:
                    charge_time_available = EV_average_home_departure_time_index - t_day
                if charge_time_available < charge_time_necessary:
                    EV_battery_is_available = False
                    P_load+= P_bat_EV_charge_max
                else:
                    EV_battery_is_available = True
            else:
                EV_battery_is_available = False

            # print(t)
            if P_inverter_array[t] > P_inverter_max:
                P_inverter = P_inverter_max
            else:
                P_inverter = P_inverter_array[t]

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
                elif (E_bat_EV < E_bat_EV_max) and EV_battery_is_available:
                    P_charge_EV_max = np.min([P_bat_EV_charge_max,(E_bat_EV_max-E_bat_EV)*3600*1000/delta_t])

                    if P_excess > P_charge_EV_max:
                        P_bat_EV_charge = P_charge_EV_max
                        E_bat_EV += (P_bat_EV_charge/1000)*(delta_t/3600)                   #charge battery
                        P_injection = P_excess - P_bat_EV_charge/eta_bat_EV
                    else:
                        P_bat_EV_charge = P_excess
                        E_bat += (P_bat_EV_charge/1000)*(delta_t/3600)*eta_bat_EV          #charge battery
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
                elif E_bat_EV>0:                                             #battery not empty yet
                    P_EV_discharge_max = np.min([P_bat_EV_discharge_max,E_bat_EV*3600*1000/delta_t])
                    if P_short > P_EV_discharge_max:
                        P_bat_EV_discharge = P_EV_discharge_max
                        E_bat_EV -= (P_bat_EV_discharge/1000)*(delta_t/3600)                #discharge battery
                        P_offtake = P_short - P_bat_EV_discharge*eta_bat_EV
                    else:
                        P_bat_EV_discharge = P_short
                        E_bat_EV -= (P_bat_EV_discharge/1000)*(delta_t/3600)/eta_bat_EV        #discharge battery
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

def plot_power_modeling_one_day(day,P_load_day,P_inverter_day,P_offtake_day,E_battery_day):
    x = [i*4 for i in range(24)]
    l = ["%s:00"%i for i in range(24)]

    fig, ax = plt.subplots(3,1, figsize=(10, 8))
    ax1 = ax[0]
    ax2 = ax[1]
    ax3 = ax[2]

    plt.suptitle(f'Power modeling for day {day}', fontsize = 15)
    ax1.set_title("Demand and generation", fontsize = 15)
    ax1.plot(P_load_day, label='load demand')
    ax1.plot(P_inverter_day, label='Generation at AC inverter side')
    ax1.set_xticks([])
    ax1.set_xlabel('')
    ax1.set_xticks(x,l, fontsize=10, rotation=45)
    ax1.set_ylabel('Power [W]', fontsize = 15)
    ax1.tick_params(labelsize = 10)
    ax1.legend(frameon=False)

    ax2.set_title("Offtake and injection", fontsize = 15)
    ax2.plot(P_offtake_day, label='offtake')
    ax2.plot(P_injection_day, label='injection')
    # ax2.set_xticks([])
    # ax2.set_xlabel('')
    ax2.set_xticks(x,l, fontsize=10, rotation=45)
    ax2.set_ylabel('Power [W]', fontsize = 15)
    ax2.tick_params(labelsize = 10)
    ax2.legend(frameon=False)

    ax3.set_title("Battery charging", fontsize = 15)
    ax3.plot(E_battery_day, label='Battery charging state')
    ax3.set_xticks(x,l, fontsize=10, rotation=45)
    ax3.set_ylabel('E [kWh]', fontsize = 15)
    ax3.tick_params(labelsize = 10)
    ax3.set_xlabel("Time (hh:mm)", fontsize = 15)
    ax3.legend(frameon=False)
    plt.subplots_adjust(hspace=0.5)
    # plt.tight_layout()

    output_file_path = f'Output_data/figures/new/non_battery_case/plot_power_modeling_one_day_{day}_new'
    # plt.savefig(output_file_path)
    # plt.show()

Flat_roof_case = True
Battery_case = True
Southern_orientation_case = True
dynamic_tarrif_case = True
EV_case = 1

PV_data = {}
PV_data['l_panel_option'] = 2.278
PV_data['w_panel_option'] = 1.134
PV_data['P_PV_peak_option'] = 550
PV_data['eta_cell_option'] = 0.213
PV_data['beta_ref_option'] = -0.0034
PV_data['PV_price_option'] = 212
PV_data['PV_lifetime_option'] = 25

#hybrid
Inverter_data = {}
Inverter_data['eta_inverter_option'] = 0.95
Inverter_data['P_inverter_max_option'] = 6000
Inverter_data['inverter_price_option'] = 3000
Inverter_data['inverter_lifetime_option'] = 15

#non-hybrid
# Inverter_data['eta_inverter_option'] = 0.95
# Inverter_data['P_inverter_max_option'] = 4000
# Inverter_data['inverter_price_option'] = 2300
# Inverter_data['inverter_lifetime_option'] = 15

Battery_data = {}
Battery_data['P_bat_charge_max_option'] = 1280
Battery_data['P_bat_discharge_max_option'] = 1280
Battery_data['E_bat_max_option'] = 0.64
Battery_data['eta_bat_option'] = 0.92
Battery_data['battery_price_option'] = 565
Battery_data['battery_lifetime_option'] = 15

EV_data = {}
#case 1
EV_data['EV average distance traveled per day'] = 23*2+20
EV_data['EV average energy consumption'] =  0.187
EV_average_home_arrival_time = datetime(2018, 1, 1, 17, 0)
EV_data['EV average home arrival time index'] = (EV_average_home_arrival_time.hour)*4-1
EV_average_home_departure_time = datetime(2018, 1, 1, 8, 0)
EV_data['EV average home departure time index'] = (EV_average_home_departure_time.hour)*4-1
EV_data['Max charge speed convertor'] = 7.6
EV_data['Convertor efficiency'] = 0.98*0.96
EV_data['Max battery capacity'] = 103

P_offtake, P_injection, P_direct_consumption, P_inverter, P_load, E_battery =\
    run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,dynamic_tarrif_case,EV_case,PV_data,Inverter_data,Battery_data,EV_data)


# for day in random.sample(range(365), 30):
# # for day in [124]:
#     P_offtake_day = P_offtake[day,:]
#     P_injection_day = P_injection[day,:]
#     P_direct_consumption_day = P_direct_consumption[day,:]
#     P_inverter_day = P_inverter[day,:]
#     P_load_day = P_load[day,:]
#     E_battery_day = E_battery[day,:]
#     plot_power_modeling_one_day(day,P_load_day,P_inverter_day,P_offtake_day,E_battery_day)
