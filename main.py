#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import urllib3
import json
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

# Logger Config
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
http = urllib3.PoolManager()

### USER CONFIG
bot_token = "INSERT TOKEN HERE"
### END USER CONFIG


def getAllStops():
    r = http.request("http://www.temporealeataf.it/Mixer/Rest/PublicTransportService.svc/stops?urLat=44&urLon=12&llLat=43&llLon=10&getId=true")
    stops = json.loads(r)


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
    print(getAllStops())


if __name__ == '__main__':
    main()