from __future__ import division
import sys
sys.path.insert(0, "/Users/bill/code/ratesoccer/")
from math import e
import os
from rate import *

relpath = lambda p: os.path.join(os.path.abspath(os.path.dirname(__file__)), p)

def get_results_season(season="12_13"):
    bpl_results = get_results(relpath("../data/bpl_{}.csv".format(season)))
    bundesliga_results = get_results(relpath("../data/bundesliga_{}.csv".format(season)))
    ligue1_results = get_results(relpath("../data/ligue1_{}.csv".format(season)))
    seriea_results = get_results(relpath("../data/seriea_{}.csv".format(season)))
    laliga_results = get_results(relpath("../data/laliga_{}.csv".format(season)))
    cl_results = get_results(relpath("../data/cl_{}.csv".format(season)), league=False)
    europa_results = get_results(relpath("../data/europa_{}.csv".format(season)), league=False)
    major_teams_set = get_teams(bpl_results, bundesliga_results, ligue1_results, seriea_results, laliga_results)
    results = merge_by_date(bpl_results, cl_results, europa_results, bundesliga_results, ligue1_results, seriea_results, laliga_results)
    return results, major_teams_set

def score_results(teams):
    seen = set()
    #correctly predicted, incorrectly predicted
    results = [0,0]
    for team in teams:
        for game in team.historical:
            rating, opp, opp_rating, result, date = game

            # skip games we've already seen
            key = "".join(sorted([team.name, opp.name])) + date.isoformat()
            if key in seen: continue
            else:           seen.add(key)

            if rating.mu > opp_rating.mu and result > .5:  results[0] += 1
            if rating.mu < opp_rating.mu and result > .5:  results[1] += 1
            if rating.mu > opp_rating.mu and result <= .5: results[1] += 1
            if rating.mu < opp_rating.mu and result <= .5: results[0] += 1

    return results


# the logistic function is WAY worse than winner-take-all. No idea why.
#
#           10_11: 1149/1875 = 61.3% success rate
#           11_12: 1230/1879 = 65.5% success rate
#           12_13: 1241/1870 = 66.4% success rate
# logistic: 10_11: 1021/1875 = 54.5% success rate
# logistic: 11_12: 1008/1883 = 53.5% success rate
# logistic: 12_13: 1046/1876 = 55.8% success rate
def logistic_results(hscore, ascore):
    if hscore > ascore:
        home_value = 1/(1+e**(ascore-hscore))
        away_value = 1 - home_value
    elif hscore < ascore:
        home_value = 1/(1+e**(hscore-ascore))
        away_value = 1 - home_value
    else:
        home_value = away_value = .5
    return home_value, away_value

