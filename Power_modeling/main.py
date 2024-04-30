import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

from power_modeling_v2 import run_power_modeling
from get_number_of_solar_panels import get_number_of_solar_panels
from price_calculation_v2 import get_electricity_bill
from financial_functions import get_financials

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)

"""
#PV data options
"""
PV_data_options = ['Canadian Solar - HiKu6 Mono PERC',\
                    'Canadian Solar - TOPHiKu6',\
                    'Recom - Mono Cristalline Half Cut Module',\
                    'Recom - Black Tiger',\
                    'Vertex - BIFACIAL DUAL GLASS MONOCRYSTALLINE MODULE',\
                    'Vertex - BACKSHEET MONOCRYSTALLINE MODULE']
l_panel_options = []
w_panel_options = []

P_PV_peak_options = []

eta_cell_options = []
beta_ref_options = []
PV_price_options = []
PV_lifetime_options = []

l_roof = 10
w_roof = 12

#Option 0: Canadian Solar - HiKu6 Mono PERC
l_panel_options.append(2.278)
w_panel_options.append(1.134)
P_PV_peak_options.append(550)
eta_cell_options.append(0.213)
beta_ref_options.append(-0.0034)
PV_price_options.append(212)
PV_lifetime_options.append(25)

#Option 1: Canadian Solar - TOPHiKu6
l_panel_options.append(1.722)
w_panel_options.append(1.134)
P_PV_peak_options.append(430)
eta_cell_options.append(0.22)
beta_ref_options.append(-0.0029)
PV_price_options.append(130)
PV_lifetime_options.append(25)

#Option 2: Recom - Mono Cristalline Half Cut Module
l_panel_options.append(1.724)
w_panel_options.append(1.134)
P_PV_peak_options.append(410)
eta_cell_options.append(0.2097)
beta_ref_options.append(-0.0036)
PV_price_options.append(115)
PV_lifetime_options.append(25)

#Option 3: Recom - Black Tiger
l_panel_options.append(1.722)
w_panel_options.append(1.134)
P_PV_peak_options.append(450)
eta_cell_options.append(0.23)
beta_ref_options.append(-0.0029)
PV_price_options.append(130.6)
PV_lifetime_options.append(25)

#Option 4: Vertex - BIFACIAL DUAL GLASS MONOCRYSTALLINE MODULE
l_panel_options.append(2.172)
w_panel_options.append(1.303)
P_PV_peak_options.append(600)
eta_cell_options.append(0.212)
beta_ref_options.append(-0.0034)
PV_price_options.append(222)
PV_lifetime_options.append(25)

#Option 5: Vertex - BACKSHEET MONOCRYSTALLINE MODULE
l_panel_options.append(1.762)
w_panel_options.append(1.134)
P_PV_peak_options.append(425)
eta_cell_options.append(0.213)
beta_ref_options.append(-0.0034)
PV_price_options.append(119.8)
PV_lifetime_options.append(25)


PV_data = {}

"""
#Inverter data options
"""
Inverter_data_options = []
eta_inverter_options = []
P_inverter_max_options = []
inverter_price_options = []
inverter_lifetime_options = []

Hybrid_Inverter_data_options = []
eta_hybrid_inverter_options = []
P_hybrid_inverter_max_options = []
hybrid_inverter_price_options = []
hybrid_inverter_lifetime_options = []

#Option 0: Victron Energy - Inverter RS Smart Solar 48/6000
Inverter_data_options.append('Victron Energy - Inverter RS Smart Solar 48/6000')
eta_inverter_options.append(0.95)
P_inverter_max_options.append(4000)
inverter_price_options.append(2300)
inverter_lifetime_options.append(15)

#Option 0: Victron Energy - Multi RS Solar 48/6000 Hybride omvormer
Hybrid_Inverter_data_options.append('Victron Energy - Multi RS Solar 48/6000 Hybride omvormer')
eta_hybrid_inverter_options.append(0.95)
P_hybrid_inverter_max_options.append(6000)
hybrid_inverter_price_options.append(3000)
hybrid_inverter_lifetime_options.append(15)

#Option 1: SMA - Sunny Boy mit SMA Smart Connected - 3000W
Inverter_data_options.append('SMA - Sunny Boy mit SMA Smart Connected - 3000W')
eta_inverter_options.append(0.964)
P_inverter_max_options.append(5500)
inverter_price_options.append(1318)
inverter_lifetime_options.append(15)

