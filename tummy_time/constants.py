from datetime import datetime

import appdirs

DATA_DIR = appdirs.user_data_dir('tummy-time')
EWA_ALPHA = 0.7

ARCHIVES_URL = 'http://post-office.corp.redhat.com/archives/tlv-food-arrivals/'
FIRST_ARCHIVE = datetime(2010, 11, 1)
ARCHIVE_SUFFIX = '.txt.gz'
