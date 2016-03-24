# coding=utf-8
import re
import time
from datetime import datetime
from datetime import timedelta

from gmail_wrapper_api import GmailClientApi
from tinydb import TinyDB
from tinydb import Query
import unicodedata

DB_FILE = 'db.json'
GMT_OFFSET = 2


def is_heb(input_string):
    for c in input_string:
        if c in 'אבגדהוזחטיכלמנסעפצקרשתךםןץ':
            return True
    return False


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
        self.creation_time = self.time_str_to_gmt_daytime(creation_time)
        self.parsed_data = self.parse(data)

    @staticmethod
    def _tz_offset_str_to_hours(tz_offset_str):
        return -1 * int(tz_offset_str) / 100 + GMT_OFFSET

    @classmethod
    def time_str_to_gmt_daytime(cls, time_str):
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
        dt = datetime.fromtimestamp(time.mktime(struct))

        return dt + timedelta(hours=cls._tz_offset_str_to_hours(tz_offset))

    @classmethod
    def _filter_text_basic(cls, text):
        """
        :param data: str -> raw input string
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


class Fetcher(object):
    def __init__(self):
        self.client = GmailClientApi(None)

    def get_msg_ids(self):
        # a list of [ {"id": "153a833d1dbee17e",
        # "threadId": "153a833d1dbee17e"}]
        msgs = self.client.get_messages_matching_query(
            query='to: tlv-food-arrivals')

        for m in msgs:
            yield m['id']

    def get_msg_objects(self):
        for msg_id in self.get_msg_ids():
            yield self.client.get_message(msg_id=msg_id)

    @classmethod
    def format_msg_data(cls, msg):
        """Extracts data from msg and wraps in ParsedData.

        :param msg: GmailMessage.
        :returns list: list of ParsedData objects per item in msg.
        """
        parser = Parser(msg.uid, msg.subject, msg.date)

        return parser.get_parsed_data()

    def get_formatted_data(self):
        """:return list: list of ParsedData objects """

        for msg in self.get_msg_objects():
            yield self.format_msg_data(msg)


class Db(object):
    db = None
    food_arrivals_table = None
    db_tables = ['food_arrivals']

    def __init__(self):
        self._load_db()

    @classmethod
    def purge_db(cls):
        open(DB_FILE, 'w').close()
        TinyDB(DB_FILE)

    def _load_db(self):
        self.db = TinyDB(DB_FILE)
        self.food_arrivals_table = self.db.table('food_arrivals')

    def get_food_arrival_by_id(self, uid):
        return self.food_arrivals_table.search(Query().uid == uid)

    def update_food_arrivals_table(self, uid, date, data):
        if self.get_food_arrival_by_id(uid):
            print('dup uid {}'.format(uid))
            return

        self.food_arrivals_table.insert(
            {'uid': uid, 'date': date, 'data': data})

    def get_all_food_arrivals(self):
        return self.food_arrivals_table.all()