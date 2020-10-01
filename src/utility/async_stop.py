#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime as dt
from tabulate import tabulate

#@MWT(timeout=60*60)
def update_stops():#update, context):
    stops = requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()
    with open('src/data/stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)

def getJsonListLocal():
    with open('src/data/stops.json', 'r') as f:
        return json.loads(f.read())

def getJsonListWeb():
    return requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()

def getSingleStop(stop):
    return requests.get(f'http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/single?Lat={stop["y"]}&Lon={stop["x"]}&nodeId={stop["id"]}&getSchedule=true').json()

def formatTable(timeline):
    table = []
    for time in timeline:
        #Aggiungo un'ora (3600 sec) perchè il mio localtime UTC è sballato
        d_time = dt.fromtimestamp(int(time['d'])/1000 + 3600).strftime('%H:%M')
        table.append([time['n'], d_time, time['t']])
    return tabulate(table, headers=["N. Bus", "Arrivo", "Partenza"], tablefmt="simple")

def formatData(timeline):
    table = ''
    for time in timeline:
        d_time = dt.fromtimestamp(int(time['d'])/1000 + 3600).strftime('%H:%M')
        table += '{:>4} {:>10} {:>25}\n'.format(time['n'], d_time, time['t'])
    return table

def calculate_circle(y , x , pos_list):
    pi=3.14153
    std_radius=2000 #these are meters
    constant=0.0174533 #conversion number from decimal degree to radiant
    point2_constant=0.004 #default number to draw 500m square around position
    second_x=x+0.004
    fourth_y=y+0.004
    third_x=x-0.004
    fifth_y=y-0.004
    bus_stop_list={}
    for stop in pos_list:
        if third_x < stop['x'] < second_x and fifth_y < stop['y'] < fourth_y:
            bus_stop_list[stop['n']] = stop
    if bus_stop_list:
        return bus_stop_list
    else:
        None


'''
"\U0001F68F", 
"\U0001F68D",
'''