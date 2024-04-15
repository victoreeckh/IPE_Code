import math

def get_number_of_solar_panels(south_orientation, flat_roof, surface_area_roof, surface_area_panel):
    if flat_roof is False:
        angle = 45
        cos_value = math.cos(math.radians(angle))
        surface_area_tilted_panel=cos_value*surface_area_panel
        number_of_panels = math.floor(surface_area_roof / surface_area_tilted_panel)
        return number_of_panels

    if flat_roof is True:
        if south_orientation is False:
            angle = 10
            cos_value = math.cos(math.radians(angle))
            surface_area_tilted_panel = cos_value * surface_area_panel
            number_of_panels = math.floor(surface_area_roof / surface_area_tilted_panel)
            return number_of_panels

        if south_orientation is True:
            angle = 40
            solar_elevation_at_solar_noon_shortest_day = 15.57 #chatgpt value for genk
            cos_value = math.cos(math.radians(angle))
            shade_buffer = 1 + math.sin(math.radians(angle))*math.tan(math.radians(solar_elevation_at_solar_noon_shortest_day))
            surface_area_tilted_panel = cos_value * surface_area_panel*shade_buffer
            number_of_panels = math.floor(surface_area_roof / surface_area_tilted_panel)
            return number_of_panels

number_of_panels = get_number_of_solar_panels(True,True,40,1)
number_of_panels2 = get_number_of_solar_panels(False,True,40,1)
number_of_panels3 = get_number_of_solar_panels(True,False,40,1) #all gabbles
print(number_of_panels,number_of_panels2,number_of_panels3)
