#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import gzip
import sys
import urllib2

import constants
import data_utils
import db_api


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

    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(1)

    return arg_parser.parse_args()


def init_db():
    print('initializing DB')
    db_api.purge_db()


def fetch_data():
    print('fetching data')
    fetcher = data_utils.Fetcher(url=constants.ARCHIVES_URL,
                                 first_archive_date=constants.FIRST_ARCHIVE,
                                 archive_suffix=constants.ARCHIVE_SUFFIX)
    ret = []
    try:
        ret = fetcher.fetch()
    except urllib2.URLError as e:
        print(e)
    finally:
        return ret


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
            'invalid args: --alias-query and --query are mutually exclusive')

    if args.alias_delete:
        if any([args.alias_list, args.alias_query, args.alias_create]):
            raise ValueError(
                'invalid args: --alias-delete cannot be used with any alias'
                'options')

    if args.alias_create:
        if any([args.alias_list, args.alias_query, args.alias_delete]):
            raise ValueError(
                'invalid args: --alias-create cannot be used with any alias'
                'options')
        if not args.query:
            raise ValueError('invalid args: use -q to provide the query')


def main():
    args = get_args()
    try:
        validate_arguments(args)
    except ValueError as e:
        print(e)
        return

    if args.init_db:
        db_api.purge_db()

    if args.fetch_data:
        populate_food_arrivals_data()

    if args.alias_list:
        dump_aliases()
        return

    if args.alias_delete:
        delete_query_alias(args.alias_delete)
        return

    if args.alias_query:
        query = db_api.alias_query_get(args.alias_query)
        if not query:
            return
        args.query = query.query_keywords.split()

    results = []
    if args.query:
        results = query_restaurants(args.query)
        if args.alias_create:
            create_query_alias(args.alias_create, args.query)

    if args.estimate_time and results:
        dump_restaurant_stats(results)


if __name__ == '__main__':
    main()
