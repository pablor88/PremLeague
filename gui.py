import PySimpleGUI as sg
import plfixtures
import pltable
import sqlite3
import plresults
import time

conn = sqlite3.connect('PLResults.sqlite')
cur = conn.cursor()

fixtures = plfixtures.Fixtures()

updated_fixtures = []
results = []

table = pltable.LeagueTable()
toprow = table[0:1][0]
rows = table[1:]
tbl = sg.Table(values=rows, headings=toprow, key='__TABLE__', auto_size_columns=True,
               display_row_numbers=False, justification='center',cols_justification=('r', 'l', 'c', 'c'), visible=False)

menu_list = ['Fixtures', 'Results']
#lst = sg.Listbox(updated_fixtures, size=(500, 20), enable_events=True, highlight_background_color='blue')

lst = sg.Listbox(menu_list, size=(500, 20), enable_events=True, highlight_background_color='blue')

layout = [  [lst],
            [tbl],
            [sg.Button('Ok'), sg.Button('Cancel'), sg.Button('Back', key='__BACK__', visible=False)], 
            [sg.Button('League Table')]]

# Create the Window
window = sg.Window('Window Title', layout, size=(1000, 800))
# Event Loop to process "events" and get the "values" of the inputs
while True:
    
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
    if event == 'Ok' or event == 0:
        result = ''

        if values[0][0] == 'Results' or values[0][0] == 'Fixtures':
            screen = values[0][0]
            lst.update(values=['Team', 'All'])
            window.refresh()
            continue
            
        if values[0][0] == 'Team' and screen == 'Results':
            cur.execute('SELECT Team from Home ORDER BY Home.Team')
            teams = []
            for row in cur:
                teams.append(row[0])
            lst.update(values=teams)
            window.find_element('__BACK__').update(visible=True)
            window.refresh()
            continue

        if values[0][0] == 'All' and screen == 'Results':
            cur.execute('''SELECT Home.team, Results.Result, Away.team FROM
                Home JOIN Results JOIN Away ON
                Results.Home_id = Home.id and Results.Away_id = Away.id''')
            results = []
            for row in cur:
                results.append(row[0]+' '+row[1]+' '+row[2])
            lst.update(values=results)
            window.find_element('__BACK__').update(visible=True)
            window.refresh()
            continue

        if screen == 'Fixtures':
            if values[0][0] == 'All':
                new_fixtures = fixtures.all()
                result = 'h2h'
                screen = ''
                lst.update(values=new_fixtures)
                window.find_element('__BACK__').update(visible=True)
                window.refresh()
                continue
            elif values[0][0] == 'Team':
                result = 'Team'
                cur.execute('SELECT Team from Home ORDER BY Home.Team')
                teams = []
                for row in cur:
                    teams.append(row[0])
                lst.update(values=teams)
                window.find_element('__BACK__').update(visible=True)
                window.refresh()
                continue
            elif values[0][0] == 'Fixtures' or values[0][0] == 'Results': continue
            elif values[0][0] in teams:
                new_fixtures = fixtures.team(values[0][0])

                lst.update(values=new_fixtures)
                window.find_element('__BACK__').update(visible=True)
                window.refresh()
                continue

        if ' v ' in values[0][0]:
            fixture = values[0][0].split(' v ')
            hteam = fixture[0].strip()
            ateam = fixture[1].strip()
            result = 'h2h'
        else:
            hteam = values[0][0]
            result = 'team'
            

        if ' v ' in values[0][0]:
            cur.execute('''SELECT Home.Team, Results.Result, Away.Team FROM Home JOIN Results JOIN Away
                        ON Results.Home_id = Home.id AND Results.Away_id = Away.id
                        WHERE ? = Home.Team or ? = Away.Team LIMIT 5''', (hteam, hteam))
    
            for row in cur:
                results.append(row[0]+' '+row[1]+' '+row[2])
            results.append('\n')
            cur.execute('''SELECT Home.Team, Results.Result, Away.Team FROM Home JOIN Results JOIN Away
                        ON Results.Home_id = Home.id AND Results.Away_id = Away.id
                        WHERE ? = Away.Team or ? = Away.Team LIMIT 5''', (ateam, ateam))

            for row in cur:
                results.append(row[0]+' '+row[1]+' '+row[2])
        
        else:
            cur.execute('''SELECT Home.Team, Results.Result, Away.Team FROM Home JOIN Results JOIN Away
                        ON Results.Home_id = Home.id AND Results.Away_id = Away.id
                        WHERE ? = Home.Team or ? = Away.Team LIMIT 10''', (hteam, hteam))
            
            for row in cur:
                results.append(row[0]+' '+row[1]+' '+row[2])

        lst.update(values=results)

        window.find_element('__BACK__').update(visible=True)
        window.refresh() 
    
    if event == '__BACK__':
        
        if result == 'h2h':
            lst.update(values=new_fixtures)
            window.find_element('__BACK__').update(visible=True)
        elif result == 'team':
            window.find_element('__BACK__').update(visible=True)
            lst.update(values=teams)
        else:
            window.find_element('__BACK__').update(visible=False)
            lst.update(values=menu_list)
        results = []
        result = ''
        window.refresh()

    if event == 'League Table':
        window.find_element('__TABLE__').update(visible=True)
        window.refresh()

conn.close()
window.close()