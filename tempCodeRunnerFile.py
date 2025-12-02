from nba_api.stats.static import teams
from nba_api.stats.endpoints import teaminfocommon, commonteamroster, scheduleleaguev2, playergamelog
from tabulate import tabulate
from dotenv import load_dotenv
import pandas as pd
import psycopg
import os

# get_teams returns a list of 30 dictionaries, each an NBA team.
nba_teams = teams.get_teams()
# print(json.dumps(nba_teams, indent=4))

load_dotenv()
lal_team_id = 1610612747
dsn = os.getenv("DATABASE_URL")
roster = commonteamroster.CommonTeamRoster(team_id=1610612747)
roster_df = roster.get_data_frames()[0]
print(tabulate(roster_df, headers='keys', tablefmt='psql'))