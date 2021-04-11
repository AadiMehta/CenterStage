import copy
import datetime

import pytz
import currency


languages = [{'label': 'English', 'value': 'English'},
 {'label': 'Mandarin', 'value': 'Mandarin'},
 {'label': 'Hindi', 'value': 'Hindi'},
 {'label': 'Spanish', 'value': 'Spanish'},
 {'label': 'French', 'value': 'French'},
 {'label': 'Arabic', 'value': 'Arabic'},
 {'label': 'Bengali', 'value': 'Bengali'},
 {'label': 'Russian', 'value': 'Russian'},
 {'label': 'Portuguese', 'value': 'Portuguese'},
 {'label': 'Indonesian', 'value': 'Indonesian'},
 {'label': 'Japanese', 'value': 'Japanese'},
 {'label': 'Punjabi', 'value': 'Punjabi'},
 {'label': 'Marathi', 'value': 'Marathi'},
 {'label': 'Urdu', 'value': 'Urdu'},
 {'label': 'Gujarati', 'value': 'Gujarati'},
 {'label': 'Polish', 'value': 'Polish'},
 {'label': 'Tamil', 'value': 'Tamil'},
 {'label': 'Telugu', 'value': 'Telugu'},
 {'label': 'German', 'value': 'German'},
 {'label': 'Italian', 'value': 'Italian'}]

get_offset = lambda item: "(GMT" + datetime.datetime.now(pytz.timezone(item)).strftime('%z')[0:3] + ":" \
                          + datetime.datetime.now(pytz.timezone(item)).strftime('%z')[3:] + ") " + item

tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones]
tz_sorted = sorted(tz, key=lambda x: int(x[1].split()[0]))

timezones = [
    dict(label=get_offset(tz[0]), value=tz[0]) for tz in tz_sorted
]

currency_data = copy.deepcopy(currency.data._currencies)
del currency_data['BTC']
del currency_data['ETH']
del currency_data['LTC']
del currency_data['ADA']

format_currency = lambda currency: '{} {}'.format(currency['symbol_native'], currency['name'])

currencies = [
    dict(
        label=format_currency(currency_data[code]),
        value=code
    )
    for code in currency_data
]

currency_labels = {}
for code in currency_data:
    currency_labels[code] = dict(
        label=format_currency(currency_data[code]),
        symbol=currency_data[code]['symbol_native'],
        value=code
    )
