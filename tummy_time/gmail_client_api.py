from __future__ import print_function

import os

import httplib2
from apiclient import errors
from apiclient import discovery

import oauth2client
from oauth2client import client
from oauth2client import tools

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class GmailMessage(object):
    def __init__(self, email_message):
        self.email_message = email_message
        self.headers = self.email_message['payload']['headers']
        self.parse_message_params()

    def parse_message_header(self, hdr):
        if hdr['name'] == 'Subject':
            self.subject = hdr['value']
        elif hdr['name'] == 'Date':
            self.date = hdr['value']

    def parse_message_params(self):
        self.id = self.email_message['id']
        for h in self.headers:
            self.parse_message_header(h)

    def __str__(self):
        return ','.join((self.id, self.subject, self.date))


class GmailClientApi(object):
    def __init__(self, flags):
        self.flags = flags
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build(serviceName='gmail', version='v1',
                                       http=self.http)

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        :returns: The obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def get_message(self, user_id, msg_id):
        """Get a Message with given ID.

          :param user_id: User's email address. The special value 'me' can be
          used to indicate the authenticated user.

          :param msg_id: The ID of the Message required.

        :returns: A Message.
        """
        try:
            message = self.service.users().messages().get(userId=user_id,
                                                          id=msg_id).execute()
            # print('Message snippet: %s' % message['snippet'])

            return GmailMessage(message)

        except errors.HttpError, error:
            print('An error occurred: %s' % error)

    def list_messages_matching_query(self, user_id, query=''):
        """List all Messages of the user's mailbox matching the query.

          :param user_id: User's email address. The special value 'me'
          can be used to indicate the authenticated user.
          :param query: String used to filter messages returned.
          Eg.- 'from:user@some_domain.com' for Messages from a particular
          sender.

        :returns: List of Messages that match the criteria of the query.
        Note that the returned list contains Message IDs, you must use get with
        the appropriate ID to get the details of a message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id,
                                                            q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(
                    userId=user_id,
                    q=query,
                    pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages

        except errors.HttpError, error:
            print('An error occurred: %s' % error)
