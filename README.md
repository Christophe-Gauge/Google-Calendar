# Google-Calendar
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL_v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

Useful Python scripts using Google Calendar.



All of these scripts assume that the Google Calendar libraries are installed and configured:
`pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

They also assume that you have your Google Calendar API credentials stored in a file named `credentials.json` in the local directory.

The following Python libraries are also needed in order to properly deal with timezones:
```
pip3 install pytz
pip3 install get_localzone
```


## Calendar Reminders

[calendar_reminders.py](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/calendar_reminders.py)

For each event in your Google Calendar ensures that the proper event reminders are set. Defaults are a popup 30 and 10 minutes before the event.




## Add Work Holidays

[add_work_holidays.py](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/add_work_holidays.py)

This script can be used to create new events based on a list of dates in plaintext.



## Add Flight Info

[add_flight_info.py](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/add_flight_info.py)

Given a travel itinerary in .yaml format, creates entries in a Google Calendar with departure and arrival times in local timezones.

It uses the [airport_timezone.tsv](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/airport_timezone.tsv) Airport data file, which is included in this repository and is extracted from the (opentraveldata)[https://github.com/opentraveldata/opentraveldata] data using [get_airports_timezone.py](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/get_airports_timezone.py). The file contains the three letter IATA codes, the full name, and the timezone for the world's airport's.



Additional requirements:
```
pip3 install pyaml
```


## ISS Visible

[iss_visible.py](https://github.com/Christophe-Gauge/Google-Calendar/blob/main/iss_visible.py)

Given a geographic location, determines the optimal viewing times from the ISS (code name ZARYA) in the next 10 days between sunset and 10:30 pm, and creates calendar events if they don't already exist.
Optimal viewing conditions are defined as when the ISS is at least 30 degrees above the horizon from the viewing location and lit by the sun.

This script uses the skyfield library for astronomical calculations, and requires a local copy of the file [de440.bsp](https://rhodesmill.org/skyfield/planets.html#ephemeris-download-links) which should be downloaded automatically the first time you run the script.


Additional requirements:
```
pip3 install skyfield
```