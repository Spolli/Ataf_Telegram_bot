#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
import datetime
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
#from src/data/API.py import API_KEY

API_KEY = "1121064435:AAETkb0SDomcAHgKxtl7tX2ZcNVrDy_P-X8"
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, TYPING_STOPS = range(4)

stop_list = {}

choosing_keyboard = [['Cerca Per ID fermata'],
                  ['Cerca per nome della fermata'],
                  ['Fine']]
markup = ReplyKeyboardMarkup(choosing_keyboard, one_time_keyboard=True)

####################################################################################

def getJsonList():
    return requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()

def getSingleStop(stop):
    return requests.get(f'http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/single?Lat={stop["y"]}&Lon={stop["x"]}&nodeId={stop["id"]}&getSchedule=true').json()

def askForID(update, context):
    update.message.reply_text("Inserisci l'ID della fermata...")
    return TYPING_REPLY

def askForName(update, context):
    update.message.reply_text("Inserisci il nome della fermata...")
    return TYPING_REPLY

def getInfo(update, context):
    stop = update.message.text
    if len(stop) < 7:
        findByID(stop, update)
    else:
        findByName(stop, update)
    return CHOOSING

def findByID(id, update):
    id = id.upper
    timeline = None
    stops = getJsonList()
    for stop in stops:
        if stop["id"] == id:
            timeline = getSingleStop(stop)['s']
            text = ''
            for time in timeline:
                text += str(datetime.timedelta(seconds=int(time['d'])/1000)) + '\t|\t' + time['n'] + '\t|\t' + time['t'] + '\n'
            update.message.reply_text(text)
    if timeline is None:
        update.message.reply_text('Fermata non trovata!')
    return CHOOSING 

def findByName(name, update):
    global stop_list
    stops = getJsonList()
    for stop in stops:
        if str(name.upper) in str(stop['n']):
            update.message.reply_text(stop)
            stop_list[stop['n']] = stop
    if not stop_list:
        update.message.reply_text('Fermata non trovata!')
    else:
        stops_keyboard = ['Fine']
        for key in stop_list.keys():
            update.message.reply_text(key)
            stops_keyboard.append([key])
        update.message.reply_text("Scegli la fermata", reply_markup=stops_keyboard)
    return TYPING_CHOICE

def printStopName(update, context):
    name = update.message.text
    name = name.upper
    findByID(stop_list[name]['id'], update)
    return CHOOSING

def start(update, context):
    update.message.reply_text("Benvenuto nel bot", reply_markup=markup)
    return CHOOSING

def fine(update, context):
    update.message.reply_text('Buona corsa in quello scatolotto con le ruote')
    return ConversationHandler.END


def main():
    updater = Updater(API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Cerca Per ID fermata)$'),
                                    askForID),
                       MessageHandler(Filters.regex('^(Cerca per nome della fermata)$'),
                                    askForName)
                       ],
            
            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|End|end|Done|done)$')),
                                printStopName)],
            
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|End|end|Done|done)$')),
                               getInfo)],
        },
        
        fallbacks=[MessageHandler(Filters.regex('^Fine$'), fine)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()


    #^(?=.{5,6}$)[A-Z|0-9]*$
