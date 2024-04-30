import numpy as np
import ephem
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

import os
current_dir = os.getcwd()
# print(current_dir)
project_dir = os.path.dirname(current_dir)
# print(project_dir)

"""#Upload data"""
# solar_data = pd.read_excel('C:/Users/lucas/PycharmProjects/IPE/Irradiance_data.xlsx')
irradiance_data = pd.read_csv(project_dir+'/Data_processing/Output_data/processed_irradiance_data_df.csv')
date_time = irradiance_data['DateTime']
global_horizontal_irradiance = irradiance_data['GlobRad'].to_numpy()
global_diffusive_irradiance = irradiance_data['DiffRad'].to_numpy()

# irradiance_data_old = pd.read_csv(project_dir+'/Data_processing/Input_data/Irradiance_data.csv')
# date_time_old = irradiance_data_old['DateTime']

# print(len(date_time))
# print(global_horizontal_irradiance.shape)
# print(global_diffusive_irradiance.shape)

# print(date_time.shape)

"""#Helper functions"""

def date_time_conversion(date_time_string):

    datetime_obj = datetime.strptime(date_time_string, "%d/%m/%Y %H:%M")
    year = datetime_obj.year
    month = datetime_obj.month
    day = datetime_obj.day
    hour = datetime_obj.hour
    minute = datetime_obj.minute

    dt_input = datetime(year, month, day, hour, minute)

    if dt_input < datetime(2018,3,25,2,0):
        dt_target = dt_input - timedelta(hours=1)
    elif dt_input < datetime(2018,10,28,3,0):
        dt_target = dt_input - timedelta(hours=2)
    else:
        dt_target = dt_input - timedelta(hours=1)
    return dt_target

def get_sun_position(latitude, longitude, date_time):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    # observer.date = date_times
    # observer.date = ephem.date(date_time)
    observer.date = date_time_conversion(date_time)

    sun = ephem.Sun(observer)

    # Azimuth and altitude
    azimuth = sun.az * (180.0 / ephem.pi)  # Convert radians to degrees
    altitude = sun.alt * (180.0 / ephem.pi)  # Convert radians to degrees

    # Zenith angle is 90 degrees minus the altitude
    zenith = 90.0 - altitude

    return zenith, azimuth

# Assuming solar_angle_data is loaded from somewhere, and it contains:
# solar_time_vec, azimuth_degree, zenith_degree

