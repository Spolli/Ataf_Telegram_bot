#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import telebot

### USER CONFIG
API_TOKEN = "1121064435:AAETkb0SDomcAHgKxtl7tX2ZcNVrDy_P-X8"
### END USER CONFIG

bot = telebot.TeleBot(API_TOKEN)

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
    Benvenuto nel nuovo fiammeggiange bot per l'ataf
    fatto bene stavolta!
    """)


def getSingleStop(stop):
    r = requests.get(f'http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/single?Lat={stop["y"]}&Lon={stop["x"]}&nodeId={stop["id"]}&getSchedule=true').json()
    print(r["s"])

def update_stops():
    stops = requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()
    with open('src/data/stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    print("Updated!")

@bot.message_handler(commands=['findByID'])
def findByID(message):
    bot.reply_to(message, "Inserisci l'ID della fermata \nEsempio ....")

    
    with open('src/data/stops.json', 'r') as j:
        stops = json.loads(j.read())
    for stop in stops:
        if stop["id"] == id:
            getSingleStop(stop)
    print("Nessuna fermata trovata")

@bot.message_handler(commands=['findByName'])
def findByName(message):
    with open('src/data/stops.json', 'r') as j:
        stops = json.loads(j.read())
    stop_list = []
    for stop in stops:
        if name in stop["n"].strip():
            stop_list.append(stop)

    if len(stop_list) == 0:
        print("Nessun risulato trovato!")
    elif len(stop_list) == 1:
        getSingleStop(stop_list[0])
    else:
        #caselle per scelta
        None