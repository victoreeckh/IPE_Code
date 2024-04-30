import math

def get_number_of_solar_panels(south_orientation, flat_roof, width_roof, length_roof, width_panel, length_panel):
    if flat_roof is False:
        angle = 45
        cos_value = math.cos(math.radians(angle))
        width_tilted_panel=cos_value*width_panel
        number_of_panels_length = math.floor(length_roof/length_panel)
        number_of_panels_width = math.floor(width_roof / width_tilted_panel)
        number_of_panels = number_of_panels_length*number_of_panels_width
        return number_of_panels

    if flat_roof is True:
        if south_orientation is False:
            angle = 10
            cos_value = math.cos(math.radians(angle))
            width_tilted_panel = cos_value * width_panel
            number_of_panels_length = math.floor(length_roof / length_panel)
            number_of_panels_width = math.floor(width_roof / width_tilted_panel)
            number_of_panels = number_of_panels_length * number_of_panels_width
            return number_of_panels

        if south_orientation is True:
            angle = 40
            solar_elevation_at_solar_noon_shortest_day = 15.57 #chatgpt value for genk
            cos_value = math.cos(math.radians(angle))
            shade_buffer = 1 + math.sin(math.radians(angle))*math.tan(math.radians(solar_elevation_at_solar_noon_shortest_day))
            width_tilted_panel = cos_value * width_panel*shade_buffer
            number_of_panels_length = math.floor(length_roof / length_panel)
            number_of_panels_width = math.floor(width_roof / width_tilted_panel)
            number_of_panels = number_of_panels_length * number_of_panels_width
            return number_of_panels

number_of_panels = get_number_of_solar_panels(True,True,6,8,0.5,1)
number_of_panels2 = get_number_of_solar_panels(False,True,6,8,0.5,1)
number_of_panels3 = get_number_of_solar_panels(True,False,6,8,0.5,1) #all gabbles
print(number_of_panels,number_of_panels2,number_of_panels3)