def get_solar_irradiance(irradiance_GHI, irradiance_DHI, south_tilt_degree, east_west_tilt_degree, azimuth_degree, zenith_degree):
    # Convert to radians
    azimuth_rad = np.radians([azimuth_degree])  # Ensure it's an array
    zenith_rad = np.radians([zenith_degree])

    south_tilt_rad = np.radians([south_tilt_degree])  # Ensure it's an array
    east_west_tilt_rad = np.radians([east_west_tilt_degree])

    #the solar position vector calculation
    # solar_position = np.array([np.sin(zenith_rad) * np.sin(azimuth_rad),
    #                            np.sin(zenith_rad) * np.cos(azimuth_rad),
    #                            np.cos(zenith_rad)])
    solar_position = np.array([np.sin(zenith_rad) * np.sin(azimuth_rad),
                               np.sin(zenith_rad) * np.cos(azimuth_rad),
                               np.cos(zenith_rad)]).reshape((3,))
    # print(solar_position)

    # The position of the solar panels
    azimuth_E = np.pi / 2
    azimuth_S = np.pi
    azimuth_W = 3 * np.pi / 2

    panel_E = np.array([np.sin(east_west_tilt_rad) * np.sin(azimuth_E),
                        np.sin(east_west_tilt_rad) * np.cos(azimuth_E),
                        np.cos(east_west_tilt_rad)])
    panel_S = np.array([np.sin(south_tilt_rad) * np.sin(azimuth_S),
                        np.sin(south_tilt_rad) * np.cos(azimuth_S),
                        np.cos(south_tilt_rad)])
    panel_W = np.array([np.sin(east_west_tilt_rad) * np.sin(azimuth_W),
                        np.sin(east_west_tilt_rad) * np.cos(azimuth_W),
                        np.cos(east_west_tilt_rad)])
    # print(panel_E)
    # Calculate the inner product between the solar position vector and the panel orientation vector: gives cosine(alpha)
    # DNI_amplification_E = np.sum(solar_position * panel_E, axis=1)
    # DNI_amplification_S = np.sum(solar_position * panel_S, axis=1)
    # DNI_amplification_W = np.sum(solar_position * panel_W, axis=1)

    DNI_amplification_E = np.dot(solar_position,panel_E)
    DNI_amplification_S = np.dot(solar_position,panel_S)
    DNI_amplification_W = np.dot(solar_position,panel_W)

    # Irradiation from the back does not result in power
    DNI_amplification_E = np.maximum(DNI_amplification_E, 0)
    DNI_amplification_S = np.maximum(DNI_amplification_S, 0)
    DNI_amplification_W = np.maximum(DNI_amplification_W, 0)

    # Calculate the Direct Normal Irradiance (DNI)
    DNI = (irradiance_GHI - irradiance_DHI) / np.cos(zenith_rad)
    DNI[zenith_degree > 88] = 0
    DNI = np.maximum(DNI, 0)

    # Calculating total irradiance on PV panels under given tilt
    Irrad_solarpanelE = irradiance_DHI + DNI * DNI_amplification_E
    Irrad_solarpanelS = irradiance_DHI + DNI * DNI_amplification_S
    Irrad_solarpanelW = irradiance_DHI + DNI * DNI_amplification_W
    # print(f'DNI is: {DNI}')
    # print(f'DNI amplification East: {DNI_amplification_E}')
    # print(f'DNI amplification South: {DNI_amplification_S}')
    # print(f'DNI amplification West: {DNI_amplification_W}')

    # return Irrad_solarpanelE.item(), Irrad_solarpanelS.item(), Irrad_solarpanelW.item()
    return Irrad_solarpanelE, Irrad_solarpanelS, Irrad_solarpanelW

def plot_irradiance_profile_for_different_panel_orientations(total_irradiance_df):
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_East'], label='East', color='blue')
    plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_South'], label='South', color='red')
    plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_West'], label='West', color='orange')

    plt.title('Irradiance profile for different panel orientations')
    plt.xlabel('Time')
    plt.ylabel('Irradiance [W/m²]')
    plt.legend()  # Add a legend
    # plt.grid(True)  # Add a grid
    plt.tight_layout()  # Fit the plot nicely into the figure
    plt.show()

def plot_irradiance_profiles_for_different_panel_orientations_for_one_day(total_irradiance,day):

    total_irradiance_E = total_irradiance[0,:].reshape(365,24*60)
    total_irradiance_S = total_irradiance[1,:].reshape(365,24*60)
    total_irradiance_W = total_irradiance[2,:].reshape(365,24*60)
    x=[i*60 for i in range(24)]
    l=[]
    for i in range(24):
          l.append("%s:00"%i)
          # l.append(" ")
    plt.figure(figsize=(8, 6))  # Set the figure size
    plt.xticks(x,l,fontsize=10, rotation=60)
    plt.plot(total_irradiance_E[day,:],label='East', color='blue')
    plt.plot(total_irradiance_S[day,:],label='South', color='red')
    plt.plot(total_irradiance_W[day,:], label='West', color='orange')
    plt.title(f'Irradiance profile for different panel orientations on day {day}')
    plt.xlabel('Time')
    plt.ylabel('Irradiance [W/m²]')
    plt.legend()  # Add a legend
    # plt.grid(True)  # Add a grid
    plt.tight_layout()  # Fit the plot nicely into the figure
    plt.show()

"""#Case study"""

