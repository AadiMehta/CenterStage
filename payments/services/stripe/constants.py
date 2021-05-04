

STIPE_COUNTRIES = [
    {
        "name": "Australia (AU)",
        "code": "AU",
        "bank": {
            "routing_number": {
                "required": True,
                "name": "BSB",
                "max_length": 6,
                "min_length": 6
            },
            "account_number": {
                "required": True,
                "name": "Account number",
                "max_length": 5,
                "min_length": 9
            },
        }
    },
    {
        "name": "Austria (AT)",
        "code": "AT",
        "bank": {
            "routing_number": {
                "required": False,
                "name": "",
                "max_length": 0,
                "min_length": 0
            },
            "account_number": {
                "required": True,
                "name": "IBAN",
                "max_length": 21,
                "min_length": 20
            },
        }
    },
    {
        "name": "Belgium (BE)",
        "code": "BE",
        "bank": {
            "routing_number": {
                "required": False,
                "name": "",
                "max_length": 0,
                "min_length": 0
            },
            "account_number": {
                "required": True,
                "name": "IBAN",
                "max_length": 21,
                "min_length": 20
            },
        }
    },
    {
        "name": "Brazil (BR)",
        "code": "BR"
    },
    {
        "name": "Bulgaria (BG)",
        "code": "BG"
    },
    {
        "name": "Canada (CA)",
        "code": "CA"
    },
    {
        "name": "Cyprus (CY)",
        "code": "CY"
    },
    {
        "name": "Czech Republic (CZ)",
        "code": "CZ"
    },
    {"name": "Denmark (DK)", "code": "DK"},
    {"name": "Estonia (EE)", "code": "EE"},
    {"name": "Finland (FI)", "code": "FI"},
    {"name": "France (FR)", "code": "FR"},
    {"name": "Germany (DE)", "code": "DE"},
    {"name": "Gibraltar (GI)", "code": "GI"},
    {"name": "Greece (GR)", "code": "GR"},
    {"name": "Hong Kong (HK)", "code": "HK"},
    {"name": "Hungary (HU)", "code": "HU"},
    {"name": "India (IN)", "code": "IN"},
    {"name": "Ireland (IE)", "code": "IE"},
    {"name": "Italy (IT)", "code": "IT"},
    {"name": "Japan (JP)", "code": "JP"},
    {"name": "Liechtenstein (LI)", "code": "LI"},
    {"name": "Lithuania (LT)", "code": "LT"},
    {"name": "Luxembourg (LU)", "code": "LU"},
    {"name": "Latvia (LV)", "code": "LV"},
    {"name": "Malta (MT)", "code": "MT"},
    {"name": "Malaysia (MY)", "code": "MY"},
    {"name": "Mexico (MX)", "code": "MX"},
    {"name": "Netherlands (NL)", "code": "NL"},
    {"name": "New Zealand (NZ)", "code": "NZ"},
    {"name": "Norway (NO)", "code": "NO"},
    {"name": "Poland (PL)", "code": "PL"},
    {"name": "Portugal (PT)", "code": "PT"},
    {"name": "Romania (RO)", "code": "RO"},
    {"name": "Singapore (SG)", "code": "SG"},
    {"name": "Slovakia (SK)", "code": "SK"},
    {"name": "Slovenia (SI)", "code": "SI"},
    {"name": "Spain (ES)", "code": "ES"},
    {"name": "Sweden (SE)", "code": "SE"},
    {"name": "Switzerland (CH)", "code": "CH"},
    {"name": "United Kingdom (GB)", "code": "GB"},
    {"name": "United States (US)", "code": "US"}
]


