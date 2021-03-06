#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from src.data.API import API_KEY
from src.data.msg import *
from src.utility.async_stop import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

stop_list = {}

markup = ReplyKeyboardMarkup(choosing_keyboard, one_time_keyboard=True)

####################################################################################

def askForID(update, context):
    update.message.reply_text(ENTER_ID_msg)
    return TYPING_REPLY

def askForName(update, context):
    update.message.reply_text(ENTER_NAME_msg)
    return TYPING_REPLY

def askForLocation(update, context):
    update.message.reply_text(ENTER_LOC_msg)
    return TYPING_REPLY

def getInfoLoc(update, context):
    states = CHOOSING
    try:
        loc = update.message.location
        states = findNearestStops(loc.latitude, loc.longitude, update)
    except:
        update.message.reply_text(ERROR_LOC_msg, reply_markup=markup)
    return states

def getInfo(update, context):
    try:
        stop = update.message.text.upper()
        states = CHOOSING
        if not stop == 'INDIETRO':
            if stop.isalnum() and len(stop) < 7:
                findByID(stop, update)
            else:
                states = findByName(stop, update)
            return states
    except:
        update.message.reply_text(ERROR_msg, reply_markup=markup)
    return CHOOSING

def findNearestStops(lat, lon, update):
    global stop_list
    stop_list.clear()
    stops = getJsonListLocal()
    stop_list = calculate_circle(lat, lon, stops)
    if not stop_list is None:
        loc_keyboard = [['Fine', 'Indietro']]
        for stop in stop_list.keys():
            loc_keyboard.append([stop])
        location_markup = ReplyKeyboardMarkup(loc_keyboard, one_time_keyboard=True)
        update.message.reply_text(CHOOSE_NEAR_STOP_msg, reply_markup=location_markup)
        return TYPING_CHOICE
    else:
        update.message.reply_text(ERROR_msg, reply_markup=markup)
        return CHOOSING

def findByID(id, update):
    global stop_list
    stop_list.clear()
    timeline = None
    stops = getJsonListLocal()
    for stop in stops:
        if stop["id"] == id:
            timeline = getSingleStop(stop)
            if timeline:
                loc = f"{timeline['y']},{timeline['x']}"
                refresh_keyboard = [[InlineKeyboardButton('Aggiorna Orari', callback_data=timeline['id']), InlineKeyboardButton('Fermata', callback_data=loc)]]
                refresh_markup = InlineKeyboardMarkup(refresh_keyboard, one_time_keyboard=True)
                update.message.reply_text(formatTable(timeline['s']), reply_markup=refresh_markup)
            else:
                update.message.reply_text(NO_BUS_msg, reply_markup=markup)
    if timeline is None:
        update.message.reply_text(NO_STOP_msg, reply_markup=markup)

def refresh(update, context):
    query = update.callback_query
    query.answer()
    findByID(query.data, query)
    return CHOOSING

def sendLocURL(update, context):
    query = update.callback_query
    query.answer()
    url = f"http://maps.google.com/maps?q=loc:{query.data}"
    query.edit_message_text(url, reply_markup=markup)
    return CHOOSING

def findByName(name, update):
    global stop_list
    stop_list.clear()
    stops = getJsonListLocal()
    for stop in stops:
        if name in stop['n']:
            stop_list[stop['n']] = stop
    if not stop_list:
        update.message.reply_text(NO_STOP_msg)
    else:
        stops_keyboard = [['Fine', 'Indietro']]
        for key in stop_list.keys():
            stops_keyboard.append([key])
        markup_stop = ReplyKeyboardMarkup(stops_keyboard, one_time_keyboard=True)
        update.message.reply_text(CHOSE_STOP_msg, reply_markup=markup_stop)
    return TYPING_CHOICE

def printStopName(update, context):
    try:
        name = update.message.text
        findByID(stop_list[name]['id'], update)
    except:
        update.message.reply_text(ERROR_msg, reply_markup=markup)
    return CHOOSING
        
def start(update, context):
    update.message.reply_text(WELCOME_msg, reply_markup=markup)
    return CHOOSING

def fine(update, context):
    update.message.reply_text(CLOSE_msg, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def undo(update, context):
    update.message.reply_text(reply_markup=markup)
    return CHOOSING

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
                                    askForName),
                        MessageHandler(Filters.regex('^(Cerca fermate vicine a te)$'),
                                    askForLocation),
                        CallbackQueryHandler(sendLocURL, pattern='^[0-9.,]*$'),
                        CallbackQueryHandler(refresh, pattern='^\w{4,6}[a-zA-Z0-9]*$')
                       ],
            
            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|End|end|Done|done)$')), printStopName)],
            
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|Indietro|indietro)$')), getInfo),
                MessageHandler(Filters.location & ~(Filters.command | Filters.regex('^(Fine|fine|Indietro|indietro)$')), getInfoLoc),],
        },
        
        fallbacks=[
            MessageHandler(Filters.regex('^Fine$'), fine),
            MessageHandler(Filters.regex('^Indietro$'), undo)
            ]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    update_stops()
    main()

