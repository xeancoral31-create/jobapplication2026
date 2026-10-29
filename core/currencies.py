"""core/currencies.py — Comprehensive ISO-4217 world currencies reference."""

# Raw registry of world currencies: (code, name, symbol)
ISO_CURRENCIES = [
    ("AED", "United Arab Emirates Dirham", "د.إ"),
    ("AFN", "Afghan Afghani", "؋"),
    ("ALL", "Albanian Lek", "L"),
    ("AMD", "Armenian Dram", "֏"),
    ("ANG", "Netherlands Antillean Guilder", "ƒ"),
    ("AOA", "Angolan Kwanza", "Kz"),
    ("ARS", "Argentine Peso", "$"),
    ("AUD", "Australian Dollar", "A$"),
    ("AWG", "Aruban Florin", "ƒ"),
    ("AZN", "Azerbaijani Manat", "₼"),
    ("BAM", "Bosnia-Herzegovina Convertible Mark", "KM"),
    ("BBD", "Barbadian Dollar", "Bds$"),
    ("BDT", "Bangladeshi Taka", "৳"),
    ("BGN", "Bulgarian Lev", "лв"),
    ("BHD", "Bahraini Dinar", ".د.ب"),
    ("BIF", "Burundian Franc", "FBu"),
    ("BMD", "Bermudan Dollar", "$"),
    ("BND", "Brunei Dollar", "B$"),
    ("BOB", "Bolivian Boliviano", "Bs."),
    ("BRL", "Brazilian Real", "R$"),
    ("BSD", "Bahamian Dollar", "B$"),
    ("BTN", "Bhutanese Ngultrum", "Nu."),
    ("BWP", "Botswanan Pula", "P"),
    ("BYN", "Belarusian Ruble", "Br"),
    ("BZD", "Belize Dollar", "BZ$"),
    ("CAD", "Canadian Dollar", "C$"),
    ("CDF", "Congolese Franc", "FC"),
    ("CHF", "Swiss Franc", "CHF"),
    ("CLP", "Chilean Peso", "$"),
    ("CNY", "Chinese Yuan", "¥"),
    ("COP", "Colombian Peso", "$"),
    ("CRC", "Costa Rican Colón", "₡"),
    ("CUP", "Cuban Peso", "$"),
    ("CVE", "Cape Verdean Escudo", "$"),
    ("CZK", "Czech Koruna", "Kč"),
    ("DJF", "Djiboutian Franc", "Fdj"),
    ("DKK", "Danish Krone", "kr"),
    ("DOP", "Dominican Peso", "RD$"),
    ("DZD", "Algerian Dinar", "دج"),
    ("EGP", "Egyptian Pound", "E£"),
    ("ERN", "Eritrean Nakfa", "Nfk"),
    ("ETB", "Ethiopian Birr", "Br"),
    ("EUR", "Euro", "€"),
    ("FJD", "Fijian Dollar", "FJ$"),
    ("FKP", "Falkland Islands Pound", "£"),
    ("GBP", "British Pound", "£"),
    ("GEL", "Georgian Lari", "₾"),
    ("GHS", "Ghanaian Cedi", "₵"),
    ("GIP", "Gibraltar Pound", "£"),
    ("GMD", "Gambian Dalasi", "D"),
    ("GNF", "Guinean Franc", "FG"),
    ("GTQ", "Guatemalan Quetzal", "Q"),
    ("GYD", "Guyanaese Dollar", "G$"),
    ("HKD", "Hong Kong Dollar", "HK$"),
    ("HNL", "Honduran Lempira", "L"),
    ("HRK", "Croatian Kuna", "kn"),
    ("HTG", "Haitian Gourde", "G"),
    ("HUF", "Hungarian Forint", "Ft"),
    ("IDR", "Indonesian Rupiah", "Rp"),
    ("ILS", "Israeli New Shekel", "₪"),
    ("INR", "Indian Rupee", "₹"),
    ("IQD", "Iraqi Dinar", "ع.د"),
    ("IRR", "Iranian Rial", "﷼"),
    ("ISK", "Icelandic Króna", "kr"),
    ("JMD", "Jamaican Dollar", "J$"),
    ("JOD", "Jordanian Dinar", "JD"),
    ("JPY", "Japanese Yen", "¥"),
    ("KES", "Kenyan Shilling", "KSh"),
    ("KGS", "Kyrgystani Som", "с"),
    ("KHR", "Cambodian Riel", "៛"),
    ("KMF", "Comorian Franc", "CF"),
    ("KPW", "North Korean Won", "₩"),
    ("KRW", "South Korean Won", "₩"),
    ("KWD", "Kuwaiti Dinar", "KD"),
    ("KYD", "Cayman Islands Dollar", "$"),
    ("KZT", "Kazakhstani Tenge", "₸"),
    ("LAK", "Laotian Kip", "₭"),
    ("LBP", "Lebanese Pound", "ل.ل"),
    ("LKR", "Sri Lankan Rupee", "Rs"),
    ("LRD", "Liberian Dollar", "L$"),
    ("LSL", "Lesotho Loti", "L"),
    ("LYD", "Libyan Dinar", "LD"),
    ("MAD", "Moroccan Dirham", "DH"),
    ("MDL", "Moldovan Leu", "L"),
    ("MGA", "Malagasy Ariary", "Ar"),
    ("MKD", "Macedonian Denar", "ден"),
    ("MMK", "Myanmar Kyat", "K"),
    ("MNT", "Mongolian Tugrik", "₮"),
    ("MOP", "Macanese Pataca", "MOP$"),
    ("MRU", "Mauritanian Ouguiya", "UM"),
    ("MUR", "Mauritian Rupee", "₨"),
    ("MVR", "Maldivian Rufiyaa", "Rf"),
    ("MWK", "Malawian Kwacha", "MK"),
    ("MXN", "Mexican Peso", "Mex$"),
    ("MYR", "Malaysian Ringgit", "RM"),
    ("MZN", "Mozambican Metical", "MT"),
    ("NAD", "Namibian Dollar", "N$"),
    ("NGN", "Nigerian Naira", "₦"),
    ("NIO", "Nicaraguan Córdoba", "C$"),
    ("NOK", "Norwegian Krone", "kr"),
    ("NPR", "Nepalese Rupee", "₨"),
    ("NZD", "New Zealand Dollar", "NZ$"),
    ("OMR", "Omani Rial", "ر.ع."),
    ("PAB", "Panamanian Balboa", "B/."),
    ("PEN", "Peruvian Sol", "S/"),
    ("PGK", "Papua New Guinean Kina", "K"),
    ("PHP", "Philippine Peso", "₱"),
    ("PKR", "Pakistani Rupee", "₨"),
    ("PLN", "Polish Zloty", "zł"),
    ("PYG", "Paraguayan Guarani", "₲"),
    ("QAR", "Qatari Rial", "QR"),
    ("RON", "Romanian Leu", "lei"),
    ("RSD", "Serbian Dinar", "дин."),
    ("RUB", "Russian Ruble", "₽"),
    ("RWF", "Rwandan Franc", "RF"),
    ("SAR", "Saudi Riyal", "SR"),
    ("SBD", "Solomon Islands Dollar", "SI$"),
    ("SCR", "Seychellois Rupee", "SR"),
    ("SDG", "Sudanese Pound", "SDG"),
    ("SEK", "Swedish Krona", "kr"),
    ("SGD", "Singapore Dollar", "S$"),
    ("SHP", "Saint Helena Pound", "£"),
    ("SLL", "Sierra Leonean Leone", "Le"),
    ("SOS", "Somali Shilling", "S"),
    ("SRD", "Surinamese Dollar", "Sr$"),
    ("SSP", "South Sudanese Pound", "SS£"),
    ("STN", "São Tomé & Príncipe Dobra", "Db"),
    ("SVC", "Salvadoran Colón", "₡"),
    ("SYP", "Syrian Pound", "£S"),
    ("SZL", "Swazi Lilangeni", "E"),
    ("THB", "Thai Baht", "฿"),
    ("TJS", "Tajikistani Somoni", "SM"),
    ("TMT", "Turkmenistani Manat", "T"),
    ("TND", "Tunisian Dinar", "DT"),
    ("TOP", "Tongan Paʻanga", "T$"),
    ("TRY", "Turkish Lira", "₺"),
    ("TTD", "Trinidad & Tobago Dollar", "TT$"),
    ("TWD", "New Taiwan Dollar", "NT$"),
    ("TZS", "Tanzanian Shilling", "TSh"),
    ("UAH", "Ukrainian Hryvnia", "₴"),
    ("UGX", "Ugandan Shilling", "USh"),
    ("USD", "US Dollar", "$"),
    ("UYU", "Uruguayan Peso", "$U"),
    ("UZS", "Uzbekistani Som", "so'm"),
    ("VES", "Venezuelan Bolívar", "Bs.S"),
    ("VND", "Vietnamese Dong", "₫"),
    ("VUV", "Vanuatu Vatu", "VT"),
    ("WST", "Samoan Tala", "WS$"),
    ("XAF", "Central African CFA Franc", "FCFA"),
    ("XCD", "East Caribbean Dollar", "EC$"),
    ("XOF", "West African CFA Franc", "CFA"),
    ("XPF", "CFP Franc", "CFPF"),
    ("YER", "Yemeni Rial", "﷼"),
    ("ZAR", "South African Rand", "R"),
    ("ZMW", "Zambian Kwacha", "ZK"),
    ("ZWL", "Zimbabwean Dollar", "Z$"),
]

