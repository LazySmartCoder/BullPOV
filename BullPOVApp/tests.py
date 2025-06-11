import pycountry

countryCode = {country.name: country.alpha_2 for country in pycountry.countries}

print(countryCode)
