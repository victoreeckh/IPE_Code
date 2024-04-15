import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

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
PV_data_options = 3
l_panel_options = [1,1,1]
w_panel_options = [1,1,1]

P_PV_peak_options = [400,400,400]

eta_cell_options = [0.2046,0.2046,0.2046]
beta_ref_options = [-0.0029,-0.0029,-0.0029]
PV_price_options = [183,183,183]
PV_lifetime_options = [25,25,25]

PV_data = {}

"""
#Inverter data options
"""
Inverter_data_options = 3
eta_inverter_options = [0.95,0.95,0.95]
P_inverter_max_options = [900,900,900]

inverter_price_options = [917,917,917]
inverter_lifetime_options = [10,10,10]

Inverter_data = {}

"""
#Battery data options
"""
Battery_data_options = 3
P_bat_charge_max_options = [7500,7500,7500] #W
P_bat_discharge_max_options = [6000,6000,6000] #W
E_bat_max_options = [10,10,10] #kWh
eta_bat_options = [0.95,0.95,0.95]

battery_price_options = [100,100,100]
battery_lifetime_options = [10,10,10]

Battery_data = {}

"""
#Other data options
"""
discount_rate = 0.04
installation_cost = 1000
"""
#Looping
"""
strings_to_print = []
string_line = '=========================================================================='

nb_cases = 2**5
nb_component_cases = 3**3
case = 0
for Flat_roof_case in [True,False]:
    for Battery_case in [True,False]:
        for Southern_orientation_case in [True,False]:
            for dynamic_tarrif_case in [True,False]:
                for EV_case in [True,False]:
                    case_id = str(int(Flat_roof_case))+str(int(Battery_case))+str(int(Southern_orientation_case))+str(int(dynamic_tarrif_case))+str(int(EV_case))
                    strings_to_print.append(string_line)
                    strings_to_print.append(f'Current case id: {case_id}')
                    strings_to_print.append(f'Flat roof?: {Flat_roof_case}')
                    strings_to_print.append(f'Battery case?: {Battery_case}')
                    strings_to_print.append(f'Southern orientation case?: {Southern_orientation_case}')
                    strings_to_print.append(f'Dynamic tarrif case?: {dynamic_tarrif_case}')
                    strings_to_print.append(f'EV case?: {EV_case}')
                    print(f'Case {case}/{nb_cases} done, case {case_id}')
                    case+=1
                    component_case = 0
                    for PV_option in range(PV_data_options):
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

                        for Inverter_option in range(Inverter_data_options):
                            Inverter_data['eta_inverter_option'] = eta_inverter_options[Inverter_option]
                            Inverter_data['P_inverter_max_option'] = P_inverter_max_options[Inverter_option]
                            Inverter_data['inverter_price_option'] = inverter_price_options[Inverter_option]
                            Inverter_data['inverter_lifetime_option'] = inverter_lifetime_options[Inverter_option]

                            for Battery_option in range(Battery_data_options):
                                strings_to_print.append(string_line)
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
                                P_offtake,P_injection,P_direct_consumption,P_inverter,P_load,E_battery = run_power_modeling(Flat_roof_case,Battery_case,Southern_orientation_case,PV_data,Inverter_data,Battery_data)

                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_offtake',P_offtake)
                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_injection',P_injection)
                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_direct_consumption',P_direct_consumption)
                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_inverter',P_inverter)
                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/P_load',P_load)
                                np.save(f'Output_data/results/case_{case_id}/component_case_{component_id}/E_battery',E_battery)

                                annual_electricity_bill = get_electricity_bill(P_offtake, P_injection, dynamic_tarrif_case, EV_case)
                                electricity_bill_base = get_electricity_bill(P_load, np.zeros(P_load.shape), dynamic_tarrif_case, EV_case)
                                strings_to_print.append(f'Annual electricity bill [EUR]: {annual_electricity_bill:.2f}')
                                strings_to_print.append(f'Annual electricity bill base [EUR]: {electricity_bill_base:.2f}')

                                capex = PV_data['PV_price_option'] + Inverter_data['inverter_price_option'] + Battery_data['battery_price_option']

                                Net_present_value, payback_period, return_on_investment = get_financials(PV_data['PV_price_option'],\
                                                                                                        PV_data['PV_lifetime_option'],\
                                                                                                        Inverter_data['inverter_price_option'],\
                                                                                                        Inverter_data['inverter_lifetime_option'],\
                                                                                                        Battery_data['battery_price_option'],\
                                                                                                        Battery_data['battery_lifetime_option'],\
                                                                                                        installation_cost,\
                                                                                                        annual_electricity_bill,\
                                                                                                        electricity_bill_base,\
                                                                                                        discount_rate)
                                strings_to_print.append(f'Discount rate used: {discount_rate:.4f}')
                                strings_to_print.append(f'Net present value [EUR]: {Net_present_value:.2f}')
                                strings_to_print.append(f'Payback period [yr]: {payback_period:.2f}')
                                strings_to_print.append(f'Return on investment: {return_on_investment:.2f}')

                                with open(f'Output_data/results/case_{case_id}/results.txt', 'a') as file:
                                    for string in strings_to_print:
                                        file.write(string + '\n')

                                strings_to_print = []
