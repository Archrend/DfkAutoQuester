import pandas as pd
import logging
import logging.config
import telegram_handler

def setLoggerConfig():
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {'format': '%(asctime)s - %(levelname)s - %(message)s'},
        'telegram': {'format': '%(asctime)s - %(message)s'}
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': 'guild_bot.log',
            'maxBytes': 20971520,
            'backupCount': 9
        }
    },
    'loggers': {
        'default': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'telegram']
        }
    },
    'disable_existing_loggers': False
    })
    return logging.getLogger('default')