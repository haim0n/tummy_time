# coding=utf-8
import calendar
import email
import glob
import os
import re
import time
import urllib2

from datetime import datetime
from datetime import time as dt
from datetime import timedelta

from email.header import decode_header
import itertools

import pytz

from tummy_time import db_api

_script_location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

EWA_ALPHA = 0.7


def time_to_seconds(t):
    return t.hour * 3600 + t.minute * 60 + t.second


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

    st_list = [time_to_seconds(time_list[0])]
    st = st_list[0]
    for d in time_list[1:]:
        yt = time_to_seconds(d)
        st = alpha * yt + (1 - alpha) * st_list[-1]
        st_list.append(st)

    # print(st_list, st)

    st_hr = int(st / 3600)
    st_min = int(st % 3600 / 60)
    st_sec = int(st % 3600 % 60)

    return dt(st_hr, st_min, st_sec)


class Parser(object):
    tz_re = re.compile("\(([A-Z]+)\)")

    def __init__(self):
        self.session = db_api.Session()

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
    def _txt_to_messages(cls, text):
        """Convert raw text data to email messages.

        :param text: str -> raw input string
        :returns: list -> email objects
        """
        regex = re.compile('^From .', flags=re.DOTALL | re.MULTILINE)

        msg_texts = re.split(regex, text)[1:]
        return [email.message_from_string(''.join(['From ', txt])) for txt in
                msg_texts]

    def parse(self, data):
        msg_list = self._txt_to_messages(data)
        for msg in msg_list:
            msg_id = msg.get('Message-ID')
            tbl = db_api.Restaurant
            if self.session.query(tbl).filter(tbl.id == msg_id).first():
                print('dup msg_id: {}'.format(msg_id))
                continue
            arr_time = self.time_str_to_israel_datetime(msg.get('Date'))
            dh = decode_header(msg.get('Subject'))
            subj = ''.join([unicode(t[0], t[1] or 'ASCII') for t in dh])
            rest = tbl(id=msg_id, arrival_time=arr_time, subject=subj)
            self.session.add(rest)
            self.session.commit()
            print('added {} {}'.format(msg_id, arr_time))
        return msg_list


class Fetcher(object):
    def __init__(self, url, first_archive_date, archive_suffix,
                 archive_dir=os.path.join(_script_location, 'archives')):
        self.url = url
        self.first_archive_date = first_archive_date
        self.archive_suffix = archive_suffix
        self.archive_dir = archive_dir
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def _get_all_archive_dates(self):
        """Provides formatted archive dates.

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

    def _get_all_archive_names(self):
        """Provides formatted archive names.

        :returns: list -> list of strings in the form of
        YYYY-mm.archive_suffix
        """
        return map(self._archive_name_from_date, self._get_all_archive_dates())

    def _fetch_archives(self, archives_to_fetch):
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

        return [os.path.join(self.archive_dir, archive) for archive in
                fetched_list]

    def _get_fetched_archives(self):
        return [a.split('/')[-1] for a in
                glob.glob(self.archive_dir + '/*' + self.archive_suffix)]

    def fetch(self):
        """Fetches all remote archives that don't exist locally.

        The latest archive always gets downloaded for potentially holding
        new data.

        :return list: -> list of downloaded archive file names.
        """
        today = datetime.now()
        latest_archive = self._archive_name_from_date(
            (today.year, today.month))
        fetched_archives = self._get_fetched_archives()
        archives_to_fetch = set(self._get_all_archive_names()) - set(
            fetched_archives) | {latest_archive}

        return self._fetch_archives(archives_to_fetch)

    def purge_data(self):
        if os.path.exists(self.archive_dir):
            os.rmdir(self.archive_dir)
