import sqlite3
import urllib.error, urllib.request, urllib.parse
from bs4 import BeautifulSoup
import ssl
import requests

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://www.skysports.com/premier-league-results'

html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')

tags = soup.find_all()
results = dict()

for tag in tags:
    if tag.has_attr('class'):
        if tag['class'][0] == 'fixres__header2':
            dtime = tag.text
        if tag['class'][0] == 'fixres__item':
            results[dtime] = results.get(dtime, 0) + 1

print(results)