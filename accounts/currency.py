import requests
import re

"""
Functions to do currency conversion.
In a real project (non-demo) this information would be cached in some way (DB, redis) so that we don't have to call a remote API each time.
"""

def currency_rate(source,dest):
    """
    Returns the number you should multiply with in order to change from "source" currency to "dest" currency.
    E.g. convert 1 EUR (source) to USD (dest) = 0.89
    Does real-time HTTP call.
    """
    assert re.match("[A-Z]{3}",source)
    assert re.match("[A-Z]{3}",dest)
    # We need to set source=1 and ask only about the dest. currency
    # e.g. "tell me the destination currency, in my terms"
    params = {'base': source, 'symbols': dest}
    try:
        r = requests.get('http://api.fixer.io/latest', params=params)
        r = r.json()
    except requests.exceptions.ConnectionError:
        raise Exception("Connection to get currency rates failed")

    rate = r['rates'][dest]
    #print("Returning rate: 1 %s == %f %s"%(source,rate,dest))
    return rate