#Option 1: SMA - Sunny Tripower Smart Energy (Hybrid) - 5000W
Hybrid_Inverter_data_options.append('SMA - Sunny Tripower Smart Energy (Hybrid) - 5000W')
eta_hybrid_inverter_options.append(0.973)
P_hybrid_inverter_max_options.append(7500)
hybrid_inverter_price_options.append(1900)
hybrid_inverter_lifetime_options.append(15)

#Option 2: SMA - Sunny Boy mit SMA Smart Connected - 3680W
Inverter_data_options.append('SMA - Sunny Boy mit SMA Smart Connected - 3680W')
eta_inverter_options.append(0.965)
P_inverter_max_options.append(5500)
inverter_price_options.append(1535)
inverter_lifetime_options.append(15)

#Option 2: SMA - Sunny Tripower Smart Energy (Hybrid) - 6000W
Hybrid_Inverter_data_options.append('SMA - Sunny Tripower Smart Energy (Hybrid) - 5000W')
eta_hybrid_inverter_options.append(0.975)
P_hybrid_inverter_max_options.append(9000)
hybrid_inverter_price_options.append(2120)
hybrid_inverter_lifetime_options.append(15)

#Option 3: SMA - Sunny Boy mit SMA Smart Connected - 4000W
Inverter_data_options.append('SMA - Sunny Boy mit SMA Smart Connected - 4000W')
eta_inverter_options.append(0.965)
P_inverter_max_options.append(7500)
inverter_price_options.append(1473)
inverter_lifetime_options.append(15)

#Option 3: SMA - Sunny Tripower Smart Energy (Hybrid) - 8000W
Hybrid_Inverter_data_options.append('SMA - Sunny Tripower Smart Energy (Hybrid) - 8000W')
eta_hybrid_inverter_options.append(0.978)
P_hybrid_inverter_max_options.append(12000)
hybrid_inverter_price_options.append(2550)
hybrid_inverter_lifetime_options.append(15)

#Option 4: SMA - Sunny Boy mit SMA Smart Connected - 5000W
Inverter_data_options.append('SMA - Sunny Boy mit SMA Smart Connected - 5000W')
eta_inverter_options.append(0.965)
P_inverter_max_options.append(7500)
inverter_price_options.append(1580)
inverter_lifetime_options.append(15)

#Option 4: SMA - Sunny Tripower Smart Energy (Hybrid) - 10000W
Hybrid_Inverter_data_options.append('SMA - Sunny Tripower Smart Energy (Hybrid) - 10000W')
eta_hybrid_inverter_options.append(0.975)
P_hybrid_inverter_max_options.append(15000)
hybrid_inverter_price_options.append(2850)
hybrid_inverter_lifetime_options.append(15)

#Option 5: SMA - Sunny Boy mit SMA Smart Connected - 6000W
Inverter_data_options.append('SMA - Sunny Boy mit SMA Smart Connected - 6000W')
eta_inverter_options.append(0.966)
P_inverter_max_options.append(9000)
inverter_price_options.append(1590)
inverter_lifetime_options.append(15)

Inverter_data = {}

"""
#Battery data options
"""
Battery_data_options = ['Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 0.640kWh',\
                        'Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 1.28kWh',\
                        'Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 4.22kWh',\
                        'Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 2.56kWh',\
                        'Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 5.12kWh',\
                        'SMA - SMA Home Storage - 3.28kWh',\
                        'SMA - SMA Home Storage - 6.56kWh',\
                        'SMA - SMA Home Storage - 9.84kWh',\
                        'SMA - SMA Home Storage - 13.12kWh',\
                        'SMA - SMA Home Storage - 16.4kWh']
P_bat_charge_max_options = [] #W
P_bat_discharge_max_options = [] #W
E_bat_max_options = [] #kWh
eta_bat_options = []

battery_price_options = []
battery_lifetime_options = []

# Option 0: Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 0.640kWh
P_bat_charge_max_options.append(1280)
P_bat_discharge_max_options.append(1280)
E_bat_max_options.append(0.64)
eta_bat_options.append(0.92)
battery_price_options.append(565)
battery_lifetime_options.append(15)

# Option 1: Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 1.28kWh
P_bat_charge_max_options.append(2560)
P_bat_discharge_max_options.append(2560)
E_bat_max_options.append(1.28)
eta_bat_options.append(0.92)
battery_price_options.append(930)
battery_lifetime_options.append(15)

