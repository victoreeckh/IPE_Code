import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)


"""# Defining system parameters"""
Flat_roof = True
Battery_case = True
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

#Battery characteristics (SMA Home Storage 3.2)
P_bat_charge_max = 7500 #W
P_bat_discharge_max = 6000 #W (From inverter datasheets??)
E_bat_max = 10 #kWh (medium battery)
eta_bat = 0.945

"""# Download data"""

#from single GTI files
GTI_EW = np.load(project_dir+\
            f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_east_west_tilt_angle}.npy')
GTI_E = GTI_EW[0,:].reshape(365,24,60)
GTI_W = GTI_EW[2,:].reshape(365,24,60)

GTI_S = np.load(project_dir+\
            f'/effective_irradiance/Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{optimal_south_tilt_angle}.npy')
GTI_S = GTI_S[1,:].reshape(365,24,60)

#load data
# P_load = np.load(project_dir+'/Data_processing/Output_data/processed_load_data.npy')
processed_load_data_df = pd.read_csv(project_dir+'/Data_processing/Output_data/processed_load_data_df.csv')
P_load_array = processed_load_data_df['load data'].to_numpy()*1000 #Watt
print(np.sum(P_load_array,axis=0)/1000*0.25)

#Cell temperature data
T_CommRoof = np.load(project_dir+'/Data_processing/Output_data/processed_T_CommRoof_data.npy')
T_RV = np.load(project_dir+'/Data_processing/Output_data/processed_T_RV_data.npy')


"""# Power modeling calculations"""

#Cases are binary permutations of (roof_tilt,orientation,battery use)=2^3=8 cases

if Flat_roof:
    T_cell = T_CommRoof
else:
    T_cell = T_RV

eta_temp = 1 - beta_ref*(T_cell-T_ref)
eta_panel = eta_cell * eta_shade * eta_obstruct * eta_temp * eta_degrad
eta_panel = eta_panel.reshape(365,24,60)
# print(eta_panel.shape)

if Southern_orientation_case:
    GTI = GTI_S
else:
    GTI = GTI_E      #klopt dit?

P_sun = GTI*n*A                                                     #(365,24,60)
P_panel = P_sun*eta_panel                                           #Element wise product

P_inverter = eta_inverter*P_panel

P_inverter_array = P_inverter[:,:,::15].reshape(365*96)

delta_t = 15*60

if not Battery_case:
    P_offtake = P_load_array - P_inverter_array
    P_injection = - P_offtake
    P_battery = np.zeros(P_offtake.shape)

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
                    P_injection = P_excess - P_bat_charge
                else:
                    P_bat_charge = P_excess
                    E_bat += (P_bat_charge/1000)*(delta_t/3600)                   #charge battery
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
                    P_offtake = P_short - P_bat_discharge
                else:
                    P_bat_discharge = P_short
                    E_bat -= (P_bat_discharge/1000)*(delta_t/3600)                #discharge battery
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


# print(P_offtake_array.shape)

# plot

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

    output_file_path = f'Output_data/figures/plot_power_modeling_one_day_{day}'
    plt.savefig(output_file_path)
    # plt.show()


for day in random.sample(range(365), 30):
# for day in [1]:
    P_offtake_day = P_offtake[day,:]
    P_injection_day = P_injection[day,:]
    P_direct_consumption_day = P_direct_consumption[day,:]
    P_inverter_day = P_inverter[day,:]
    P_load_day = P_load[day,:]
    E_battery_day = E_battery[day,:]
    plot_power_modeling_one_day(day,P_load_day,P_inverter_day,P_offtake_day,E_battery_day)
