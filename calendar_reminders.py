#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
For each event in your Google Calendar ensures that popup reminders are set.

Assumes that the Google Calendar libraries are installed and configured:
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Source: https://github.com/Christophe-Gauge/Google-Calendar
'''

# I M P O R T S ###############################################################

from __future__ import print_function
from __future__ import generators
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil import tz
from dateutil.parser import parse as dtparse
from pytz import timezone
from datetime import datetime, timedelta
from tzlocal import get_localzone


__author__ = "Christophe Gauge"
__version__ = "1.0.1"
__license__ = "GNU General Public License v3.0"


# G L O B A L S ###############################################################


# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']

calendars = ['primary']
reminders = {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 30}, {'method': 'popup', 'minutes': 5}]}
number_of_calendar_events = 20  # Retrieve x number of calendar entries

timezone = get_localzone()
print(timezone)


# F U N C T I O N S ###########################################################


def get_service():
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
    return service


def get(service, calendarId):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print(f'Getting the upcoming {number_of_calendar_events} events')
    events_result = service.events().list(calendarId=calendarId, timeMin=now,
                                        maxResults=number_of_calendar_events, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def main():
    service = get_service()
    for calendar in calendars:
        myEvents = get(service, calendar)
        for event in myEvents:
            # All-day events have a date, not a dateTime
            if 'dateTime' in event['start']:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_date = dtparse(start).astimezone(timezone)
                print(event['summary'])
                print(start_date)
                if event['reminders']['useDefault'] is False \
                        and 'overrides' in event['reminders'] \
                        and {'method': 'popup', 'minutes': 5} in event['reminders']['overrides'] \
                        and {'method': 'popup', 'minutes': 30} in event['reminders']['overrides']:
                    pass
                else:
                    print('**** ', event['reminders'])
                    event['reminders'] = reminders
                    updated_event = service.events().update(calendarId=calendar, eventId=event['id'], body=event).execute()

                print('-'*20)


###############################################################################

if __name__ == "__main__":
    main()

# E N D   O F   F I L E #######################################################

