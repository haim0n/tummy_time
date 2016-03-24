import re
import time
from datetime import datetime
from datetime import timedelta


class DataPrinter(object):
    tz_re = re.compile("\(([A-Z]+)\)")

    @staticmethod
    def _tz_offset_str_to_hours(tz_offset_str):
        return (-1 * int(tz_offset_str)/100 + 2)

    def time_to_gmt(self, time_str):
        """
        :param time_str: string from msg Date header
        :return: datetime for GMT (+0200) representation
        """

        # skip the TZ name, if exists
        time_str_list = time_str.rsplit()
        tz = time_str_list[-1]
        if self.tz_re.match(tz):
            time_str_list = time_str_list[:-1]
        tz_offset = time_str_list[-1]

        # skip the offset
        time_str_list = time_str_list[:-1]
        time_str = ' '.join(time_str_list)

        struct = time.strptime(time_str, '%a, %d %b %Y %H:%M:%S')
        dt = datetime.fromtimestamp(time.mktime(struct))

        return dt + timedelta(hours=self._tz_offset_str_to_hours(tz_offset))


class DataParser(object):
    def __init__(self, uid, data, created_at):
        self.uid = uid
        self.data = data
        self.created_at = created_at
