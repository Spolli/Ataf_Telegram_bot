#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime as dt
from tabulate import tabulate

def update_stops():
    stops = requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()
    with open('src/data/stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    return True

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
        d_time = dt.utcfromtimestamp(int(time['d'])//1000).strftime('%H:%M')
        table.append([ time['n'], d_time, time['t']])
    return tabulate(table, headers=["N. Bus", "Arrivo", "Partenza"], tablefmt="simple")

'''
"\U0001F68F", 
"\U0001F68D",
'''