# Option 2: Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 4.22kWh
P_bat_charge_max_options.append(5120)
P_bat_discharge_max_options.append(5120)
E_bat_max_options.append(4.22)
eta_bat_options.append(0.92)
battery_price_options.append(2300)
battery_lifetime_options.append(15)

# Option 3: Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 2.56kWh
P_bat_charge_max_options.append(5120)
P_bat_discharge_max_options.append(5120)
E_bat_max_options.append(2.56)
eta_bat_options.append(0.92)
battery_price_options.append(1990)
battery_lifetime_options.append(15)

# Option 4: Victron Energy - Lithium-Iron-Phosphate Batteries Smart - 5.12kWh
P_bat_charge_max_options.append(10240)
P_bat_discharge_max_options.append(10240)
E_bat_max_options.append(5.12)
eta_bat_options.append(0.92)
battery_price_options.append(2770)
battery_lifetime_options.append(15)

# Option 5: SMA - SMA Home Storage - 3.28kWh
P_bat_charge_max_options.append(3456)
P_bat_discharge_max_options.append(3456)
E_bat_max_options.append(3.28)
eta_bat_options.append(0.942)
battery_price_options.append(1574)
battery_lifetime_options.append(15)

# Option 6: SMA - SMA Home Storage - 6.56kWh
P_bat_charge_max_options.append(6912)
P_bat_discharge_max_options.append(6912)
E_bat_max_options.append(6.56)
eta_bat_options.append(0.942)
battery_price_options.append(2853)
battery_lifetime_options.append(15)

# Option 7: SMA - SMA Home Storage - 9.84kWh
P_bat_charge_max_options.append(10368)
P_bat_discharge_max_options.append(10368)
E_bat_max_options.append(9.84)
eta_bat_options.append(0.942)
battery_price_options.append(4280)
battery_lifetime_options.append(15)

# Option 8: SMA - SMA Home Storage - 13.12kWh
P_bat_charge_max_options.append(138234)
P_bat_discharge_max_options.append(138234)
E_bat_max_options.append(13.12)
eta_bat_options.append(0.942)
battery_price_options.append(5706)
battery_lifetime_options.append(15)

# Option 9: SMA - SMA Home Storage - 16.4kWh
P_bat_charge_max_options.append(17280)
P_bat_discharge_max_options.append(17280)
E_bat_max_options.append(16.4)
eta_bat_options.append(0.942)
battery_price_options.append(7133)
battery_lifetime_options.append(15)

Battery_data = {}

"""
#EV data
"""
EV_data = {}
#case 1
EV_data['EV average distance traveled per day'] = 20
EV_data['EV average energy consumption'] =  0.2                  #kWh/km
EV_average_home_arrival_time = datetime(2018, 1, 1, 16, 0)
EV_data['EV average home arrival time index'] = (EV_average_home_arrival_time.hour)*4-1
EV_data['Max charge speed'] = 7                                   #kW

#case 2

"""
#Other data options
"""
discount_rate = 0.03            #risk-free rate Belgium
# installation_cost_pct =
"""
#Looping
"""
best_results = {}
best_results['best_NPV'] = -float('inf')
best_results['best_NPV_comp_id'] = None
best_results['best_PBP'] = float('inf')
best_results['best_PBP_comp_id'] = None
best_results['best_ROI'] = 0
best_results['best_ROI_comp_id'] = None
strings_to_print = []
best_results_strings_to_print = []
string_line = '=========================================================================='

