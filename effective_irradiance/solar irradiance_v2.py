import numpy as np
import ephem
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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

# print(len(date_time))
# print(global_horizontal_irradiance.shape)
# print(global_diffusive_irradiance.shape)

# print(date_time.shape)

"""#Helper functions"""

def get_sun_position(latitude, longitude, date_time):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    # observer.date = date_time
    observer.date = ephem.date(date_time)

    sun = ephem.Sun(observer)

    # Azimuth and altitude
    azimuth = sun.az * (180.0 / ephem.pi)  # Convert radians to degrees
    altitude = sun.alt * (180.0 / ephem.pi)  # Convert radians to degrees

    # Zenith angle is 90 degrees minus the altitude
    zenith = 90.0 - altitude

    return zenith, azimuth

# Assuming solar_angle_data is loaded from somewhere, and it contains:
# solar_time_vec, azimuth_degree, zenith_degree

def get_solar_irradiance(irradiance_GHI, irradiance_DHI, south_tilt, east_west_tilt, azimuth_degree, zenith_degree):
    # Convert to radians
    azimuth_rad = np.radians([azimuth_degree])  # Ensure it's an array
    zenith_rad = np.radians([zenith_degree])

    #the solar position vector calculation
    solar_position = np.array([np.sin(zenith_rad) * np.sin(azimuth_rad),
                               np.sin(zenith_rad) * np.cos(azimuth_rad),
                               np.cos(zenith_rad)]).T

    # The position of the solar panels
    azimuth_E = np.pi / 2
    azimuth_S = np.pi
    azimuth_W = 3 * np.pi / 2

    panel_E = np.array([np.sin(east_west_tilt) * np.sin(azimuth_E),
                        np.sin(east_west_tilt) * np.cos(azimuth_E),
                        np.cos(east_west_tilt)])
    panel_S = np.array([np.sin(south_tilt) * np.sin(azimuth_S),
                        np.sin(south_tilt) * np.cos(azimuth_S),
                        np.cos(south_tilt)])
    panel_W = np.array([np.sin(east_west_tilt) * np.sin(azimuth_W),
                        np.sin(east_west_tilt) * np.cos(azimuth_W),
                        np.cos(east_west_tilt)])

    # Calculate the inner product between the solar position vector and the panel orientation vector: gives cosine(alpha)
    DNI_amplification_E = np.sum(solar_position * panel_E, axis=1)
    DNI_amplification_S = np.sum(solar_position * panel_S, axis=1)
    DNI_amplification_W = np.sum(solar_position * panel_W, axis=1)

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


#for one day
one_day_case = False
if one_day_case:
    granularity = 4

    total_irradiance = np.zeros((3,24*granularity))
    day = 103

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

    # always the same data? -> no
    # difference = total_irradiance[0,:]-total_irradiance[1,:]
    # print(difference)
    # print(all([i == 0 for i in difference]))

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
    plt.show()

#for all days
all_days_case = False
if all_days_case:

    total_irradiance = np.zeros((3,date_time.shape[0]))
    for i in range(date_time.shape[0]):
        exact_moment = date_time[i]
        zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
        GHI = global_horizontal_irradiance[i]
        DHI = global_diffusive_irradiance[i]
        total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,south_tilt_angle,east_west_tilt_angle,azimuth_angle,zenith_angle)
        total_irradiance[0,i] = total_irradiance_E
        total_irradiance[1,i] = total_irradiance_S
        total_irradiance[2,i] = total_irradiance_W

    # print(total_irradiance)

    # # Convert the np.arrays to a DataFrame
    # total_irradiance_df = pd.DataFrame({'DateTime': date_time})
    # total_irradiance_df['Irradiance_East'] = total_irradiance[0,:]
    # total_irradiance_df['Irradiance_South'] = total_irradiance[1,:]
    # total_irradiance_df['Irradiance_West'] = total_irradiance[2,:]

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

"""# Optimal angle calculation"""
#for all tilt angles werkt niet (OSError: 143488800 requested and 35056128 written)?
# total_irradiance_for_all_angles = np.load('Output_data/total_irradiance_for_all_angles.npy')

#per tilt angle
tilt_angles = range(91)
total_irradiance_for_all_angles = np.zeros((len(tilt_angles),3,date_time.shape[0]))
for tilt_angle in range(len(tilt_angles)):
    total_irradiance_angle = np.load(f'Output_data/total_irradiance_per_angle/total_irradiance_for_tilt_angle_{tilt_angle}.npy')
    total_irradiance_for_all_angles[tilt_angle,:,:] = total_irradiance_angle


#integrate
#kWh/m^2
total_incoming_energy_for_all_angles = np.sum(total_irradiance_for_all_angles,axis=2)/60

# x=[i*10 for i in range(10)]
# # l=[10*i for i in x]
# # l=[]
# # for i in range(24):
# #       l.append("%s:00"%i)
#       # l.append(" ")
#
# plt.figure(figsize=(8, 6))  # Set the figure size
# plt.xticks(x,x,fontsize=10)
# plt.plot(total_incoming_energy_for_all_angles[:,0],label='East', color='blue')
# plt.plot(total_incoming_energy_for_all_angles[:,1],label='South', color='red')
# plt.plot(total_incoming_energy_for_all_angles[:,2], label='West', color='orange')
# plt.xlim(left=0)
# plt.ylim(bottom=0)
# plt.title(f'Yearly solar energy yield in function of varying tilt angles')
# plt.xlabel('Tilt angle [degrees]')
# plt.ylabel('Solar incoming energy [kWh/m²]')
# plt.legend()  # Add a legend
# # plt.grid(True)  # Add a grid
# plt.tight_layout()  # Fit the plot nicely into the figure
# plt.show()


"""#Plotting"""
#One day case

#All days case
# plot_irradiance_profile_for_different_panel_orientations(total_irradiance_df)

# plot_irradiance_profiles_for_different_panel_orientations_for_one_day(total_irradiance,10)

#All angles case
