#! /usr/bin/env python

from __future__ import print_function

from oauth2client import tools
from tummy_time.gmail_client_api import GmailClientApi

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


def print_formatted_msgs(msg_list):
    for msg in msg_list:
        print(msg)

def get_msg_objects(client):
    """
    :param client: gmail client
    :return: list of GmailMessage objects
    """

    # a list of [ {"id": "153a833d1dbee17e", "threadId": "153a833d1dbee17e"}]
    messages = client.list_messages_matching_query(
        query='to: tlv-food-arrivals')
    msg_ids = [m['id'] for m in messages]

    return [client.get_message(msg_id=msg_id) for msg_id in msg_ids]


def main():
    gclient = GmailClientApi(flags)
    msg_objects = get_msg_objects(gclient)
    print_formatted_msgs(msg_objects)

if __name__ == '__main__':
    main()