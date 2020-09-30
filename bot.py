#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
from datetime import datetime as dt
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from src.data.API import API_KEY

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

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
    try:
        stop = update.message.text.upper()
        states = CHOOSING
        if len(stop) < 7:
            states = findByID(stop, update)
        else:
            states = findByName(stop, update)
        return states

    except:
        update.message.reply_text('Upsy stinky error', reply_markup=markup)
        return CHOOSING
    
def findByID(id, update):
    global stop_list
    timeline = None
    stops = getJsonList()
    for stop in stops:
        if stop["id"] == id:
            timeline = getSingleStop(stop)['s']
            if timeline:
                text = ''
                for time in timeline:
                    d_time = dt.utcfromtimestamp(int(time['d'])//1000)
                    text += d_time.strftime('%H:%M') + '\t|\t' + time['n'] + '\t|\t' + time['t'] + '\n'
                update.message.reply_text(text, reply_markup=markup)
            else:
                update.message.reply_text("Non passa nessun bus, mi dispy", reply_markup=markup)
    if timeline is None:
        update.message.reply_text('Fermata non trovata!', reply_markup=markup)
    stop_list = {}
    return CHOOSING 

def findByName(name, update):
    global stop_list
    stops = getJsonList()
    for stop in stops:
        if name in stop['n']:
            stop_list[stop['n']] = stop
    if not stop_list:
        update.message.reply_text('Fermata non trovata!')
    else:
        stops_keyboard = [['Fine']]
        for key in stop_list.keys():
            stops_keyboard.append([key])
        markup_stop = ReplyKeyboardMarkup(stops_keyboard, one_time_keyboard=True)
        update.message.reply_text("Scegli la fermata:", reply_markup=markup_stop)
    return TYPING_CHOICE

def printStopName(update, context):
    try:
        name = update.message.text
        return findByID(stop_list[name]['id'], update)
    except:
        update.message.reply_text('Upsy stinky error', reply_markup=markup)
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