nb_cases = 2**5
nb_component_cases = 300
case = 0
for Flat_roof_case in [True,False]:
    for Battery_case in [True,False]:
        for Southern_orientation_case in [True,False]:
            for dynamic_tarrif_case in [True]:
                # for EV_case in [True,False]:
                # for EV_case in [0,1,2,3]:
                for EV_case in [1]:
                    case_id = str(int(Flat_roof_case))+str(int(Battery_case))+str(int(Southern_orientation_case))+str(int(dynamic_tarrif_case))+str(int(EV_case))
                    strings_to_print.append(string_line)
                    strings_to_print.append(string_line)
                    strings_to_print.append(f'Current case id: {case_id}')
                    strings_to_print.append(f'Flat roof?: {Flat_roof_case}')
                    strings_to_print.append(f'Battery case?: {Battery_case}')
                    strings_to_print.append(f'Southern orientation case?: {Southern_orientation_case}')
                    strings_to_print.append(f'Dynamic tarrif case?: {dynamic_tarrif_case}')
                    strings_to_print.append(f'EV case?: {EV_case}')
                    strings_to_print.append(string_line)
                    print(f'Case {case}/{nb_cases} done, case {case_id}')
                    case+=1
                    component_case = 0
                    for PV_option,PV_option_name in enumerate(PV_data_options):
                        strings_to_print.append(string_line)
                        PV_data['l_panel_option'] = l_panel_options[PV_option]
                        # strings_to_print.append(f'Panel length used: {l_panel_options[PV_option]}')
                        PV_data['w_panel_option'] = w_panel_options[PV_option]
                        # strings_to_print.append(f'Panel width used: {w_panel_options[PV_option]}')
                        PV_data['P_PV_peak_option'] = P_PV_peak_options[PV_option]
                        # strings_to_print.append(f'PV peak value used: {P_PV_peak_options[PV_option]}')
                        PV_data['eta_cell_option'] = eta_cell_options[PV_option]
                        # strings_to_print.append(f'Cell efficiency used: {eta_cell_options[PV_option]}')
                        PV_data['beta_ref_option'] = beta_ref_options[PV_option]
                        # strings_to_print.append(f'Temperature coefficient used (beta): {beta_ref_options[PV_option]}')
                        PV_data['PV_price_option'] = PV_price_options[PV_option]
                        # strings_to_print.append(f'PV price used: {PV_price_options[PV_option]}')
                        PV_data['PV_lifetime_option'] = PV_lifetime_options[PV_option]
                        # strings_to_print.append(f'PV lifetime used: {PV_lifetime_options[PV_option]}')

                        if Battery_case: #-> Hybrid inverter
                            for Hybrid_Inverter_option, Hybrid_Inverter_option_name in enumerate(Hybrid_Inverter_data_options):
                                Inverter_data['eta_inverter_option'] = eta_hybrid_inverter_options[Hybrid_Inverter_option]
                                Inverter_data['P_inverter_max_option'] = P_hybrid_inverter_max_options[Hybrid_Inverter_option]
                                Inverter_data['inverter_price_option'] = hybrid_inverter_price_options[Hybrid_Inverter_option]
                                Inverter_data['inverter_lifetime_option'] = hybrid_inverter_lifetime_options[Hybrid_Inverter_option]

                                for Battery_option,Battery_option_name in enumerate(Battery_data_options):
                                    strings_to_print.append(f'PV component used: {PV_option_name}')
                                    strings_to_print.append(f'Hyrbid inverter component used: {Hybrid_Inverter_option_name}')
                                    strings_to_print.append(f'Battery component used: {Battery_option_name}')
                                    component_id = str(int(PV_option))+str(int(Hybrid_Inverter_option))+str(int(Battery_option))
                                    strings_to_print.append(f'Current component_id id: {component_id}')
                                    print(f'component_case {component_case}/{nb_component_cases} done, componentcase {component_id}')
                                    component_case+=1

                                    Battery_data['P_bat_charge_max_option'] = P_bat_charge_max_options[Battery_option]
                                    Battery_data['P_bat_discharge_max_option'] = P_bat_discharge_max_options[Battery_option]
                                    Battery_data['E_bat_max_option'] = E_bat_max_options[Battery_option]
                                    Battery_data['eta_bat_option'] = eta_bat_options[Battery_option]
                                    Battery_data['battery_price_option'] = battery_price_options[Battery_option]
                                    Battery_data['battery_lifetime_option'] = battery_lifetime_options[Battery_option]

                                    os.makedirs(f'Output_data/results/case_{case_id}/component_case_{component_id}', exist_ok=True)
                                    P_offtake,P_injection,P_direct_consumption,P_inverter,P_load,E_battery = run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,EV_case,PV_data,Inverter_data,Battery_data,EV_data)

                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_offtake',P_offtake)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_injection',P_injection)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_direct_consumption',P_direct_consumption)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_inverter',P_inverter)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_load',P_load)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/E_battery',E_battery)

                                    annual_electricity_bill = get_electricity_bill(P_offtake, P_injection, dynamic_tarrif_case, EV_case)
                                    electricity_bill_base = get_electricity_bill(P_load, np.zeros(P_load.shape), dynamic_tarrif_case, EV_case)
                                    strings_to_print.append(f'Annual electricity bill [EUR]: {annual_electricity_bill:.2f}')
                                    strings_to_print.append(f'Annual electricity bill base [EUR]: {electricity_bill_base:.2f}')

                                    # capex = PV_data['PV_price_option'] + Inverter_data['inverter_price_option'] + Battery_data['battery_price_option']
                                    n = get_number_of_solar_panels(Southern_orientation_case, Flat_roof_case, w_roof, l_roof, w_panel_options[PV_option], l_panel_options[PV_option],PV_data['P_PV_peak_option'],Inverter_data['P_inverter_max_option'])
                                    installation_cost = 25*n
                                    if Flat_roof_case:
                                        installation_cost += 900
                                    else:
                                        installation_cost += 1200
                                    if Battery_case:
                                        installation_cost += 750+1075       #1ste is battery, tweede is connector

                                    Net_present_value, payback_period, return_on_investment, capex = get_financials(n*PV_data['PV_price_option'],\
                                                                                                            PV_data['PV_lifetime_option'],\
                                                                                                            Inverter_data['inverter_price_option'],\
                                                                                                            Inverter_data['inverter_lifetime_option'],\
                                                                                                            Battery_data['battery_price_option'],\
                                                                                                            Battery_data['battery_lifetime_option'],\
                                                                                                            installation_cost,\
                                                                                                            annual_electricity_bill,\
                                                                                                            electricity_bill_base,\
                                                                                                            discount_rate)
                                    if Net_present_value > best_results['best_NPV']:
                                        best_results['best_NPV'] = Net_present_value
                                        best_results['best_NPV_comp_id'] = component_id
                                    if payback_period < best_results['best_PBP']:
                                        best_results['best_PBP'] = payback_period
                                        best_results['best_PBP_comp_id'] = component_id
                                    if return_on_investment>best_results['best_ROI']:
                                        best_results['best_ROI'] = return_on_investment
                                        best_results['best_ROI_comp_id'] = component_id



                                    strings_to_print.append(f'Discount rate used: {discount_rate:.4f}')
                                    strings_to_print.append(f'Number of panels used: {n:.2f}')
                                    strings_to_print.append(f'Capex: {capex:.2f}')
                                    strings_to_print.append(f'Net present value [EUR]: {Net_present_value:.2f}')
                                    strings_to_print.append(f'Payback period [yr]: {payback_period:.2f}')
                                    strings_to_print.append(f'Return on investment: {return_on_investment:.2f}')
                                    strings_to_print.append(string_line)

                                    # with open(f'Output_data/results/case_{case_id}/all_results.txt', 'a') as file:
                                    #     for string in strings_to_print:
                                    #         file.write(string + '\n')

                                    strings_to_print = []
                        else:
                            for Inverter_option, Inverter_option_name in enumerate(Inverter_data_options):
                                Inverter_data['eta_inverter_option'] = eta_inverter_options[Inverter_option]
                                Inverter_data['P_inverter_max_option'] = P_inverter_max_options[Inverter_option]
                                Inverter_data['inverter_price_option'] = inverter_price_options[Inverter_option]
                                Inverter_data['inverter_lifetime_option'] = inverter_lifetime_options[Inverter_option]

                                for Battery_option,Battery_option_name in enumerate(Battery_data_options):
                                    strings_to_print.append(f'PV component used: {PV_option_name}')
                                    strings_to_print.append(f'Inverter component used: {Inverter_option_name}')
                                    strings_to_print.append(f'Battery component used: {Battery_option_name}')
                                    component_id = str(int(PV_option))+str(int(Inverter_option))+str(int(Battery_option))
                                    strings_to_print.append(f'Current component_id id: {component_id}')
                                    print(f'component_case {component_case}/{nb_component_cases} done, componentcase {component_id}')
                                    component_case+=1

                                    Battery_data['P_bat_charge_max_option'] = P_bat_charge_max_options[Battery_option]
                                    Battery_data['P_bat_discharge_max_option'] = P_bat_discharge_max_options[Battery_option]
                                    Battery_data['E_bat_max_option'] = E_bat_max_options[Battery_option]
                                    Battery_data['eta_bat_option'] = eta_bat_options[Battery_option]
                                    Battery_data['battery_price_option'] = battery_price_options[Battery_option]
                                    Battery_data['battery_lifetime_option'] = battery_lifetime_options[Battery_option]

                                    os.makedirs(f'Output_data/results/case_{case_id}/component_case_{component_id}', exist_ok=True)
                                    P_offtake,P_injection,P_direct_consumption,P_inverter,P_load,E_battery = run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,EV_case,PV_data,Inverter_data,Battery_data,EV_data)

                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_offtake',P_offtake)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_injection',P_injection)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_direct_consumption',P_direct_consumption)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_inverter',P_inverter)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_load',P_load)
                                    # np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/E_battery',E_battery)

                                    annual_electricity_bill = get_electricity_bill(P_offtake, P_injection, dynamic_tarrif_case, EV_case)
                                    electricity_bill_base = get_electricity_bill(P_load, np.zeros(P_load.shape), dynamic_tarrif_case, EV_case)
                                    strings_to_print.append(f'Annual electricity bill [EUR]: {annual_electricity_bill:.2f}')
                                    strings_to_print.append(f'Annual electricity bill base [EUR]: {electricity_bill_base:.2f}')

                                    # capex = PV_data['PV_price_option'] + Inverter_data['inverter_price_option'] + Battery_data['battery_price_option']

                                    n = get_number_of_solar_panels(Southern_orientation_case, Flat_roof_case, w_roof, l_roof, w_panel_options[PV_option], l_panel_options[PV_option],PV_data['P_PV_peak_option'],Inverter_data['P_inverter_max_option'])
                                    installation_cost = 25*n
                                    if Flat_roof_case:
                                        installation_cost += 900
                                    else:
                                        installation_cost += 1200
                                    if Battery_case:
                                        installation_cost += 750+1075       #1ste is battery, tweede is connector


                                    Net_present_value, payback_period, return_on_investment, capex = get_financials(n*PV_data['PV_price_option'],\
                                                                                                            PV_data['PV_lifetime_option'],\
                                                                                                            Inverter_data['inverter_price_option'],\
                                                                                                            Inverter_data['inverter_lifetime_option'],\
                                                                                                            Battery_data['battery_price_option'],\
                                                                                                            Battery_data['battery_lifetime_option'],\
                                                                                                            installation_cost,\
                                                                                                            annual_electricity_bill,\
                                                                                                            electricity_bill_base,\
                                                                                                            discount_rate)
                                    if Net_present_value > best_results['best_NPV']:
                                        best_results['best_NPV'] = Net_present_value
                                        best_results['best_NPV_comp_id'] = component_id
                                    if payback_period < best_results['best_PBP']:
                                        best_results['best_PBP'] = payback_period
                                        best_results['best_PBP_comp_id'] = component_id
                                    if return_on_investment>best_results['best_ROI']:
                                        best_results['best_ROI'] = return_on_investment
                                        best_results['best_ROI_comp_id'] = component_id

                                    strings_to_print.append(f'Discount rate used: {discount_rate:.4f}')
                                    strings_to_print.append(f'Number of panels used: {n:.2f}')
                                    strings_to_print.append(f'Capex: {capex:.2f}')
                                    strings_to_print.append(f'Net present value [EUR]: {Net_present_value:.2f}')
                                    strings_to_print.append(f'Payback period [yr]: {payback_period:.2f}')
                                    strings_to_print.append(f'Return on investment: {return_on_investment:.2f}')
                                    strings_to_print.append(string_line)

                                    # with open(f'Output_data/results/case_{case_id}/all_results.txt', 'a') as file:
                                    #     for string in strings_to_print:
                                    #         file.write(string + '\n')

                                    strings_to_print = []

                    best_NPV_comp_id_print = best_results['best_NPV_comp_id']
                    best_NPV_print = best_results['best_NPV']
                    best_PBP_comp_id_print = best_results['best_PBP_comp_id']
                    best_PBP_print = best_results['best_PBP']
                    best_ROI_comp_id_print = best_results['best_ROI_comp_id']
                    best_ROI_print = best_results['best_ROI']
                    best_results_strings_to_print.append(f'Best performing component case regarding NPV: {best_NPV_comp_id_print}')
                    best_results_strings_to_print.append(f'Net present value [EUR]: {best_NPV_print:.2f}')
                    best_results_strings_to_print.append(f'Best performing component case regarding PBP: {best_PBP_comp_id_print}')
                    best_results_strings_to_print.append(f'Payback period [yr]: {best_PBP_print:.2f}')
                    best_results_strings_to_print.append(f'Best performing component case regarding ROI: {best_ROI_comp_id_print}')
                    best_results_strings_to_print.append(f'Return on investment: {best_ROI_print:.2f}')
                    # with open(f'Output_data/results/case_{case_id}/best_results.txt', 'a') as file:
                    #     for string in best_results_strings_to_print:
                    #         file.write(string + '\n')

                    best_results_strings_to_print = []
