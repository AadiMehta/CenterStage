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

timezones = pytz.all_timezones

currency_data = currency.data._currencies

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