# I'm not convinced that different volatilities result in better prediction, in any
# way that rises above the noise:
#
# 0.02: 10_11: 1147/1875 = 61.2% success rate
# 0.02: 11_12: 1231/1879 = 65.5% success rate
# 0.02: 12_13: 1241/1870 = 66.4% success rate
# 0.06: 10_11: 1149/1875 = 61.3% success rate
# 0.06: 11_12: 1230/1879 = 65.5% success rate
# 0.06: 12_13: 1241/1870 = 66.4% success rate
# 0.1: 10_11: 1164/1875 = 62.1% success rate
# 0.1: 11_12: 1239/1879 = 65.9% success rate
# 0.1: 12_13: 1250/1870 = 66.8% success rate
# 0.14: 10_11: 1186/1875 = 63.3% success rate
# 0.14: 11_12: 1246/1879 = 66.3% success rate
# 0.14: 12_13: 1263/1870 = 67.5% success rate
# 0.18: 10_11: 1197/1875 = 63.8% success rate
# 0.18: 11_12: 1265/1879 = 67.3% success rate
# 0.18: 12_13: 1263/1870 = 67.5% success rate
# 0.22: 10_11: 1218/1875 = 65.0% success rate
# 0.22: 11_12: 1278/1879 = 68.0% success rate
# 0.22: 12_13: 1279/1870 = 68.4% success rate
# 0.26: 10_11: 1227/1875 = 65.4% success rate
# 0.26: 11_12: 1292/1879 = 68.8% success rate
# 0.26: 12_13: 1286/1870 = 68.8% success rate
# 0.3: 10_11: 1236/1875 = 65.9% success rate
# 0.3: 11_12: 1302/1879 = 69.3% success rate
# 0.3: 12_13: 1289/1870 = 68.9% success rate
# 0.34: 10_11: 1246/1875 = 66.5% success rate
# 0.34: 11_12: 1308/1879 = 69.6% success rate
# 0.34: 12_13: 1296/1870 = 69.3% success rate
# 0.38: 10_11: 1257/1875 = 67.0% success rate
# 0.38: 11_12: 1314/1879 = 69.9% success rate
# 0.38: 12_13: 1294/1870 = 69.2% success rate
# 0.42: 10_11: 1269/1875 = 67.7% success rate
# 0.42: 11_12: 1315/1879 = 70.0% success rate
# 0.42: 12_13: 1302/1870 = 69.6% success rate
# 0.46: 10_11: 1276/1875 = 68.1% success rate
# 0.46: 11_12: 1309/1879 = 69.7% success rate
# 0.46: 12_13: 1309/1870 = 70.0% success rate
# 0.5: 10_11: 1290/1875 = 68.8% success rate
# 0.5: 11_12: 1315/1879 = 70.0% success rate
# 0.5: 12_13: 1311/1870 = 70.1% success rate
# 0.54: 10_11: 1300/1875 = 69.3% success rate
# 0.54: 11_12: 1315/1879 = 70.0% success rate
# 0.54: 12_13: 1326/1870 = 70.9% success rate
# 0.58: 10_11: 1301/1875 = 69.4% success rate
# 0.58: 11_12: 1325/1879 = 70.5% success rate
# 0.58: 12_13: 1338/1870 = 71.6% success rate
#0.6: 10_11: 1314/1875 = 70.1% success rate
#0.6: 11_12: 1331/1879 = 70.8% success rate
#0.6: 12_13: 1340/1870 = 71.7% success rate
#0.64: 10_11: 1320/1875 = 70.4% success rate
#0.64: 11_12: 1337/1879 = 71.2% success rate
#0.64: 12_13: 1350/1870 = 72.2% success rate
#0.68: 10_11: 1330/1875 = 70.9% success rate
#0.68: 11_12: 1343/1879 = 71.5% success rate
#0.68: 12_13: 1360/1870 = 72.7% success rate
#0.72: 10_11: 1337/1875 = 71.3% success rate
#0.72: 11_12: 1351/1879 = 71.9% success rate
#0.72: 12_13: 1366/1870 = 73.0% success rate
#0.76: 11_12: 1362/1879 = 72.5% success rate
#0.76: 12_13: 1373/1870 = 73.4% success rate
#0.8: 11_12: 1366/1879 = 72.7% success rate
#0.8: 12_13: 1384/1870 = 74.0% success rate
#0.84: 11_12: 1373/1879 = 73.1% success rate
#0.84: 12_13: 1394/1870 = 74.5% success rate
#0.88: 11_12: 1380/1879 = 73.4% success rate
#0.88: 12_13: 1402/1870 = 75.0% success rate
#0.88: 11_12: 1380/1879 = 73.4% success rate
#0.88: 12_13: 1402/1870 = 75.0% success rate
#unable to rate. Zero Division
#0.92: 11_12: 1402/1870 = 75.0% success rate
#0.92: 12_13: 1415/1870 = 75.7% success rate
#unable to rate. Zero Division
#0.96: 11_12: 1415/1870 = 75.7% success rate
#0.96: 12_13: 1416/1870 = 75.7% success rate

if __name__=="__main__":
    #for i in range(10, 13):
    #    season = "{}_{}".format(i, i+1)
    #    results, league_teams = get_results_season(season)
    #    glicko_env = glicko.Glicko2()
    #    teams = rate_teams_by_glicko(results, glicko_env, winner_takes_all, league_teams).values()
    #    score = score_results(teams)
    #    print "{}: {}/{} = {:.1f}% success rate".format(season, score[0], sum(score), (score[0]/sum(score))*100)
    for volatility in [x/100 for x in range(100, 120, 4)]:
        for i in range(11, 13):
            season = "{}_{}".format(i, i+1)
            results, league_teams = get_results_season(season)
            glicko_env = glicko.Glicko2(volatility=volatility)
            try:
                teams = rate_teams_by_glicko(results, glicko_env, winner_takes_all, league_teams).values()
            except ZeroDivisionError:
                print "unable to rate. Zero Division"
                continue
            except OverflowError:
                print "unable to rate. Overflow"
                continue
            teams_by_glicko = list(sorted(teams, key=lambda x: x.glicko.mu))
            score = score_results(teams)
            print "{}: {}: {}/{} = {:.1f}% success rate".format(volatility, season, score[0], sum(score), (score[0]/sum(score))*100)
