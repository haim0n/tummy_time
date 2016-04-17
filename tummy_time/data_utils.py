# coding=utf-8
import calendar
import os
import re
import time
import urllib2
from datetime import time as dt
from datetime import datetime
from datetime import timedelta

import itertools
import glob

import pytz

import unicodedata

from tummy_time import db_api

_script_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

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
        data = unicodedata.normalize('NFKD', data).encode('ascii', 'ignore')
        data = cls._filter_text_basic(data)
        lst = cls._filter_multiple_entries(data)

        return lst

    def get_parsed_data(self):
        out = [ParsedData(self.uid, str(d), str(self.creation_time)) for d in
               self.parsed_data]
        return out


class Fetcher(object):
    def __init__(self, url, first_archive_date, archive_suffix,
                 archive_dir=os.path.join(_script_location, 'archives')):
        self.url = url
        self.session = db_api.Session()
        self.first_archive_date = first_archive_date
        self.archive_suffix = archive_suffix
        self.archive_dir = archive_dir
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def _get_all_archive_dates(self):
        """

        :returns: set - set of tuples (year, month) each tuple representing
        archives dates.
        """
        start_month = self.first_archive_date.month
        start_year = self.first_archive_date.year
        today = datetime.now()
        all_dates = itertools.product(range(start_year, today.year + 1),
                                      range(1, 13))
        dates_to_remove = []
        months_to_remove = range(1, start_month)
        if months_to_remove:
            dates_to_remove = list(
                itertools.product([start_year], months_to_remove))

        months_to_remove = []
        if today.month < 12:
            months_to_remove = range(today.month + 1, 13)
        if months_to_remove:
            dates_to_remove += list(itertools.product([today.year],
                                                      months_to_remove))

        dates = set(all_dates) - set(dates_to_remove)
        return dates

    def _archive_name_from_date(self, date_tuple):
        return ''.join(
            [str(date_tuple[0]), '-', calendar.month_name[date_tuple[1]],
             self.archive_suffix])

    def get_all_archive_names(self):
        """

        :returns: list - list of strings in the form of YYYY-mm.archive_suffix
        """
        return map(self._archive_name_from_date, self._get_all_archive_dates())

    def fetch_archives(self, archives_to_fetch):
        fetched_list = []
        for archive in archives_to_fetch:
            try:
                remote_archive = self.url + '/' + archive
                local_archive = os.path.join(self.archive_dir, archive)
                fetched = urllib2.urlopen(remote_archive)
                with open(local_archive, 'wb') as outf:
                    outf.write(fetched.read())
                print('fetched {}'.format(archive))
                fetched_list.append(archive)
            except urllib2.HTTPError as e:
                print('error fetching {}: {}'.format(archive, e))

        return fetched_list

    def get_fetched_archives(self):
        return [a.split('/')[-1] for a in
                glob.glob(self.archive_dir + '/*' + self.archive_suffix)]

    def fetch(self):
        """Fetches all available archives that don't exist locally from remote
        url. The latest archive always gets downloaded for potentially holding
        new data.

        :return list: list of downloaded archive file names"""
        today = datetime.now()
        latest_archive = self._archive_name_from_date(
            (today.year, today.month))
        fetched_archives = self.get_fetched_archives()
        archives_to_fetch = set(self.get_all_archive_names()) - set(
            fetched_archives) | {latest_archive}

        return self.fetch_archives(archives_to_fetch)
