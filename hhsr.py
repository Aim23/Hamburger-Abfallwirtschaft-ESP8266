import json
import requests
import locale
import datetime as d
import time
from bs4 import BeautifulSoup
import paho.mqtt.client as mqtt

locale.setlocale(locale.LC_ALL, '') # "de_DE.UTF-8" on raspbian 

class HHSR: 
    
    def __init__(self, settings):
        self.setting = settings
        
        try:
            with open(self.setting, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except OSError:
            print(f'Datei {self.setting} nicht gefunden')
            raise
        
        self.url = self.settings['url']
        self.settings.pop("url")
        
        self.strasse = self.settings['strasse']
        self.hausnummer = self.settings['hausnummer']
        self.broker = self.settings['broker_address']

    
    def update(self):
        self.mqtt = mqtt.Client()
        self.r = requests.post(self.url, params=self.settings)
        self.page = self.r.text
        self.soup = BeautifulSoup(self.page, 'html.parser')
        
        if self.soup.find_all(class_='adresse'):
            raise TypeError("Adresse/Hausnummer nicht gefunden.")
        
        self.div_abfuhrkalender = self.soup.find(class_='box', id='abfuhrkalender')
        
        self.tds = self.div_abfuhrkalender.find_all('td')
        self.table_cols = []
        for self.td in self.tds:
            self.table_cols.append(self.td.string)
        
        self.compose_list = [self.table_cols[self.x:self.x+3] for self.x in range (0, len(self.table_cols),3)]
        
        self.now = d.datetime.now()
        
        self.hhsr = {}
        
        for self.values in self.compose_list:
            self.datum, self.tonne, self.frequency = self.values
            self.datum = d.datetime.strptime(str(self.datum), '%a, %d.%m.%Y')
            self.datum = d.datetime(self.datum.year, self.datum.month, self.datum.day, 16, 0, 0)
            self.difference = (self.datum - self.now).days
            self.hhsr.update({self.tonne : {'Datum': str(self.datum), 'Fällig': self.difference, 'Häufigkeit': self.frequency}})
        
        with open('data.json', 'w', encoding='utf-8') as self.f: 
            json.dump(self.hhsr, self.f, ensure_ascii=False, indent=4)
        print(json.dump)
    
    def on_connect(self, client, userdata, flags, rc):
        pass 
    
    def MQTTupdate(self):
        pass
    
    def request(self): 
        pass

x = HHSR('settings.json')
x.update()