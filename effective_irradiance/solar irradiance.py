import numpy as np
import ephem
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

latitude = 50.99461
longitude = 5.53972
south_tilt_angle = 40
east_west_tilt_angle = 10

def get_sun_position(latitude, longitude, date_time):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = date_time

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

    return Irrad_solarpanelE.item(), Irrad_solarpanelS.item(), Irrad_solarpanelW.item()

solar_data = pd.read_excel('C:/Users/lucas/PycharmProjects/IPE/Irradiance_data.xlsx')
date_time = solar_data['DateTime']
global_horizontal_irradiance = solar_data['GlobRad']
global_diffusive_irradiance = solar_data['DiffRad']

total_irradiance = []

for i in range(len(date_time)):
    exact_moment = date_time[i]
    zenith_angle, azimuth_angle = get_sun_position(latitude,longitude,exact_moment)
    GHI = global_horizontal_irradiance[i]
    DHI = global_diffusive_irradiance[i]
    total_irradiance_E, total_irradiance_S, total_irradiance_W = get_solar_irradiance(GHI,DHI,south_tilt_angle,east_west_tilt_angle,azimuth_angle,zenith_angle)
    total_irradiance.append([exact_moment,total_irradiance_E,total_irradiance_S,total_irradiance_W])

print(total_irradiance)
# Convert the list to a DataFrame
columns = ['DateTime', 'Irradiance_East', 'Irradiance_South', 'Irradiance_West']
total_irradiance_df = pd.DataFrame(total_irradiance, columns=columns)

# Plotting
plt.figure(figsize=(10, 6))  # Set the figure size
plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_East'], label='East', color='blue')
plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_South'], label='South', color='red')
plt.plot(total_irradiance_df['DateTime'], total_irradiance_df['Irradiance_West'], label='West', color='orange')

plt.title('Irradiance profile for different panel orientations')
plt.xlabel('Time')
plt.ylabel('Irradiance [W/m²]')
plt.legend()  # Add a legend
plt.grid(True)  # Add a grid
plt.tight_layout()  # Fit the plot nicely into the figure
plt.show()