#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
from datetime import datetime

import db_api
import data_utils

ARCHIVES_URL = 'http://post-office.corp.redhat.com/archives/tlv-food-arrivals/'
FIRST_ARCHIVE = datetime(2010, 11, 1)
ARCHIVE_SUFFIX = '.txt.gz'


def get_args():
    arg_parser = argparse.ArgumentParser(description='Food arrival stats')
    arg_parser.add_argument('-Z', '--init-db', action='store_true',
                            help='purge all local data', default=False)

    arg_parser.add_argument('-F', '--fetch-data', action='store_true',
                            default=False,
                            help='fetch data and populate local db with it')

    arg_parser.add_argument('-L', '--list-all-restaurants',
                            action='store_true',
                            help='shows a list of restaurants from local db')

    arg_parser.add_argument('-d', '--dump-restaurant-stats')

    return arg_parser.parse_args()


def init_db():
    print('initializing DB')
    db_api.purge_db()


def fetch_data():
    print('fetching data')
    fetcher = data_utils.Fetcher(url=ARCHIVES_URL,
                                 first_archive_date=FIRST_ARCHIVE,
                                 archive_suffix=ARCHIVE_SUFFIX)
    archives = fetcher.fetch()


def populate_food_arrivals_data():
    data = fetch_data()


def output_to_file(f, db):
    db.dump_food_arrivals_to_file(f)


def list_all_restaurants(db):
    for r in sorted(set(db.get_all_restaurants())):
        print(r)


def dump_restaurant_stats(db, rest_name):
    str_times_list = []
    for dct in db.get_restaurant_data(rest_name):
        print(db.dump_rest_dct_to_csv(dct))
        str_times_list.append(dct['date'].split()[-1])

    print('-' * 50)
    if str_times_list:
        print('estimation: {}'.format(data_utils.calc_ema(str_times_list)))


def main():
    args = get_args()

    if args.init_db:
        db_api.purge_db()

    if args.fetch_data:
        populate_food_arrivals_data()


if __name__ == '__main__':
    main()
