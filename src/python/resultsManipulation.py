import gviz_api
import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--longLeg', default=False, action='store_true')



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


def getResultsStringByLegLength(df, long=True):
    jsData = []

    for c in df['team'].unique():
        rename_dict = {'rank': c, "name": f"name {c}"}
        jsData.append(df.loc[lambda d: (d['team'] == c) & (d['long'] == long)][['minutes', 'rank', 'name']].rename(columns=rename_dict))

    return pd.concat(jsData, sort=False)


def generateResultsStringForLegs(data, long):
    jsDataFrame = getResultsStringByLegLength(df, long)
    cols = [(i, "string") if "name" in i else (i, 'number') for i in list(jsDataFrame)]

    data_table = gviz_api.DataTable(cols)
    data_table.LoadData(list(jsDataFrame.itertuples(index=False, name=None)))

    return data_table.ToJSon().replace('NaN', 'null').replace('"nan"', 'null')


def getTeamRankDictionary(teamRank):
    teamRankArrayDict = []
    for i, row in teamRank.iterrows():
        t = row['team']
        teamRankArrayDict.append({"v": row['rank'], "f": f'{t}'})
    return teamRankArrayDict


if __name__== "__main__":
    args = parser.parse_args()
    df = getTeamResults()
    teamRank = getTeamRanksFromRace(df)
    print(generateResultsStringForLegs(df, args.longLeg))
