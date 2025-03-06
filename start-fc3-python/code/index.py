# -*- coding: utf-8 -*-

import logging
import bs4

def handler(event, context):
    logger = logging.getLogger()
    logger.info(event)
    print(bs4.__version__)
    return event