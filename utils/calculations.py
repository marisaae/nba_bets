def calc_ppg(player_stats_df):
    points = player_stats_df["pts"].sum()
    games = player_stats_df.shape[0]
    if games == 0:
        return 0
    return round(points / games, 1)


def calc_apg(player_stats_df):
    assists = player_stats_df["ast"].sum()
    games = player_stats_df.shape[0]
    if games == 0:
        return 0
    return round(assists / games, 1)


def calc_fgpct(player_stats_df):
    fgm = player_stats_df["fgm"].sum()
    fga = player_stats_df["fga"].sum()
    if fga == 0:
        return 0
    return round((fgm / fga) * 100, 1)


def calc_3ppct(player_stats_df):
    three_made = player_stats_df["three_pts_made"].sum()
    three_att = player_stats_df["three_pts_att"].sum()
    if three_att == 0:
        return 0
    return round((three_made / three_att) * 100, 1)


def calc_mid(player_stats_df):
    game_count = player_stats_df.shape[0]
    mid = game_count // 2

    return game_count, mid