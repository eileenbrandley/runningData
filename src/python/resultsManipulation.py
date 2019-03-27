import gviz_api
import pandas as pd
import numpy as np


def get_minutes(t):
    """
    Function turns string time to number of minutes
    :param t: String in time format mm:ss
    :return: Time as number of seconds
    """
    time = [int(i) for i in t.split(':')]
    return time[0] + time[1] / 60


def getAllData():
    dataLong = pd.read_csv("/Users/eileentoomer/Downloads/seaaLongLegs2019.csv")
    dataShort = pd.read_csv("/Users/eileentoomer/Downloads/seaaShortLegs2019.csv")

    return (
        pd.concat([dataLong.assign(long=True), dataShort.assign(long=False)])
            .assign(minutes=lambda d: d['time'].apply(get_minutes))
            .assign(team=lambda d: d['team'].pipe(stripSpeechMarksFromClubs))
            .reset_index(drop=True)
    )


def getTeamRanksFromRace(data):
    """
    Returns the ranking positions of all teams that finished (i.e. had 12 runners)
    :param data: Dataframe containing team/seconds
    :return:
    """
    return (
        data.groupby('team')['minutes']
            .agg([np.sum, 'count'])
            .loc[lambda d: d['count'] == 12]
            .rank(ascending=False)
            .rename(columns={'sum': 'rank'})[['rank']]
            .reset_index()
    )


def teamRankToDict(teamRanks):
    return pd.Series(teamRanks['rank'].values, index=teamRanks['team']).to_dict()


def getRunnerLegRanking(data):
    return data.groupby(['long'])['minutes'].rank(ascending=True).rename('legRank')

def stripSpeechMarksFromClubs(clubs):
    return clubs.str.replace('"', '')


def getTeamResults():
    data = getAllData()
    teams = getTeamRanksFromRace(data)
    runners = getRunnerLegRanking(data)
    return data.join(runners).merge(teams, on='team')