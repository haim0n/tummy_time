#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import gzip
from datetime import datetime

import data_utils
import db_api

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

    arg_parser.add_argument('-q', '--query', action='store', nargs='+',
                            help='query the data for matching any of the '
                                 'supplied query strings. e.g -q burger pizza '
                                 'will return all entries matching \'burger\' '
                                 'or \'pizza\'')

    arg_parser.add_argument('-e', '--estimate-time',
                            action='store_true', default=False,
                            help='calculate estimated time arrival for the '
                                 'resulting query entries')

    arg_parser.add_argument('--alias-create', action='store',
                            help='add query alias, use with -q switch. Use -q '
                                 'switch without this option to dry-run the '
                                 'query')

    arg_parser.add_argument('--alias-delete', action='store',
                            help='delete query alias')

    arg_parser.add_argument('--alias-list', action='store_true',
                            default=False, help='list existing aliases')

    arg_parser.add_argument('-Q', '--alias-query', action='store',
                            default=False, help='run aliased query')

    return arg_parser.parse_args()


def init_db():
    print('initializing DB')
    db_api.purge_db()


def fetch_data():
    print('fetching data')
    fetcher = data_utils.Fetcher(url=ARCHIVES_URL,
                                 first_archive_date=FIRST_ARCHIVE,
                                 archive_suffix=ARCHIVE_SUFFIX)
    return fetcher.fetch()


def parse_data(archives):
    print('parsing data')
    parser = data_utils.Parser()
    for archive in archives:
        with gzip.open(archive, 'rb') as f:
            data = f.read()
        parser.parse(data)


def populate_food_arrivals_data():
    archives = fetch_data()
    parse_data(archives)


def output_to_file(f, db):
    db.dump_food_arrivals_to_file(f)


def query_restaurants(query):
    res = db_api.filter_restaurant_subject(query)
    for r in res:
        print(r.subject, r.arrival_time)

    return res


def dump_restaurant_stats(restaurants):
    times_list = [r.arrival_time for r in restaurants]
    print('-' * 50)
    if times_list:
        print('estimation: {}'.format(data_utils.calc_ema(times_list)))


def create_query_alias(alias_name, query):
    db_api.alias_create(alias_name, query)


def delete_query_alias(alias_name):
    db_api.alias_delete(alias_name)


def dump_aliases():
    for a in db_api.alias_list_all():
        print(u'{}: {}'.format(a.name, a.query_keywords))


def validate_arguments(args):
    if args.query and args.alias_query:
        raise ValueError(
            'invalid args: --alias-query and --query are mutual exclusive')


def main():
    args = get_args()

    if args.init_db:
        db_api.purge_db()

    if args.fetch_data:
        populate_food_arrivals_data()

    if args.alias_list:
        dump_aliases()
        return
    try:
        validate_arguments(args)
    except ValueError as e:
        print(e)
        return

    if args.alias_query:
        query = db_api.alias_query_get(args.alias_query)
        if not query:
            return
        args.query = query.query_keywords.split()

    if args.alias_delete:
        delete_query_alias(args.alias_delete)
        return

    results = []
    if args.query:
        results = query_restaurants(args.query)
        if args.alias_create:
            create_query_alias(args.alias_create, args.query)

    if args.estimate_time and results:
        dump_restaurant_stats(results)


if __name__ == '__main__':
    main()
