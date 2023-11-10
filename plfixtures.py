import sqlite3
import urllib.error, urllib.request, urllib.parse
from bs4 import BeautifulSoup
import ssl
import requests

class Fixtures():

    def all(self):

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        url = 'https://www.skysports.com/premier-league-fixtures'

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')

        tags = soup.find_all('span')
        fixtures = list()

        for tag in tags:
            if len(fixtures) == 20:
                new_fixtures = []
                i = 0
                while i < 20:
                    new_fixtures.append(fixtures[i]+' v '+fixtures[i + 1])
                    i += 2
                return new_fixtures

            if tag.has_attr('class'):
                if len(tag['class']) > 1:
                    if tag['class'][1] == 'matches__participant':
                        fixtures.append(tag.text.strip())
    
    def team(self, team):

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        conn = sqlite3.connect('PLResults.sqlite')
        cur = conn.cursor()

        cur.execute('DROP TABLE IF EXISTS FixturesHome')
        cur.execute('DROP TABLE IF EXISTS FixturesAway')
        cur.execute('DROP TABLE IF EXISTS FixturesPair')
        
        cur.execute(''' CREATE TABLE IF NOT EXISTS FixturesHome 
            (id INTEGER NOT NULL PRIMARY KEY, Team TEXT UNIQUE)''')

        cur.execute(''' CREATE TABLE IF NOT EXISTS FixturesAway 
            (id INTEGER NOT NULL PRIMARY KEY, Team TEXT UNIQUE)''')

        cur.execute(''' CREATE TABLE IF NOT EXISTS FixturesPair 
            (Home_id INTEGER, Away_id INTEGER, Error INTEGER)''')

        url = 'https://www.skysports.com/premier-league-fixtures'

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')

        tags = soup.find_all('span')
        fixtures = list()

        for tag in tags:
            if len(fixtures) == 2:
                hteam = fixtures[0]
                ateam = fixtures[1]

                cur.execute('INSERT OR IGNORE INTO FixturesHome (Team) Values (?)', (hteam,))
                cur.execute('INSERT OR IGNORE INTO FixturesAway (Team) Values (?)', (ateam,))
                for row in cur.execute('SELECT id, team FROM FixturesHome WHERE team = ?', (hteam, )):
                    hteam_id = row[0]

                for row in cur.execute('SELECT id, team FROM FixturesAway WHERE team = ?', (ateam, )):
                    ateam_id = row[0]

                cur.execute('INSERT OR IGNORE INTO FixturesPair (Home_id, Away_id, Error) Values (? , ?, 1)', 
                        (hteam_id, ateam_id))
                
                fixtures = list()

            if tag.has_attr('class'):
                if len(tag['class']) > 1:
                    if tag['class'][1] == 'matches__participant':
                        fixtures.append(tag.text.strip())

        cur.execute('''SELECT FixturesHome.Team, FixturesAway.Team FROM FixturesHome JOIN FixturesAway JOIN FixturesPair
                    ON FixturesPair.Home_id = FixturesHome.id and FixturesPair.Away_id = FixturesAway.id
                    WHERE FixturesHome.Team = ? OR FixturesAway.Team = ?''', (team, team))
        
        for row in cur:
            fixtures.append(row[0]+' v '+row[1])
        
        conn.close()

        return fixtures