# Quick symbol map
CURRENCY_SYMBOLS = {code: sym for code, _name, sym in ISO_CURRENCIES}

# Quick name map
CURRENCY_NAMES = {code: name for code, name, _sym in ISO_CURRENCIES}

# Priority/popular currencies shown at top for rapid selection
POPULAR_CODES = [
    "USD",  # US Dollar
    "PHP",  # Philippine Peso
    "EUR",  # Euro
    "GBP",  # British Pound
    "CAD",  # Canadian Dollar
    "AUD",  # Australian Dollar
    "SGD",  # Singapore Dollar
    "JPY",  # Japanese Yen
    "CNY",  # Chinese Yuan
    "INR",  # Indian Rupee
    "AED",  # UAE Dirham
    "SAR",  # Saudi Riyal
    "QAR",  # Qatari Rial
    "HKD",  # Hong Kong Dollar
    "NZD",  # New Zealand Dollar
    "CHF",  # Swiss Franc
    "KRW",  # South Korean Won
    "THB",  # Thai Baht
    "MYR",  # Malaysian Ringgit
    "IDR",  # Indonesian Rupiah
    "VND",  # Vietnamese Dong
    "TWD",  # New Taiwan Dollar
    "BRL",  # Brazilian Real
    "MXN",  # Mexican Peso
    "ZAR",  # South African Rand
    "TRY",  # Turkish Lira
    "KWD",  # Kuwaiti Dinar
]

