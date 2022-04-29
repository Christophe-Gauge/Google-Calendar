#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Given a travel itinerary in .yaml format, creates entries in a Google Calendar with departure and arrival times in local timezones.

Uses Airport data file extracted from https://github.com/opentraveldata/opentraveldata

Assumes that the Google Calendar libraries are installed and configured:
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Source: https://github.com/Christophe-Gauge/Google-Calendar
'''

# I M P O R T S ###############################################################

from dateutil import parser
import yaml
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


__author__ = "Christophe Gauge"
__version__ = "1.0.1"
__license__ = "GNU General Public License v3.0"


# G L O B A L S ###############################################################

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']


flight_description = 'Confirmation number: ABCDEF\neTicket number: 123456789'
my_flights = """
- name: UA1813
  departure:
    airport: TPA
    time: Sat, May 08, 2021 05:30 PM
  arrival:
    airport: IAH
    time: Sat, May 08, 2021 06:58 PM
- name: UA46
  departure:
    airport: IAH
    time: Sat, May 08, 2021 07:40 PM
  arrival:
    airport: FRA
    time: Sat, May 09, 2021 12:20 PM
- name: LH1092
  departure:
    airport: FRA
    time: Sun, May 09, 2021 04:25 PM
  arrival:
    airport: BIA
    time: Sun, May 09, 2021 06:00 PM
- name: LH2281
  departure:
    airport: BIA
    time: Sat, Jul 10, 2021 05:20 PM
  arrival:
    airport: MUC
    time: Sat, Jul 10, 2021 06:40 PM
- name: UA107
  departure:
    airport: MUC
    time: Sun, Jul 11, 2021 12:20 PM
  arrival:
    airport: IAD
    time: Sun, Jul 11, 2021 03:10 PM
- name: UA2437
  departure:
    airport: IAD
    time: Sun, Jul 11, 2021 05:09 PM
  arrival:
    airport: TPA
    time: Sun, Jul 11, 2021 07:14 PM
"""
flights = yaml.safe_load(my_flights)

with open("airport_timezone.tsv") as file:
    data = file.read()
airports = {}
for line in data.split('\n'):
    if line != '':
        iata_code, airport_name, timezone = line.split('\t')
        airports[iata_code] = {"airport_name": airport_name, "timezone": timezone}


# F U N C T I O N S ###########################################################


def main():
  """Main function."""
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

  for flight in flights:
      print(flight['name'])
      print(flight['departure']['airport'], airports[flight['departure']['airport']])
      flight_title = f"{flight['name']} - {airports[flight['departure']['airport']]['airport_name']} ({flight['departure']['airport']}) - {airports[flight['arrival']['airport']]['airport_name']} ({flight['arrival']['airport']})"

      my_event = {
          'summary': flight_title,
          'description': flight_description,
          'start': {
              'dateTime': parser.parse(flight['departure']['time']).isoformat(),
              'timeZone': airports[flight['departure']['airport']]['timezone'],
          },
          'end': {
              'dateTime': parser.parse(flight['arrival']['time']).isoformat(),
              'timeZone': airports[flight['arrival']['airport']]['timezone'],
          },
          'reminders': {
              'useDefault': False,
              'overrides': [
                  {'method': 'popup', 'minutes': 30},
                  {'method': 'popup', 'minutes': 10},
              ],
          },
      }

      print(my_event)
      event = service.events().insert(calendarId='primary', body=my_event).execute()
      print('Event created: %s' % (event.get('htmlLink')))


###############################################################################

if __name__ == "__main__":
    main()

# E N D   O F   F I L E #######################################################
