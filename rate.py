import requests, cPickle, csv, codecs, time, operator, re
from bs4 import BeautifulSoup
import glicko
import datetime

# Set the glicko parameters environment
#TODO: find proper params?
GlickoEnv = glicko.Glicko2()

class Team(object):
    def __init__(self, name):
        self.name = name
        self.sanitizedname = re.sub("\s", "", name.lower().encode("ascii", "ignore"))
        self.glicko = GlickoEnv.create_rating()
        self.historical = []
        # leauge wins, draws, losses, other comp wins, draws, losses
        self.record = [[0,0,0], [0,0,0]]

    def update(self, opponent, result, date=None, use_glicko=None):
        # We need to upate against the glicko of our opponent *before* the match,
        # so the use_glicko parameter allows us to pass it in.
        opponent_glicko = use_glicko if use_glicko else opponent.glicko

        self.glicko = GlickoEnv.rate(self.glicko, [(result, opponent_glicko)])
        self.historical.append((self.glicko, opponent, result, date))

    def ninetyfive(self):
        #return the score we're 95% certain the teams' rating is higher than
        return self.glicko.mu - 2*self.glicko.sigma

    def write_history(self, f):
        f.write(u"mu,sigma,opp,result,date\n")
        for h in self.historical:
            mu, sigma = h[0].mu, h[0].sigma
            opp = h[1].name if h[1] else ""
            result = h[2] if h[2] is not None else ""
            date = h[3].isoformat() if h[3] else ""
            f.write(u'{0},{1},{2},{3},{4}\n'.format(mu, sigma, opp, result, date))

    def update_record(self, ourscore, oppscore, league):
        league = 0 if league else 1
        if ourscore > oppscore:
            self.record[league][0] += 1
        elif ourscore < oppscore:
            self.record[league][2] += 1
        else:
            self.record[league][1] += 1

    def __unicode__(self):
        return u"%s %.2f %.2f" % (self.name, self.glicko.mu, self.glicko.sigma)

    def __str__(self):
        return (u"%s %.2f %.2f" % (self.name, self.glicko.mu, self.glicko.sigma)).encode("utf8")

    def __repr__(self): return self.__str__()

def trace_team_glicko(team, home, hscore, ascore, away):
    t = None
    if team in home.name: t, u = home, away
    if team in away.name: t, u = away, home
    if not t: return
    print "%s %s - %s %s" % (home, hscore, ascore, away)

def rate_teams_by_glicko(results, these_teams_only):
    teams = {}

    for home, hscore, ascore, away, date, _, league in results:
        if home not in teams and home in these_teams_only: teams[home] = Team(home)
        if away not in teams and away in these_teams_only: teams[away] = Team(away)

        # update the team records even for games we're not rating
        if home in these_teams_only:
            teams[home].update_record(hscore, ascore, league)
        if away in these_teams_only:
            teams[away].update_record(ascore, hscore, league)

        if home not in these_teams_only or away not in these_teams_only: continue

        home = teams[home]
        away = teams[away]

        if hscore > ascore:
            home_value = 1
            away_value = 0
        elif hscore < ascore:
            home_value = 0
            away_value = 1
        else:
            home_value = away_value = .5

        #TODO parse the dates
        old_home_glicko = home.glicko
        home.update(away, home_value, date)
        away.update(home, away_value, date, use_glicko=old_home_glicko)

    return teams

# ripped from the python docs: http://docs.python.org/2/library/csv.html#csv-examples
# plus an additional strip()
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data))
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8').strip() for cell in row]

def utf_8_encoder(unicode_csv_data):
    try:
        for line in unicode_csv_data:
            yield line.encode('utf-8')
    except UnicodeDecodeError:
        print type(line), line
        raise

def normalize_name(name):
    if name == "Spurs": return "Tottenham Hotspur"
    return name

def get_results(filename, league=True):
    data = codecs.open(filename, encoding='utf8').readlines()[1:]

    # The CSV module doesn't handle quoted entries if there's a space after
    # the comma. Example:
    # >>> list(csv.reader(['a, "b,c"']))
    # [['a', ' "b', 'c"']]
    # >>> list(csv.reader(['a,"b,c"']))
    # [['a', 'b,c']]
    # so replace all , " with ,"
    #
    # TODO: modify the data sources :(
    data = map(lambda line: line.replace(', "', ',"'), data)

    results = list(unicode_csv_reader(data))
    for row in results:
        try:
            row[4] = datetime.datetime.strptime(row[4], "%A %d %B %Y")
        except ValueError:
            try:
                row[4] = datetime.datetime.strptime(row[4], "%A, %B %d, %Y")
            except ValueError:
                print row
                raise
        row[0] = normalize_name(row[0])
        row[3] = normalize_name(row[3])

        row.append(league)
    return results

def merge_by_date(*lists):
    return sorted(reduce(operator.add, lists), key=operator.itemgetter(4))

def get_teams(*lists):
    teams = set()
    for l in lists:
        for game in l:
            home = game[0]
            away = game[3]
            teams.add(home)
            teams.add(away)
    return teams

def output(teams):
    for team in teams:
        team.write_history(open("ratingdata/{0}.csv".format(team.sanitizedname), 'w'))

    allout = open("ratingdata/allteams.csv", 'w')
    allout.write("name,mu,sigma,sanitizedname,change,last5,leaguerecord,otherrecord\n")
    for team in teams:
        if not len(team.historical):    change = "0"
        elif len(team.historical) == 1: change = "{:}".format(team.historical[0][0].mu-1500)
        else:                           change = "{:}".format(team.historical[-1][0].mu-team.historical[-2][0].mu)
        last5 = "|".join([str(h[0].mu) for h in team.historical[-5:]])
        leaguerecord = "-".join(map(str, team.record[0]))
        otherrecord = "-".join(map(str, team.record[1]))
        allout.write("{},{},{},{},{},{},{},{}\n".format(team.name,
            team.glicko.mu, team.glicko.sigma, team.sanitizedname,
            change, last5, leaguerecord, otherrecord))
    allout.close()

if __name__=="__main__":
    bpl_results = get_results("data/bpl_13_14.csv")
    bundesliga_results = get_results("data/bundesliga_13_14.csv")
    ligue1_results = get_results("data/ligue1_13_14.csv")
    seriea_results = get_results("data/seriea_13_14.csv")
    laliga_results = get_results("data/laliga_13_14.csv")
    cl_results = get_results("data/cl_13_14.csv", league=False)
    europa_results = get_results("data/europa_13_14.csv", league=False)

    major_teams_set = get_teams(bpl_results, bundesliga_results, ligue1_results, seriea_results, laliga_results)
    results = merge_by_date(bpl_results, cl_results, europa_results, bundesliga_results, ligue1_results, seriea_results, laliga_results)
    teams = rate_teams_by_glicko(results, major_teams_set).values()

    teams_by_glicko = list(sorted(teams, key=lambda x: x.glicko.mu))
    teams_by_95pct = list(sorted(teams, key=lambda x: x.ninetyfive()))

    output(teams)
