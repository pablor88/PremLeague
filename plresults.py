import sqlite3
import urllib.error, urllib.request, urllib.parse
from bs4 import BeautifulSoup
import ssl
import requests

def Results_Update():

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    conn = sqlite3.connect('PLResults.sqlite')
    cur = conn.cursor()

    url = 'https://www.flashscore.co.uk/football/england/premier-league/results/'
    url = 'https://www.skysports.com/premier-league-results'

    cur.execute(''' CREATE TABLE IF NOT EXISTS Home 
            (id INTEGER NOT NULL PRIMARY KEY, Team TEXT UNIQUE)''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS Away 
            (id INTEGER NOT NULL PRIMARY KEY, Team TEXT UNIQUE)''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS Results 
            (Result TEXT, Home_id INTEGER, Away_id INTEGER, HGoals INTEGER, AGoals INTEGER)''')

    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    tags = soup.find_all('span')
    scores = list()

    for tag in tags:
        if len(scores) == 4:
            hteam = scores[0]
            ateam = scores[3]
            HGoals = scores[1]
            AGoals = scores[2]
            result = str(scores[1]+'-'+scores[2])

            cur.execute('INSERT OR IGNORE INTO Home (Team) Values (?)', (hteam,))
            cur.execute('INSERT OR IGNORE INTO Away (Team) Values (?)', (ateam,))
            for row in cur.execute('SELECT id, team FROM Home WHERE team = ?', (hteam, )):
                hteam_id = row[0]

            for row in cur.execute('SELECT id, team FROM Away WHERE team = ?', (ateam, )):
                ateam_id = row[0]

            cur.execute('''SELECT Home.team, Results.Result, Away.team FROM
                        Home JOIN Results JOIN Away ON
                        Results.Home_id = Home.id and Results.Away_id = Away.id
                        WHERE Home.Team = ? AND Away.Team = ?''', (hteam, ateam))
            
            if cur.fetchone() is None:
                cur.execute('INSERT OR IGNORE INTO Results (Result, Home_id, Away_id, HGoals, AGoals) Values (? , ? , ? , ? , ?)', 
                            (result, hteam_id, ateam_id, HGoals, AGoals))  

            scores = list()

        if tag.has_attr('class'):
            if len(tag['class']) > 1:
                if tag['class'][1] == 'matches__participant':
                    scores.append(tag.text.strip())
            elif tag['class'][0] == 'matches__teamscores-side':
                scores.append(tag.text.strip())

    conn.commit()

    cur.execute('''SELECT Home.team, Results.Result, Away.team FROM
                Home JOIN Results JOIN Away ON
                Results.Home_id = Home.id and Results.Away_id = Away.id''')
    
    conn.close()