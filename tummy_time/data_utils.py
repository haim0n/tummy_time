# coding=utf-8
import os
import re
import time
from datetime import time as dt
from datetime import datetime
from datetime import timedelta

import pytz

import unicodedata

from tummy_time import db_api

EWA_ALPHA = 0.7


def time_str_to_seconds(time_str):
    t_hr, t_min, t_sec = map(int, time_str.split(':'))

    return t_hr * 3600 + t_min * 60 + t_sec


def calc_ema(time_list, alpha=EWA_ALPHA):
    """Calculates Exponential Moving Average for given time series.

    An exponential moving average (EMA), aka an exponentially
    weighted moving average (EWMA) is a math function which applies weighting
    factors which decrease exponentially. The weighting for each older datum
    decreases exponentially, never reaching zero.

    :param alpha: float -> The coefficient alpha represents the degree of
    weighting decrease, a constant smoothing factor between 0 and 1. A higher
    alpha discounts older observations faster.

    :param time_list: list -> list of integeres representing timestamp of
    arrival.

    :returns: time -> the calculated ewa for arrival time.
    """
    if not time_list:
        return None

    st_list = [time_str_to_seconds(time_list[0])]
    st = st_list[0]
    for d in time_list[1:]:
        yt = time_str_to_seconds(d)
        st = alpha * yt + (1 - alpha) * st_list[-1]
        st_list.append(st)

    # print(st_list, st)

    st_hr = int(st / 3600)
    st_min = int(st % 3600 / 60)
    st_sec = int(st % 3600 % 60)

    return dt(st_hr, st_min, st_sec)


class ParsedData(object):
    def __init__(self, uid, data, date):
        self.uid = uid
        self.date = date
        self.parsed_data = data

    def to_csv(self):
        return ','.join(
            (self.uid, str(self.date), str(self.parsed_data)))


class Parser(object):
    tz_re = re.compile("\(([A-Z]+)\)")

    def __init__(self, uid, data, creation_time):
        self.uid = uid
        self.creation_time = self.time_str_to_israel_datetime(creation_time)
        self.parsed_data = self.parse(data)

    @staticmethod
    def _tz_offset_str_to_hours(tz_offset_str):
        return -1 * int(tz_offset_str) / 100

    @classmethod
    def time_str_to_israel_datetime(cls, time_str):
        """Convert time representing string to GMT

        :param time_str: string from msg Date header
        :return: datetime for GMT (+0200) representation
        """
        # skip the TZ name, if exists
        time_str_list = time_str.rsplit()
        tz = time_str_list[-1]
        if cls.tz_re.match(tz):
            time_str_list = time_str_list[:-1]
        tz_offset = time_str_list[-1]

        # skip the offset
        time_str_list = time_str_list[:-1]
        time_str = ' '.join(time_str_list)

        struct = time.strptime(time_str, '%a, %d %b %Y %H:%M:%S')
        dtime = datetime.fromtimestamp(time.mktime(struct),
                                       tz=pytz.timezone('Israel'))

        res = dtime + timedelta(hours=cls._tz_offset_str_to_hours(tz_offset))
        return datetime(res.year, res.month, res.day, res.hour, res.minute,
                        res.second) + res.tzinfo._utcoffset

    @classmethod
    def _filter_text_basic(cls, text):
        """
        :param text: str -> raw input string
        :returns: data string with stripped words
        """
        remove_list = (
            'luch', 'lunch', 'from', 'the', 'has', 'arrived', 'are here',
            'food deliveries')

        remove = '|'.join(remove_list)
        regex = re.compile(r'\b(' + remove + r')\b', flags=re.IGNORECASE)

        out = regex.sub('', text).strip().lower().rstrip('.')
        return out

    @classmethod
    def _filter_multiple_entries(cls, text):
        text = re.sub(r'and\b', ',', text)
        lst = text.split(',')

        return map(str.strip, lst)

    @classmethod
    def parse(cls, data):
        if is_heb(data):
            return []
        data = unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
        data = cls._filter_text_basic(data)
        lst = cls._filter_multiple_entries(data)

        return lst

    def get_parsed_data(self):
        out = [ParsedData(self.uid, str(d), str(self.creation_time)) for d in
               self.parsed_data]
        return out


class DataArchive(object):
    def __init__(self, filename):
        self.filename = filename

    def extract(self):
        pass


class Fetcher(object):
    def __init__(self):
        self.session = db_api.get_db_session()

    @classmethod
    def format_msg_data(cls, msg):
        """Extracts data from msg and wraps in ParsedData.

        :param msg: GmailMessage.
        :returns list: list of ParsedData objects per item in msg.
        """
        parser = Parser(msg.uid, msg.subject, msg.date)

        return parser.get_parsed_data()

    def fetch_data(self):
        """:return list: list of ParsedData objects """

        archives = self.fetch_archives()
        for archive in archives:
            archive.extract()
            yield self.format_msg_data(msg)

    def fetch_archives(self):
        with self.session:
            pass
