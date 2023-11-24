#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Retrieve opentraveldata CSV file from GitHub and save the world airports IATA Code, Name and TimeZone into a TSV file.
https://github.com/opentraveldata/opentraveldata

Source: https://github.com/Christophe-Gauge/Google-Calendar
'''

# I M P O R T S ###############################################################

import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

__author__ = "Christophe Gauge"
__version__ = "1.0.1"
__license__ = "GNU General Public License v3.0"


# G L O B A L S ###############################################################

URL = 'https://raw.githubusercontent.com/opentraveldata/opentraveldata/master/opentraveldata/optd_por_public_all.csv'

df = pd.read_csv(URL, sep = "^", usecols=["iata_code", "name", "timezone"], index_col = False, low_memory=False)
df = df[df.iata_code.notnull()]
df.reset_index(drop=True, inplace = True)
df.drop_duplicates(subset ="iata_code", keep = "last", inplace = True)

print(df)
df.to_csv('airport_timezone.tsv', sep="\t", index=False)