latitude = 50.99461
longitude = 5.53972
south_tilt_angle = 40
east_west_tilt_angle = 10

#for one instance


one_instance_case = False
if one_instance_case:

    day = 124
    # day = 124 - 14
    granularity = 60
    j= 15*26
    i = day*24*60+j*int(60/granularity)
    # i = day*24*60+j*int(60/granularity) - 7*60 - 6

    exact_moment = date_time[i]
    # exact_moment = date_time_old[i]
    print(f'exact moment is: {exact_moment}')
    zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
    print(f'zenith angle is: {zenith_angle}')
    print(f'azimuth angle is: {azimuth_angle}')
    GHI = global_horizontal_irradiance[i]
    print(f'GHI is: {GHI}')
    DHI = global_diffusive_irradiance[i]
    print(f'DHI is: {DHI}')
    total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,south_tilt_angle,east_west_tilt_angle,azimuth_angle,zenith_angle)
    print(f'Total irradiance is: {total_irradiance_W}')

#for one day
one_day_case = False
if one_day_case:
    granularity = 4

    # day = 129

    for day in random.sample(range(365), 50):
    # for day in [100]:
        total_irradiance = np.zeros((3,24*granularity))
        zenits = np.zeros((24*granularity))
        azimuths = np.zeros((24*granularity))


        for j in range(24*granularity):
            i = day*24*60+j*int(60/granularity)
            exact_moment = date_time[i]
            zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
            GHI = global_horizontal_irradiance[i]
            DHI = global_diffusive_irradiance[i]
            total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,south_tilt_angle,east_west_tilt_angle,azimuth_angle,zenith_angle)
            # total_irradiance.append([exact_moment,total_irradiance_E,total_irradiance_S,total_irradiance_W])
            # total_irradiance[0,i] = exact_moment
            total_irradiance[0,j] = total_irradiance_E
            total_irradiance[1,j] = total_irradiance_S
            total_irradiance[2,j] = total_irradiance_W
            zenits[j] = zenith_angle
            azimuths[j] = azimuth_angle

        # print(np.argmax(total_irradiance[2,:]))

        x=[i*granularity for i in range(24)]
        l=[]
        for i in range(24):
              l.append("%s:00"%i)
              # l.append(" ")
        plt.figure(figsize=(8, 6))  # Set the figure size
        plt.xticks(x,l,fontsize=10, rotation=60)
        plt.plot(total_irradiance[0,:],label='East', color='blue')
        plt.plot(total_irradiance[1,:],label='South', color='red')
        plt.plot(total_irradiance[2,:], label='West', color='orange')
        plt.title(f'Irradiance profile for different panel orientations on day {day}')
        plt.xlabel('Time')
        plt.ylabel('Irradiance [W/m²]')
        plt.legend()  # Add a legend
        # plt.grid(True)  # Add a grid
        plt.tight_layout()  # Fit the plot nicely into the figure
        output_file_path = f'Output_data/figures/plot_irradiance_profiles_for_different_panel_orientations_for_one_day_{day}'
        plt.savefig(output_file_path)
        # plt.show()

        # x=[i*granularity for i in range(24)]
        # l=[]
        # for i in range(24):
        #       l.append("%s:00"%i)
        #       # l.append(" ")
        # plt.figure(figsize=(8, 6))  # Set the figure size
        # plt.xticks(x,l,fontsize=10, rotation=60)
        # plt.plot(zenits,label='zeniths', color='blue')
        # plt.plot(azimuths,label='azimuths', color='red')
        # # plt.title(f'Irradiance profile for different panel orientations on day {day}')
        # plt.xlabel('Time')
        # # plt.ylabel('Irradiance [W/m²]')
        # plt.legend()  # Add a legend
        # # plt.grid(True)  # Add a grid
        # plt.tight_layout()  # Fit the plot nicely into the figure
        # output_file_path = f'Output_data/figures/plot_zenit_profiles_for_different_panel_orientations_for_one_day_{day}'
        # # plt.savefig(output_file_path)
        # # plt.show()

