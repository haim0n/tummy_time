from __future__ import print_function

# from apiclient import discovery

from oauth2client import tools

from gmail_client_api import GmailClientApi

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


def print_formatted_msgs(client, msg_id_list):
    for msg_id in msg_id_list:
        msg = client.get_message(user_id='me', msg_id=msg_id)
        print(msg)


def main():
    gclient = GmailClientApi(flags)
    # a list of [ {"id": "153a833d1dbee17e", "threadId": "153a833d1dbee17e"}]
    messages = gclient.list_messages_matching_query(
        user_id='me',
        query='to: tlv-food-arrivals')

    msg_ids = [m['id'] for m in messages]
    print_formatted_msgs(gclient, msg_ids)

if __name__ == '__main__':
    main()