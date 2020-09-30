#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
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

def getInfo(update, context):
    try:
        stop = update.message.text.upper()
        states = CHOOSING
        if stop.isalnum() and len(stop) < 7:
            states = findByID(stop, update)
        else:
            states = findByName(stop, update)
        return states

    except:
        update.message.reply_text(ERROR_msg, reply_markup=markup)
        return CHOOSING
    
def findByID(id, update):
    global stop_list
    timeline = None
    stops = getJsonListLocal()
    for stop in stops:
        if stop["id"] == id:
            timeline = getSingleStop(stop)['s']
            if timeline:
                update.message.reply_text(formatTable(timeline), reply_markup=markup)#, parse_mode=ParseMode.HTML)
            else:
                update.message.reply_text(NO_BUS_msg, reply_markup=markup)
    if timeline is None:
        update.message.reply_text(NO_STOP_msg, reply_markup=markup)
    stop_list = {}
    return CHOOSING 

def findByName(name, update):
    global stop_list
    stops = getJsonListWeb()
    for stop in stops:
        if name in stop['n']:
            stop_list[stop['n']] = stop
    if not stop_list:
        update.message.reply_text(NO_STOP_msg)
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
        update.message.reply_text(ERROR_msg, reply_markup=markup)
        return CHOOSING
    

def start(update, context):
    update.message.reply_text(WELCOME_msg, reply_markup=markup)
    return CHOOSING

def fine(update, context):
    update.message.reply_text(CLOSE_msg)
    return ConversationHandler.END


def main():
    updater = Updater(API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex(f'^(Cerca Per ID fermata)$'),
                                    askForID),
                       MessageHandler(Filters.regex(f'^(Cerca per nome della fermata)$'),
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
