import sqlite3

def LeagueTable():

    conn = sqlite3.connect('PLResults.sqlite')
    cur = conn.cursor()

    table = [['Pos','Team', 'Pl ', 'Pts']]

    cur.execute('SELECT Home.Team FROM Home')
    teams = []
    for row in cur:
        teams.append(row[0])

    for team in teams:
        cur.execute('''SELECT
(
	SELECT Home.Team
	FROM Home
	WHERE Home.Team = ?
) AS Team,
(
	SELECT count(Results.Result)
	FROM Home JOIN Away JOIN Results
	ON Results.Home_id = Home.id AND Results.Away_id = Away.id
	WHERE Home.Team = ? or Away.Team = ?
) AS Played,
(
	SELECT
	(3 * count(CASE WHEN (Home.Team = ? AND Results.HGoals > Results.AGoals) OR (Away.Team = ? AND Results.AGoals > Results.HGoals) THEN 1 ELSE NULL END)) +
	count(CASE WHEN (Home.Team = ? AND Results.HGoals = Results.AGoals) OR (Away.Team = ? AND Results.AGoals = Results.HGoals) THEN 1 ELSE NULL END)
	FROM Home JOIN Away JOIN Results
	ON Results.Home_id = Home.id AND Results.Away_id = Away.id
) AS Points
                    ''', (team, team, team, team, team, team, team))
        
        for row in cur:
            table += [[row[0], str(row[1]), str(row[2]).rjust(3)]]

    table = sorted(table, key=lambda x: x[2], reverse=True)
    pos = 1
    for i in range(len(table)):
        if i == 0: continue
        table[i].insert(0, str(pos))
        pos += 1
    
    conn.close()
    return table