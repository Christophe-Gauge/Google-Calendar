#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Given a geographic location, determines the optimal viewing times from the ISS (code name ZARYA)
in the next 10 days between sunset and 10:30 pm, and creates calendar events if they don't already exist.

Uses the skyfield library for astronomical calculations, requires a local copy of the file de440.bsp
https://rhodesmill.org/skyfield/planets.html#ephemeris-download-links

Assumes that the Google Calendar libraries are installed and configured:
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Source: https://github.com/Christophe-Gauge/Google-Calendar
'''

# I M P O R T S ###############################################################

from __future__ import print_function
from __future__ import generators
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from skyfield import almanac
from skyfield.api import Topos, load
from skyfield.nutationlib import iau2000b
from datetime import datetime, timedelta, time
from dateutil.parser import parse as dtparse
from tzlocal import get_localzone
from pytz import timezone


__author__ = "Christophe Gauge"
__version__ = "1.0.1"
__license__ = "GNU General Public License v3.0"


# G L O B A L S ###############################################################

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SCOPES = ['https://www.googleapis.com/auth/calendar']

lat, lon = '20.7644 N', '156.4450 W'  # Your location's coordinates K
elv = 500  # Elevation in meters
# tzn = 'America/Los_Angeles'  # Your location's timezone if you chose to set it manually
# timezone = timezone(tzn)
timezone = get_localzone()  # Get System's timezone 
print(timezone)
bed_time = time(hour=23, minute=30, tzinfo=timezone)
number_of_days_to_process = 10  # We want to see if the ISS will fly over in the next x days
number_of_calendar_events = 20  # Retrieve x number of calendar events to see if we already have the flyover entries


# F U N C T I O N S ###########################################################


def Get_calendar_creds():
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
    return creds


def get_calendar_events():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 100 events on the user's calendar.
    """
    creds = Get_calendar_creds()
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(f'Getting the upcoming {number_of_calendar_events} events from the Calendar')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=number_of_calendar_events, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events


def createEvent(summary, startDate, endDate):
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.

    creds = Get_calendar_creds()
    service = build('calendar', 'v3', credentials=creds)

    event = {
      'summary': summary,
      'start': {
        'dateTime': startDate,
        'timeZone': str(timezone),
      },
      'end': {
        'dateTime': endDate,
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
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    satellites = load.tle_file(stations_url)
    print('Loaded', len(satellites), 'satellites')
    by_name = {sat.name: sat for sat in satellites}
    planets = load('./de440.bsp')

    by_name = {sat.name: sat for sat in satellites}
    satellite = by_name['ISS (ZARYA)']
    print(satellite)

    ts = load.timescale(builtin=True)
    sun = planets['sun']
    earth = planets['earth']

    # Let's get the sunset time today at the given location
    loc = Topos(lat, lon, elevation_m=elv)
    t0 = ts.utc(datetime.now(timezone))
    t1 = ts.utc(datetime.now(timezone) + timedelta(days=1))
    f = almanac.sunrise_sunset(planets, loc)
    t, y = almanac.find_discrete(t0, t1, f)
    for ti, yi in zip(t, y):
        print(ti.astimezone(timezone), 'Rise' if yi else 'Set')
        if not yi:
            sunset_time = ti.astimezone(timezone)
    print(f'Sunset Time: {sunset_time}')
    print('-'*30)

    # Get the current Google Calendar events so that we can see if we already hav ethe generated events
    myEvents = get_calendar_events()

    # Let's see is the ISS will be visible and sunlit in the next few days
    for days in range(0, number_of_days_to_process):
        try:
            # Adjust the sunset and bet time dates
            sunset_today = sunset_time + timedelta(days=days)
            print(f'Sunset: {sunset_today}')
            bed_time_today = datetime.combine(sunset_today, bed_time)
            print(f'Bedtime: {bed_time_today}')

            t0 = ts.from_datetime(sunset_today)
            t1 = ts.from_datetime(bed_time_today)
            # print(t0.tt_strftime(), t1.tt_strftime())
            t, passes = satellite.find_events(loc, t0, t1, altitude_degrees=30.0)
            is_sunlit = False  # We only want to create an event if the ISS is sunlit and visible
            for ti, event in zip(t, passes):
                sunlit = satellite.at(ti).is_sunlit(planets)
                print(f"{ti.astimezone(timezone)}  {('rise above 30°', 'culminate', 'set below 30°')[event]} is in {'sunlight' if sunlit else 'shadow'}")
                if sunlit:
                    is_sunlit = True
            if is_sunlit and len(t) > 2:
                # Round the event time to the nearest minute
                event_start_date = t[0].astimezone(timezone).replace(second=0, microsecond=0)
                event_end_date = t[2].astimezone(timezone).replace(second=0, microsecond=0)
                print(event_start_date)

                # Let's see if we already have this event in the calendar
                already_have_it = False
                for event in myEvents:
                    if event['summary'] ==  'ISS Fly-over':
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        start_date = dtparse(start).astimezone(timezone)
                        # print(start_date, event_start_date)
                        if start_date == event_start_date:
                            print('  ---> Already have it')
                            already_have_it = True
                            break
                if not already_have_it:
                    print('creating event')
                    createEvent('ISS Fly-over', event_start_date.isoformat(), event_end_date.isoformat())
        except Exception as e:
            print("ERROR: %s" % e)

        print('-'*30)
    sys.exit(0)


###############################################################################

if __name__ == "__main__":
    main()

# E N D   O F   F I L E #######################################################