# Helpers to build choice labels
def _format_choice(code, name, symbol):
    if symbol and symbol != code:
        return f"{code} — {name} ({symbol})"
    return f"{code} — {name}"


# Build popular list
_popular_set = set(POPULAR_CODES)
_popular_choices = [
    (code, _format_choice(code, CURRENCY_NAMES[code], CURRENCY_SYMBOLS.get(code, "")))
    for code in POPULAR_CODES
    if code in CURRENCY_NAMES
]

# Build other list (alphabetical, excluding popular)
_other_choices = [
    (code, _format_choice(code, name, sym))
    for code, name, sym in sorted(ISO_CURRENCIES, key=lambda x: x[0])
    if code not in _popular_set
]

# Grouped choices for Django Select widgets
CURRENCY_CHOICES = [
    ("Popular Currencies", tuple(_popular_choices)),
    ("All Other Currencies (A–Z)", tuple(_other_choices)),
]

# Flat choices (all currencies alphabetically) for models or standard validation
FLAT_CURRENCY_CHOICES = [
    (code, _format_choice(code, name, sym))
    for code, name, sym in sorted(ISO_CURRENCIES, key=lambda x: x[0])
]

# All valid currency codes (for quick O(1) membership checking)
VALID_CURRENCY_CODES = {code for code, _, _ in ISO_CURRENCIES}


def get_currency_symbol(code, default=None):
    """Return currency symbol, or fallback to code or default."""
    if not code:
        return default or ""
    return CURRENCY_SYMBOLS.get(str(code).upper(), default or str(code).upper())

