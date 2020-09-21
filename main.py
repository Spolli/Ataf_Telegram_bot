#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import json
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

# Logger Config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

### USER CONFIG
bot_token = "INSERT TOKEN HERE"
### END USER CONFIG


def getSingleStop(stop):
    r = requests.get(f'http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/single?Lat={stop["y"]}&Lon={stop["x"]}&nodeId={stop["id"]}&getSchedule=true').json()
    print(r["s"])

def update_stops():
    stops = requests.get('http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true').json()
    with open('src/data/stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    print("Updated!")
    
def search_for_id(id):
    with open('src/data/stops.json', 'r') as j:
        stops = json.loads(j.read())
    for stop in stops:
        if stop["id"] == id:
            getSingleStop(stop)
    print("Nessuna fermata trovata")

def search_for_name(name):
    with open('src/data/stops.json', 'r') as j:
        stops = json.loads(j.read())
    stop_list = []
    for stop in stops:
        if name in stop["n"].strip():
            stop_list.append(stop)

    if len(stop_list) is []:
        print("Nessun risulato trovato!")
    elif len(stop_list) == 1:
        getSingleStop(stop_list[0])
    else:
        #caselle per scelta
        None
    
def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    '''
    updater = Updater(bot_token)
    dp = updater.dispatcher
    job = updater.job_queue
    job.run_repeating(periodical_check, 600.0, 0.0)
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, status_update))
    dp.add_handler(CommandHandler("banlist", cmd_banlist))
    dp.add_handler(CommandHandler("banlist_full", cmd_banlist_full))
    dp.add_handler(CommandHandler("unsub_banlist", cmd_unsub_banlist))
    dp.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()
    '''
    #update_stops()
    search_for_id("FM1153")

if __name__ == '__main__':
    main()