import numpy as np
import pandas as pd
import csv
from datetime import datetime

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)

def extract_prices_from_2018(file_path):

    prices_2018 = [] #prices change every hour but are repeated four times to match the quarterly demand

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract the year from the 'Datetime (UTC)' column
            date_utc = datetime.strptime(row['Datetime (UTC)'], '%Y-%m-%d %H:%M:%S')
            if date_utc.year == 2018:
                # If the year is 2018, append the price to the list
                price = float(row['Price (EUR/MWhe)'])
                prices_2018.extend([price] * 4)

    return prices_2018


def multiply_and_sum_lists(list1, list2):

    if len(list1) != len(list2):
        raise ValueError("The two lists must be of the same length.")

    # Multiply the elements pairwise and sum the results
    return sum(x * y for x, y in zip(list1, list2))

#nighttarrif is every weekday from 22u to 7 u and the whole weekend active
#the VAT is already included in the tarrifs according to the documents of Engie
def get_electricity_bill(P_offtake, P_injection, dynamic_tarrif, EV_case):

    E_offtake = P_offtake/1000*0.25      #W ->kWh
    E_injection = P_injection/1000*0.25

    total_consumption_profile = E_offtake.flatten().tolist()
    total_injection_profile = E_injection.flatten().tolist()
    total_consumption = np.sum(E_offtake.flatten())

    E_offtake = E_offtake.reshape(365,24,4)
    all_indices = np.arange(365)
    mask = np.logical_or((all_indices % 7 == 6),(all_indices % 7 == 5))
    E_offtake_weekends = E_offtake[mask,:,:]
    E_offtake_weekdays = E_offtake[1-mask,:,:]

    consumption_day = np.sum(E_offtake_weekdays[:,7:22,:].flatten(),axis=0)
    consumption_night = np.sum(E_offtake_weekends.flatten(),axis=0) + np.sum(E_offtake_weekdays[:,:7,:].flatten(),axis=0) + np.sum(E_offtake_weekdays[:,22:,:].flatten(),axis=0)

    E_injection = E_injection.reshape(365,24,4)
    E_injection_weekends = E_injection[mask,:,:]
    E_injection_weekdays = E_injection[1-mask,:,:]

    injection_day = np.sum(E_injection_weekdays[:,7:22,:].flatten(),axis=0)
    injection_night = np.sum(E_injection_weekends.flatten(),axis=0) + np.sum(E_injection_weekdays[:,:7,:].flatten(),axis=0) + np.sum(E_injection_weekdays[:,22:,:].flatten(),axis=0)

    # Slicing the net_load_profile array to get monthly data
    kW_jan = total_consumption_profile[0:2976]
    kW_feb = total_consumption_profile[2976:5664]
    kW_mar = total_consumption_profile[5664:8640]
    kW_apr = total_consumption_profile[8640:11520]
    kW_may = total_consumption_profile[11520:14496]
    kW_jun = total_consumption_profile[14496:17376]
    kW_jul = total_consumption_profile[17376:20352]
    kW_aug = total_consumption_profile[20352:23328]
    kW_sep = total_consumption_profile[23328:26208]
    kW_oct = total_consumption_profile[26208:29184]
    kW_nov = total_consumption_profile[29184:32064]
    kW_dec = total_consumption_profile[32064:35040]

    # Finding the peak (maximum) value for each month
    peak_jan = np.max(kW_jan)
    peak_feb = np.max(kW_feb)
    peak_mar = np.max(kW_mar)
    peak_apr = np.max(kW_apr)
    peak_may = np.max(kW_may)
    peak_jun = np.max(kW_jun)
    peak_jul = np.max(kW_jul)
    peak_aug = np.max(kW_aug)
    peak_sep = np.max(kW_sep)
    peak_oct = np.max(kW_oct)
    peak_nov = np.max(kW_nov)
    peak_dec = np.max(kW_dec)

    # Calculating the average of the monthly peaks
    average_peak = (peak_jan + peak_feb + peak_mar + peak_apr + peak_may + peak_jun + peak_jul + peak_aug + peak_sep + peak_oct + peak_nov + peak_dec) / 12


    if dynamic_tarrif == False:
        if EV_case != 0:
            fixed_fee = 100.7 #eur/y
            consumption_price_day = 0.15883 #eur/kWh
            consumption_price_night = 0.11251  # eur/kWh
            injection_price_day = 0.0223  # eur/kWh
            injection_price_night = 0.00979  # eur/kWh
            cost_green_energy_and_WKK = 0.01582#eur/kWh

            #networkcosts
            if average_peak < 2.5:
                capacity_tariff_cost = 41.3087 *2.5 #eur/y
            else:
                capacity_tariff_cost = 41.3087 * average_peak #eur/y
            total_kwh_network_tarrif = 0.0538613 #eur/kwh
            data_processing_fee = 15.14 #eur/y

            #taxes and levies
            energy_allowance = 0.0020417 #eur/kwh
            federal_excise = 0.0503288 #eur/kwh    consumtion is around 3.1MWh


            total_price = fixed_fee + consumption_price_day*consumption_day + consumption_price_night*consumption_night - injection_price_day*injection_day - injection_price_night*injection_night + cost_green_energy_and_WKK*total_consumption + capacity_tariff_cost + total_kwh_network_tarrif*total_consumption + data_processing_fee + energy_allowance*total_consumption + federal_excise*total_consumption
            return total_price

        else:
            fixed_fee = 61.48  # eur/y
            consumption_price_day = 0.16014  # eur/kWh
            consumption_price_night = 0.13558  # eur/kWh
            injection_price_day = 0.0223  # eur/kWh
            injection_price_night = 0.00979  # eur/kWh
            cost_green_energy_and_WKK = 0.01582  # eur/kWh

            # networkcosts
            if average_peak < 2.5:
                capacity_tariff_cost = 41.3087 * 2.5  # eur/y
            else:
                capacity_tariff_cost = 41.3087 * average_peak  # eur/y
            total_kwh_network_tarrif = 0.0538613  # eur/kwh
            data_processing_fee = 15.14  # eur/y

            # taxes and levies
            energy_allowance = 0.0020417  # eur/kwh
            federal_excise = 0.0503288  # eur/kwh    consumtion is around 3.1MWh

            total_price = fixed_fee + consumption_price_day * consumption_day + consumption_price_night * consumption_night - injection_price_day * injection_day - injection_price_night * injection_night + cost_green_energy_and_WKK * total_consumption + capacity_tariff_cost + total_kwh_network_tarrif * total_consumption + data_processing_fee + energy_allowance * total_consumption + federal_excise * total_consumption
            return total_price


    if dynamic_tarrif == True:
        fixed_fee = 100.7  # eur/y
        # Define the path to your CSV file
        file_path = project_dir+'/Power_modeling/Input_data/Belgium.csv'

        # Call the function and get the prices for 2018
        prices_2018 = extract_prices_from_2018(file_path)
        consumption_prices = [(1.1+0.1*x)/100 for x in prices_2018] # eur/kWh
        injection_prices = [(-0.9050 +0.1*x)/100 for x in prices_2018]  # eur/kWh
        cost_green_energy_and_WKK = 0.01582  # eur/kWh

        # networkcosts
        if average_peak < 2.5:
            capacity_tariff_cost = 41.3087 * 2.5  # eur/y
        else:
            capacity_tariff_cost = 41.3087 * average_peak  # eur/y
        total_kwh_network_tarrif = 0.0538613  # eur/kwh
        data_processing_fee = 15.14  # eur/y

        # taxes and levies
        energy_allowance = 0.0020417  # eur/kwh
        federal_excise = 0.0503288  # eur/kwh    consumtion is around 3.1MWh

        total_price = fixed_fee + multiply_and_sum_lists(consumption_prices,total_consumption_profile) - multiply_and_sum_lists(injection_prices,total_injection_profile) + cost_green_energy_and_WKK * total_consumption + capacity_tariff_cost + total_kwh_network_tarrif * total_consumption + data_processing_fee + energy_allowance * total_consumption + federal_excise * total_consumption
        return total_price


# P_offtake = np.load(project_dir+'/Power_modeling/Output_data/P_offtake.npy')
# P_injection = np.load(project_dir+'/Power_modeling/Output_data/P_injection.npy')


"""#Tests """
# prices_2018 = np.array(extract_prices_from_2018(project_dir+'/Power_modeling/Input_data/Belgium.csv'))
# print(prices_2018.shape)
# print(f'Mean is: {np.mean(prices_2018)}')
# print(f'Median is: {np.median(prices_2018)}')
# print(f'Q1 is: {np.percentile(prices_2018,25)}')
# print(f'Q3 is: {np.percentile(prices_2018,75)}')
# print(f'Max is: {np.max(prices_2018)}')
# print(f'Min is: {np.min(prices_2018)}')


# print(f'{get_electricity_bill(P_offtake, P_injection, False, False):.2f}')
# print(f'{get_electricity_bill(P_offtake, P_injection, True, False):.2f}')
# print(f'{get_electricity_bill(P_offtake, P_injection, False, True):.2f}')
# print(f'{get_electricity_bill(P_offtake, P_injection, True, True):.2f}')
