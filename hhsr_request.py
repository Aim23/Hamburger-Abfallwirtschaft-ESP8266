import json
from bs4 import BeautifulSoup
import requests
import locale
import datetime as d 

locale.setlocale(locale.LC_TIME, "de_DE") # "de_DE.UTF-8" on raspbian 

try:
    with open('settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
except OSError:
    print('Datei (settings) nicht gefunden')
    raise

url = settings['url']
settings.pop("url")
print(settings)

r = requests.post(url, params=settings)

page = r.text
soup = BeautifulSoup(page, 'html.parser')

if soup.find_all(class_='adresse'):
    raise TypeError("Adresse/Hausnummer nicht gefunden.")

div_abfuhrkalender = soup.find(class_='box', id='abfuhrkalender')

tds = div_abfuhrkalender.find_all('td')
table_cols = []
for td in tds:
    table_cols.append(td.string)

compose_list = [table_cols[x:x+3] for x in range (0, len(table_cols),3)]

now = d.datetime.now()
hhsr = {}

for values in compose_list:
    datum, tonne, frequency = values
    datum = d.datetime.strptime(str(datum), '%a, %d.%m.%Y')
    datum = d.datetime(datum.year, datum.month, datum.day, 16, 0, 0)
    difference = (datum - now).days
    hhsr.update({ tonne : { 'Datum': str(datum), 'Fällig': difference, 'Häufigkeit': frequency } })

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(hhsr, f, ensure_ascii=False, indent=4)