#for all days
all_days_case = True
if all_days_case:
    south_tilt_angle = -45
    # total_irradiance = np.zeros((3,date_time.shape[0]))
    total_irradiance_N = np.zeros(date_time.shape[0])
    print(date_time.shape[0])
    for i in range(date_time.shape[0]):
        exact_moment = date_time[i]
        zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
        GHI = global_horizontal_irradiance[i]
        DHI = global_diffusive_irradiance[i]
        total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,south_tilt_angle,east_west_tilt_angle,azimuth_angle,zenith_angle)
        # total_irradiance[0,i] = total_irradiance_E
        # total_irradiance[1,i] = total_irradiance_S
        # total_irradiance[2,i] = total_irradiance_W
        total_irradiance_N[i] = total_irradiance_S

    # print(total_irradiance)

    # # Convert the np.arrays to a DataFrame
    # total_irradiance_df = pd.DataFrame({'DateTime': date_time})
    # total_irradiance_df['Irradiance_East'] = total_irradiance[0,:]
    # total_irradiance_df['Irradiance_South'] = total_irradiance[1,:]
    # total_irradiance_df['Irradiance_West'] = total_irradiance[2,:]

    np.save('Output_data/total_irradiance_per_angle_N/total_irradiance_for_tilt_angle_45',total_irradiance_N)



#for all angles
all_angles_case = False
if all_angles_case:

    tilt_angles = range(91)

    total_irradiance_for_all_angles = np.zeros((len(tilt_angles),3,date_time.shape[0]))

    for tilt_angle in tilt_angles:
        total_irradiance = np.zeros((3,date_time.shape[0]))
        for i in range(date_time.shape[0]):
            exact_moment = date_time[i]
            zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
            GHI = global_horizontal_irradiance[i]
            DHI = global_diffusive_irradiance[i]
            total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,tilt_angle,tilt_angle,azimuth_angle,zenith_angle)
            total_irradiance[0,i] = total_irradiance_E
            total_irradiance[1,i] = total_irradiance_S
            total_irradiance[2,i] = total_irradiance_W
        np.save(f'Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{tilt_angle}',total_irradiance)
        total_irradiance_for_all_angles[tilt_angle,:,:] = total_irradiance
        print(f"Finished total irradiance calculations of tilt_angle {tilt_angle+1}/{len(tilt_angles)}")

    # np.save('Output_data/total_irradiance_for_all_angles',total_irradiance_for_all_angles)

all_angles_case_fast = False
if all_angles_case_fast:

    tilt_angles = range(91)
    granularity = 1
    time_steps = 365*24*granularity

    total_irradiance_for_all_angles_fast = np.zeros((len(tilt_angles),3,time_steps))

    for tilt_angle in tilt_angles:
        total_irradiance = np.zeros((3,time_steps))
        for i in range(time_steps):
            exact_moment = date_time[i]
            zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
            GHI = global_horizontal_irradiance[i]
            DHI = global_diffusive_irradiance[i]
            total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,tilt_angle,tilt_angle,azimuth_angle,zenith_angle)
            total_irradiance[0,i] = total_irradiance_E
            total_irradiance[1,i] = total_irradiance_S
            total_irradiance[2,i] = total_irradiance_W
        total_irradiance_for_all_angles_fast[tilt_angle,:,:] = total_irradiance
        print(f"Finished total irradiance calculations of tilt_angle {tilt_angle+1}/{len(tilt_angles)}")

    total_incoming_energy_for_all_angles_fast = np.sum(total_irradiance_for_all_angles_fast,axis=2)*60*int(60/granularity)/3600/1000
    print(f'Optimal angle East: {np.argmax(total_incoming_energy_for_all_angles_fast[:,0])} degrees')
    print(f'Optimal angle South: {np.argmax(total_incoming_energy_for_all_angles_fast[:,1])} degrees')
    print(f'Optimal angle West: {np.argmax(total_incoming_energy_for_all_angles_fast[:,2])} degrees')

    x=[i*10 for i in range(10)]
    plt.figure(figsize=(8, 6))  # Set the figure size
    plt.xticks(x,x,fontsize=10)
    plt.plot(total_incoming_energy_for_all_angles_fast[:,0],label='East', color='blue')
    plt.plot(total_incoming_energy_for_all_angles_fast[:,1],label='South', color='red')
    plt.plot(total_incoming_energy_for_all_angles_fast[:,2], label='West', color='orange')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.title(f'Yearly solar energy yield in function of varying tilt angles')
    plt.xlabel('Tilt angle [degrees]')
    plt.ylabel('Solar incoming energy [kWh/m²]')
    plt.legend()  # Add a legend
    # plt.grid(True)  # Add a grid
    # plt.tight_layout()  # Fit the plot nicely into the figure
    output_file_path = f'Output_data/figures/yearly_solar_energy_yield_per_angle_fast_granularity_{granularity}'
    plt.savefig(output_file_path)
    # plt.show()

