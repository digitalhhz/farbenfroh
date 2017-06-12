#!/usr/bin/env python

"""Auslesen von Sensorwerte aus Home Assistant"""

__author__      = "FarbenFroh"

import homeassistant.remote as remote
import configparser
import time
import ast

#Config
Config = configparser.ConfigParser()
Config.read("config.ini")

#Connect to Home Assistant
api = remote.API(Config.get('HomeAssistant', 'IP'), Config.get('HomeAssistant', 'PW'))

#Create lists for sensor IDs
temperature_ids = []
co2_ids = []
humidity_ids = []

#Get Sensor IDs from Home Assistant
entities = remote.get_states(api)
for entity in entities:
    if str(entity).__contains__(Config.get('Sensors', 'Room')) and not str(entity).__contains__("group"):
        #print(entity)
        if str(entity).__contains__("V_TEMP"):
            temperature_ids.append(entity.entity_id)
        elif str(entity).__contains__("V_LEVEL"):
            co2_ids.append(entity.entity_id)
        elif str(entity).__contains__("V_HUM"):
            humidity_ids.append(entity.entity_id)


#Get Avergage State of on Sensor Class
def getStateAvg(api, list):
    i = 0
    sum = 0
    for list_item in list:
        value = remote.get_state(api, list_item)
        sum = sum + float(value.state)
        i = i + 1
    if(i>0):
        avg = sum/i
    else:
        avg = 0
    return avg

def setLightColor(api, values):
    inuse = "free"
    bright = 0.0
    lamp = Config.get('Sensors', 'Lamp')
    flag = 'leer'
    while (values['temp_max'] == True or values['temp_min'] or values['hum_min'] == True or values['hum_max'] == True or
                   values['Co2_max'] == True):

        if (values['temp_min'] == True and inuse == 'temp_min') or inuse == 'free':
            print('Bright:' + str(bright))
            print('TempMaxBright:' + str(values['temp_bright']))
            inuse = 'temp_min'
            if bright <= values['temp_bright'] and flag != 'reachedmax':
                print('hoch')
                bright = bright + 1
                if (bright == values['temp_bright']): flag = 'reachedmax'
            else:
                if bright == 0:
                    values['temp_min'] = False
                bright = bright - 1

            color = ast.literal_eval(Config.get('Sectors', 'Temp_Min_Color'))
            print(color)
            remote.call_service(api, 'light', 'turn_on', {'entity_id': lamp, 'brightness': bright,
                                                          'rgb_color': color})

        if (values['temp_max'] == True and inuse == 'temp_max') or inuse == 'free':
            inuse = 'temp_max'
            if bright <= values['temp_bright'] and flag != 'reachedmax':
                bright = bright + 1
                if (bright == values['temp_bright']): flag = 'reachedmax'
            else:
                if bright == 0:
                    values['temp_max'] = False
                bright = bright - 1
            remote.call_service(api, 'light', 'turn_on',
                                {'entity_id': lamp, 'brightness': bright,
                                 'rgb_color': Config.get('Sectors', 'Temp_Max_Color')})

        if (values['hum_min'] == True and inuse == 'hum_min') or inuse == 'free':
            inuse = 'hum_min'

            if bright <= values['temp_bright'] and flag != 'reachedmax':

                bright = bright + 1
                if (bright == values['temp_bright']): flag = 'reachedmax'
            else:
                print('runter')
                if bright == 0:
                    values['Co2_max'] = False
                bright = bright - 1
            remote.call_service(api, 'light', 'turn_on',
                                {'entity_id': lamp, 'brightness': bright,
                                 'rgb_color': str(Config.get('Sectors', 'Hum_Min_Color'))})

        if (values['hum_max'] == True and inuse == 'hum_max') or inuse == 'free':
            inuse = 'hum_max'
            if bright <= values['temp_bright'] and flag != 'reachedmax':

                bright = bright + 1
                if (bright == values['temp_bright']): flag = 'reachedmax'
            else:
                print('runter')
                if bright == 0:
                    values['hum_max'] = False
                bright = bright - 1
            remote.call_service(api, 'light', 'turn_on',
                                {'entity_id': lamp, 'brightness': bright,
                                 'rgb_color': str(Config.get('Sectors', 'Hum_Max_Color'))})

        if (values['Co2_max'] == True and inuse == 'Co2_max') or inuse == 'free':
            inuse = 'Co2_max'
            if bright <= values['temp_bright'] and flag != 'reachedmax':

                bright = bright + 1
                if (bright == values['temp_bright']): flag = 'reachedmax'
            else:
                if bright == 0:
                    values['Co2_max'] = False
                bright = bright - 1
            remote.call_service(api, 'light', 'turn_on',
                                {'entity_id': lamp, 'brightness': bright,
                                 'rgb_color': Config.get('Sectors', 'Co2_Max_Color')})

#Permament loop
run = True
while run:
    #Get average values
    values = {'temp_min':False,'temp_max':False,'temp_bright':0,'hum_min':False,'hum_max':False,'hum_bright':0,'Co2_max':False,'Co2_bright':0}


    tempAvg = getStateAvg(api, temperature_ids)
    if tempAvg < int(Config.get('Sectors', 'Temp_Min')):
        values['temp_min'] = True
        values['temp_bright'] = (tempAvg - int(Config.get('Sectors', 'Temp_Min'))) * -10
    elif tempAvg > int(Config.get('Sectors', 'Temp_Max')):
        values['temp_max'] = True
        values['temp_bright'] = (tempAvg - int(Config.get('Sectors', 'Temp_Max'))) * 10

    humAvg = getStateAvg(api, humidity_ids)
    if humAvg < int(Config.get('Sectors', 'Hum_Min')):
        values['hum_min'] = True
        values['hum_bright'] = (humAvg - int(Config.get('Sectors', 'Hum_Min'))) * -5
    elif humAvg > int(Config.get('Sectors', 'Hum_Max')):
        values['hum_max'] = True
        values['hum_bright'] = (humAvg - int(Config.get('Sectors', 'Hum_Max'))) * 5

    Co2Avg =  getStateAvg(api, co2_ids)
    if Co2Avg > int(Config.get('Sectors', 'Co2_Max')):
        values['Co2_max'] = True
        values['Co2_bright'] = (Co2Avg - int(Config.get('Sectors', 'Co2_Max'))) * 500

    setLightColor(api, values)


    #Delay between call
    time.sleep(int(Config.get('System', 'Delay')))
