#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Takes a list of days in plaintext and converts them to full-day events in a Google Calendar.

Assumes that the Google Calendar libraries are installed and configured:
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Source: https://github.com/Christophe-Gauge/Google-Calendar
'''

# I M P O R T S ###############################################################

from __future__ import print_function
from __future__ import generators
from pytz import timezone
from dateutil.parser import parse as dtparse
from datetime import datetime, timedelta
from dateutil import parser
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tzlocal import get_localzone


__author__ = "Christophe Gauge"
__version__ = "1.0.1"
__license__ = "GNU General Public License v3.0"


# G L O B A L S ###############################################################

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']

timezone = get_localzone()
print(timezone)

myYear = ' 2021'
work_dates = """Friday, January 1
Thursday, Dec. 31
Monday, January 18
Monday, February 15
Monday, May 31
Monday, July 5
Monday, September 6
Thursday, November 25
Friday, November 26
Thursday, December 23
Friday, December 24
Monday, December 27"""


# F U N C T I O N S ###########################################################


def createAllDayEvent(summary, startDate):
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    event = {
      'summary': summary,
      'start': {
        'date': startDate,
        'timeZone': str(timezone),
      },
      'end': {
        'date': startDate,
        'timeZone': str(timezone),
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 30},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def main():
    """Main function."""
    for myDate in work_dates.split('\n'):
        if myDate.strip() != "":
            holiday = parser.parse(myDate + myYear).date().isoformat()
            print(holiday)
            createAllDayEvent('Work Holiday', holiday)

###############################################################################

if __name__ == "__main__":
    main()

# E N D   O F   F I L E #######################################################
