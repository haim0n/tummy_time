#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse


def get_args():
    arg_parser = argparse.ArgumentParser(description='Food arrival stats')
    arg_parser.add_argument('-Z', '--init-db', action='store_true',
                            help='purge all local data', default=False)

    arg_parser.add_argument('-F', '--fetch-data', action='store_true',
                            default=False,
                            help='fetch data and populate local db with it')

    arg_parser.add_argument('-O', '--output-to-file',
                            type=argparse.FileType('w'),
                            help='dump db contents formatted as csv')

    arg_parser.add_argument('-L', '--list-all-restaurants',
                            action='store_true',
                            help='shows a list of restaurants from local db')

    arg_parser.add_argument('-d', '--dump-restaurant-stats')

    return arg_parser.parse_args()


def init_db():
    print('initializing DB')
    data_utils.Db.purge_db()


def fetch_data():
    print('fetching data')
    fetcher = data_utils.Fetcher()
    formatted_data_list = fetcher.get_formatted_data()
    for data_items in formatted_data_list:
        for data in data_items:
            print('fetched {}'.format(data.to_csv()))
            yield data


def populate_food_arrivals_data(db):
    data = fetch_data()
    print('updating db')
    for d in data:
        db.update_food_arrivals_table(uid=d.uid, date=d.date,
                                      data=d.parsed_data)


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
        init_db()

    db = data_utils.Db()
    if args.fetch_data:
        populate_food_arrivals_data(db)

    if args.output_to_file:
        output_to_file(args.output_to_file, db)

    if args.list_all_restaurants:
        list_all_restaurants(db)

    if args.dump_restaurant_stats:
        dump_restaurant_stats(db, args.dump_restaurant_stats)


if __name__ == '__main__':
    main()
