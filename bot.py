#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

API_KEY = "1121064435:AAETkb0SDomcAHgKxtl7tX2ZcNVrDy_P-X8"

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

choosing_keyboard = [['Cerca Per ID fermata'],
                  ['Cerca per nome della fermata'],
                  ['Fine']]
markup = ReplyKeyboardMarkup(choosing_keyboard, one_time_keyboard=True)

####################################################################################

def askForID(update, context):
    update.message.reply_text("Inserisci l'ID della fermata...")
    return TYPING_CHOICE

def askForName(update, context):
    update.message.reply_text("Inserisci il nome della fermata...")
    return TYPING_CHOICE

def findByID(update, context):
    text = update.message.text
    update.message.reply_text(text, reply_markup=markup)
    return CHOOSING 

def findByName(update, context):
    text = update.message.text
    update.message.reply_text(text, reply_markup=markup)
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
                                findByID),
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|End|end|Done|done)$')),
                                findByName)],
            
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^(Fine|fine|End|end|Done|done)$')),
                               fine)],
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