STRIPE_CURRENCIES = [
    {
        'code': 'AED',
        'label': 'United Arab Emirates Dirham'
    },
    {
        'code': 'AFN',
        'label': 'Afghan Afghani'
    },
    {
        'code': 'ALL',
        'label': 'Albanian Lek'
    },
    {
        'code': 'AMD',
        'label': 'Armenian Dram'
    },
    {
        'code': 'ANG',
        'label': 'Netherlands Antillean Gulden'
    },
    {
        'code': 'AOA',
        'label': 'Angolan Kwanza'
    },
    {
        'code': 'ARS',
        'label': 'Argentine Peso'
    },
    {
        'code': 'AUD',
        'label': 'Australian Dollar'
    },
    {
        'code': 'AWG',
        'label': 'Aruban Florin'
    },
    {
        'code': 'AZN',
        'label': 'Azerbaijani Manat'
    },
    {
        'code': 'BAM',
        'label': 'Bosnia & Herzegovina Convertible Mark'
    },
    {
        'code': 'BBD',
        'label': 'Barbadian Dollar'
    },
    {
        'code': 'BDT',
        'label': 'Bangladeshi Taka'
    },
    {
        'code': 'BGN',
        'label': 'Bulgarian Lev'
    },
    {
        'code': 'BIF',
        'label': 'Burundian Franc'
    },
    {
        'code': 'BMD',
        'label': 'Bermudian Dollar'
    },
    {
        'code': 'BND',
        'label': 'Brunei Dollar'
    },
    {
        'code': 'BOB',
        'label': 'Bolivian Boliviano'
    },
    {
        'code': 'BRL',
        'label': 'Brazilian Real'
    },
    {
        'code': 'BSD',
        'label': 'Bahamian Dollar'
    },
    {
        'code': 'BWP',
        'label': 'Botswana Pula'
    },
    {
        'code': 'BZD',
        'label': 'Belize Dollar'
    },
    {
        'code': 'CAD',
        'label': 'Canadian Dollar'
    },
    {
        'code': 'CDF',
        'label': 'Congolese Franc'
    },
    {
        'code': 'CHF',
        'label': 'Swiss Franc'
    },
    {
        'code': 'CLP',
        'label': 'Chilean Peso'
    },
    {
        'code': 'CNY',
        'label': 'Chinese Renminbi Yuan'
    },
    {
        'code': 'COP',
        'label': 'Colombian Peso'
    },
    {
        'code': 'CRC',
        'label': 'Costa Rican Colón'
    },
    {
        'code': 'CVE',
        'label': 'Cape Verdean Escudo'
    },
    {
        'code': 'CZK',
        'label': 'Czech Koruna'
    },
    {
        'code': 'DJF',
        'label': 'Djiboutian Franc'
    },
    {
        'code': 'DKK',
        'label': 'Danish Krone'
    },
    {
        'code': 'DOP',
        'label': 'Dominican Peso'
    },
    {
        'code': 'DZD',
        'label': 'Algerian Dinar'
    },
    {
        'code': 'EGP',
        'label': 'Egyptian Pound'
    },
    {
        'code': 'ETB',
        'label': 'Ethiopian Birr'
    },
    {
        'code': 'EUR',
        'label': 'Euro'
    },
    {
        'code': 'FJD',
        'label': 'Fijian Dollar'
    },
    {
        'code': 'FKP',
        'label': 'Falkland Islands Pound'
    },
    {
        'code': 'GBP',
        'label': 'British Pound'
    },
    {
        'code': 'GEL',
        'label': 'Georgian Lari'
    },
    {
        'code': 'GIP',
        'label': 'Gibraltar Pound'
    },
    {
        'code': 'GMD',
        'label': 'Gambian Dalasi'
    },
    {
        'code': 'GNF',
        'label': 'Guinean Franc'
    },
    {
        'code': 'GTQ',
        'label': 'Guatemalan Quetzal'
    },
    {
        'code': 'GYD',
        'label': 'Guyanese Dollar'
    },
    {
        'code': 'HKD',
        'label': 'Hong Kong Dollar'
    },
    {
        'code': 'HNL',
        'label': 'Honduran Lempira'
    },
    {
        'code': 'HRK',
        'label': 'Croatian Kuna'
    },
    {
        'code': 'HTG',
        'label': 'Haitian Gourde'
    },
    {
        'code': 'HUF',
        'label': 'Hungarian Forint'
    },
    {
        'code': 'IDR',
        'label': 'Indonesian Rupiah'
    },
    {
        'code': 'ILS',
        'label': 'Israeli New Sheqel'
    },
    {
        'code': 'INR',
        'label': 'Indian Rupee'
    },
    {
        'code': 'ISK',
        'label': 'Icelandic Króna'
    },
    {
        'code': 'JMD',
        'label': 'Jamaican Dollar'
    },
    {
        'code': 'JPY',
        'label': 'Japanese Yen'
    },
    {
        'code': 'KES',
        'label': 'Kenyan Shilling'
    },
    {
        'code': 'KGS',
        'label': 'Kyrgyzstani Som'
    },
    {
        'code': 'KHR',
        'label': 'Cambodian Riel'
    },
    {
        'code': 'KMF',
        'label': 'Comorian Franc'
    },
    {
        'code': 'KRW',
        'label': 'South Korean Won'
    },
    {
        'code': 'KYD',
        'label': 'Cayman Islands Dollar'
    },
    {
        'code': 'KZT',
        'label': 'Kazakhstani Tenge'
    },
    {
        'code': 'LAK',
        'label': 'Lao Kip'
    },
    {
        'code': 'LBP',
        'label': 'Lebanese Pound'
    },
    {
        'code': 'LKR',
        'label': 'Sri Lankan Rupee'
    },
    {
        'code': 'LRD',
        'label': 'Liberian Dollar'
    },
    {
        'code': 'LSL',
        'label': 'Lesotho Loti'
    },
    {
        'code': 'MAD',
        'label': 'Moroccan Dirham'
    },
    {
        'code': 'MDL',
        'label': 'Moldovan Leu'
    },
    {
        'code': 'MGA',
        'label': 'Malagasy Ariary'
    },
    {
        'code': 'MKD',
        'label': 'Macedonian Denar'
    },
    {
        'code': 'MNT',
        'label': 'Mongolian Tögrög'
    },
    {
        'code': 'MOP',
        'label': 'Macanese Pataca'
    },
    {
        'code': 'MRO',
        'label': 'Mauritanian Ouguiya'
    },
    {
        'code': 'MUR',
        'label': 'Mauritian Rupee'
    },
    {
        'code': 'MVR',
        'label': 'Maldivian Rufiyaa'
    },
    {
        'code': 'MWK',
        'label': 'Malawian Kwacha'
    },
    {
        'code': 'MXN',
        'label': 'Mexican Peso'
    },
    {
        'code': 'MYR',
        'label': 'Malaysian Ringgit'
    },
    {
        'code': 'MZN',
        'label': 'Mozambican Metical'
    },
    {
        'code': 'NAD',
        'label': 'Namibian Dollar'
    },
    {
        'code': 'NGN',
        'label': 'Nigerian Naira'
    },
    {
        'code': 'NIO',
        'label': 'Nicaraguan Córdoba'
    },
    {
        'code': 'NOK',
        'label': 'Norwegian Krone'
    },
    {
        'code': 'NPR',
        'label': 'Nepalese Rupee'
    },
    {
        'code': 'NZD',
        'label': 'New Zealand Dollar'
    },
    {
        'code': 'PAB',
        'label': 'Panamanian Balboa'
    },
    {
        'code': 'PEN',
        'label': 'Peruvian Nuevo Sol'
    },
    {
        'code': 'PGK',
        'label': 'Papua New Guinean Kina'
    },
    {
        'code': 'PHP',
        'label': 'Philippine Peso'
    },
    {
        'code': 'PKR',
        'label': 'Pakistani Rupee'
    },
    {
        'code': 'PLN',
        'label': 'Polish Złoty'
    },
    {
        'code': 'PYG',
        'label': 'Paraguayan Guaraní'
    },
    {
        'code': 'QAR',
        'label': 'Qatari Riyal'
    },
    {
        'code': 'RON',
        'label': 'Romanian Leu'
    },
    {
        'code': 'RSD',
        'label': 'Serbian Dinar'
    },
    {
        'code': 'RUB',
        'label': 'Russian Ruble'
    },
    {
        'code': 'RWF',
        'label': 'Rwandan Franc'
    },
    {
        'code': 'SAR',
        'label': 'Saudi Riyal'
    },
    {
        'code': 'SBD',
        'label': 'Solomon Islands Dollar'
    },
    {
        'code': 'SCR',
        'label': 'Seychellois Rupee'
    },
    {
        'code': 'SEK',
        'label': 'Swedish Krona'
    },
    {
        'code': 'SGD',
        'label': 'Singapore Dollar'
    },
    {
        'code': 'SHP',
        'label': 'Saint Helenian Pound'
    },
    {
        'code': 'SLL',
        'label': 'Sierra Leonean Leone'
    },
    {
        'code': 'SOS',
        'label': 'Somali Shilling'
    },
    {
        'code': 'SRD',
        'label': 'Surinamese Dollar'
    },
    {
        'code': 'STD',
        'label': 'São Tomé and Príncipe Dobra'
    },
    {
        'code': 'SVC',
        'label': 'Salvadoran Colón'
    },
    {
        'code': 'SZL',
        'label': 'Swazi Lilangeni'
    },
    {
        'code': 'THB',
        'label': 'Thai Baht'
    },
    {
        'code': 'TJS',
        'label': 'Tajikistani Somoni'
    },
    {
        'code': 'TOP',
        'label': 'Tongan Paʻanga'
    },
    {
        'code': 'TRY',
        'label': 'Turkish Lira'
    },
    {
        'code': 'TTD',
        'label': 'Trinidad and Tobago Dollar'
    },
    {
        'code': 'TWD',
        'label': 'New Taiwan Dollar'
    },
    {
        'code': 'TZS',
        'label': 'Tanzanian Shilling'
    },
    {
        'code': 'UAH',
        'label': 'Ukrainian Hryvnia'
    },
    {
        'code': 'UGX',
        'label': 'Ugandan Shilling'
    },
    {
        'code': 'USD',
        'label': 'United States Dollar'
    },
    {
        'code': 'UYU',
        'label': 'Uruguayan Peso'
    },
    {
        'code': 'UZS',
        'label': 'Uzbekistani Som'
    },
    {
        'code': 'VND',
        'label': 'Vietnamese Đồng'
    },
    {
        'code': 'VUV',
        'label': 'Vanuatu Vatu'
    },
    {
        'code': 'WST',
        'label': 'Samoan Tala'
    },
    {
        'code': 'XAF',
        'label': 'Central African Cfa Franc'
    },
    {
        'code': 'XCD',
        'label': 'East Caribbean Dollar'
    },
    {
        'code': 'XOF',
        'label': 'West African Cfa Franc'
    },
    {
        'code': 'XPF',
        'label': 'Cfp Franc'
    },
    {
        'code': 'YER',
        'label': 'Yemeni Rial'
    },
    {
        'code': 'ZAR',
        'label': 'South African Rand'
    },
    {
        'code': 'ZMW',
        'label': 'Zambian Kwacha'
    }
]

STRIPE_ZERO_DECIMAL_CURRENCIES = [
    "BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA", "PYG", "RWF", "UGX", "VND", "VUV", "XAF", "XOF", "XPF"
]