"""# Optimal angle calculation"""
# #for all tilt angles werkt niet (OSError: 143488800 requested and 35056128 written)?
# total_irradiance_for_all_angles = np.load('Output_data/total_irradiance_for_all_angles.npy')

# #per tilt angle
# tilt_angles = range(91)
# total_irradiance_for_all_angles = np.zeros((len(tilt_angles),3,date_time.shape[0]))
# for tilt_angle in range(len(tilt_angles)):
#     total_irradiance_angle = np.load(f'Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{tilt_angle}.npy')
#     total_irradiance_for_all_angles[tilt_angle,:,:] = total_irradiance_angle
#
#
# #integrate
# #kWh/m^2
# total_incoming_energy_for_all_angles = np.sum(total_irradiance_for_all_angles,axis=2)/60/1000
# print(total_incoming_energy_for_all_angles.shape)
# print(f'Optimal angle East: {np.argmax(total_incoming_energy_for_all_angles[:,0])} degrees')
# print(f'Optimal angle South: {np.argmax(total_incoming_energy_for_all_angles[:,1])} degrees')
# print(f'Optimal angle West: {np.argmax(total_incoming_energy_for_all_angles[:,2])} degrees')
#
# x=[i*10 for i in range(10)]
# l=[10*i for i in x]
# l=[]
# for i in range(24):
#       l.append("%s:00"%i)
#       l.append(" ")
#
# plt.figure(figsize=(8, 6))  # Set the figure size
# plt.xticks(x,x,fontsize=10)
# plt.plot((total_incoming_energy_for_all_angles[:,0]+total_incoming_energy_for_all_angles[:,2])/2,label='East-West', color='blue')
# # plt.plot(total_incoming_energy_for_all_angles[:,0],label='East', color='blue')
# plt.plot(total_incoming_energy_for_all_angles[:,1],label='South', color='red')
# # plt.plot(total_incoming_energy_for_all_angles[:,2], label='West', color='orange')
# plt.xlim(left=0)
# plt.ylim(bottom=0)
# plt.title(f'Yearly solar energy yield in function of varying tilt angles')
# plt.xlabel('Tilt angle [degrees]')
# plt.ylabel('Solar incoming energy [kWh/m²]')
# plt.legend()  # Add a legend
# # plt.grid(True)  # Add a grid
# plt.tight_layout()  # Fit the plot nicely into the figure
# output_file_path = f'Output_data/figures/yearly_solar_energy_yield_per_angle_EW'
# # plt.savefig(output_file_path)
# # plt.show()


"""#Plotting"""
#One day case

#All days case
# plot_irradiance_profile_for_different_panel_orientations(total_irradiance_df)

# plot_irradiance_profiles_for_different_panel_orientations_for_one_day(total_irradiance,10)

#All angles case
