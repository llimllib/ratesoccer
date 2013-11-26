import csv, codecs, time, operator, re
import glicko
import datetime
import copy

class Game(object):
    def __init__(self, hometeam, homescore, awayscore, awayteam, date, league, glicko_env):
        self.hometeam = hometeam
        self.homescore = homescore
        self.awayteam = awayteam
        self.awayscore = awayscore
        self.date = date
        self.league = league
        self.glicko_env = glicko_env
        self.rated = True
        self.score = "{}-{}".format(homescore, awayscore)

    def score_match(self, score_function):
        self.home_value, self.away_value = score_function(self.homescore, self.awayscore)

    def update(self, ranked_teams):
        if self.hometeam.name in ranked_teams and self.awayteam.name in ranked_teams:
            new_hometeam_glicko = self.glicko_env.rate(self.hometeam.glicko, [(self.home_value, self.awayteam.glicko)])
            self.awayteam.glicko = self.glicko_env.rate(self.awayteam.glicko, [(self.away_value, self.hometeam.glicko)])
            self.hometeam.glicko = new_hometeam_glicko
        else:
            self.rated = False

        # save the ratings after the game
        self.hometeam_rating = copy.copy(self.hometeam.glicko)
        self.awayteam_rating = copy.copy(self.awayteam.glicko)

        self.hometeam.historical.append(self)
        self.awayteam.historical.append(self)

        #update each team's record
        league = 0 if self.league else 1
        if self.homescore > self.awayscore:
            self.hometeam.record[league][0] += 1
            self.awayteam.record[league][2] += 1
        elif self.homescore < self.awayscore:
            self.hometeam.record[league][2] += 1
            self.awayteam.record[league][0] += 1
        else:
            self.hometeam.record[league][1] += 1
            self.awayteam.record[league][1] += 1

    def me(self, team):
        if team.name == self.hometeam.name:
            return (self.hometeam_rating, self.awayteam, self.awayteam_rating, self.home_value, self.date, self.score)
        else:
            return (self.awayteam_rating, self.hometeam, self.hometeam_rating, self.away_value, self.date, self.score)

class Team(object):
    def __init__(self, name, glicko_env):
        self.name = name
        self.sanitizedname = re.sub("\s", "", name.lower().encode("ascii", "ignore"))
        self.glicko = glicko_env.create_rating()
        self.glicko_env = glicko_env
        self.historical = []
        # league wins, draws, losses, other comp wins, draws, losses
        self.record = [[0,0,0], [0,0,0]]

    def ninetyfive(self):
        #return the score we're 95% certain the teams' rating is higher than
        return self.glicko.mu - 2*self.glicko.sigma

    def write_history(self, f):
        f.write(u"fullname,mu,sigma,opp,opp_rating,result,date,score\n")
        for game in self.historical:
            rating, opp, opp_rating, result, date, score = game.me(self)
            mu, sigma = rating.mu, rating.sigma
            opp = opp.name
            opp_rating = opp_rating.mu if game.rated else -1
            date = date.isoformat()
            f.write(u'{},{},{},{},{},{},{},{}\n'.format(
                self.name, mu, sigma, opp, opp_rating, result, date, score))

    def last5(self):
        """return the last 5 ratings the team has held, separated by |"""
        def rating(game):
            return "{:.2f}".format(game.me(self)[0].mu)
        return "|".join(rating(g) for g in self.historical[-5:])

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

def rate_teams_by_glicko(results, glicko_env, score_fn, ranked_teams):
    teams = {}

    for result in results:
        try:
            home, hscore, ascore, away, date, _, league = result
        except ValueError:
            print "failed to parse result {}".format(result)
            raise

        if home not in teams: teams[home] = Team(home, glicko_env)
        if away not in teams: teams[away] = Team(away, glicko_env)

        home, away = teams[home], teams[away]

        game = Game(home, hscore, ascore, away, date, league, glicko_env)
        game.score_match(score_fn)
        game.update(ranked_teams)

    return teams

def winner_takes_all(hscore, ascore):
    if hscore > ascore:
        home_value = 1
        away_value = 0
    elif hscore < ascore:
        home_value = 0
        away_value = 1
    else:
        home_value = away_value = .5

    return home_value, away_value

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
    valid_results = []
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

        # home and away scores
        try:
            row[1] = int(row[1])
            row[2] = int(row[2])
        except ValueError:
            continue

        row.append(league)
        valid_results.append(row)
    return valid_results

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

def output(teams, rated_teams):
    for team in teams:
        if team.name in rated_teams:
            f = codecs.open("ratingdata/{0}.csv".format(team.sanitizedname), 'w', 'utf8')
            team.write_history(f)

    allout = codecs.open("ratingdata/allteams.csv", 'w', 'utf8')
    allout.write("name,mu,sigma,sanitizedname,last5,leaguerecord,otherrecord\n")
    for team in teams:
        if team.name not in rated_teams: continue

        ## XXX TODO get last 5 results for a team
        last5 = team.last5()
        leaguerecord = "-".join(map(str, team.record[0]))
        otherrecord = "-".join(map(str, team.record[1]))
        allout.write(u"{},{},{},{},{},{},{}\n".format(team.name,
            team.glicko.mu, team.glicko.sigma, team.sanitizedname,
            last5, leaguerecord, otherrecord))
    allout.close()

if __name__=="__main__":
    bpl_results = get_results("data/bpl_13_14.csv")
    bundesliga_results = get_results("data/bundesliga_13_14.csv")
    ligue1_results = get_results("data/ligue1_13_14.csv")
    seriea_results = get_results("data/seriea_13_14.csv")
    laliga_results = get_results("data/laliga_13_14.csv")
    eredivisie_results = get_results("data/eredivisie_13_14.csv")
    spfl_results = get_results("data/spfl_13_14.csv")
    cl_results = get_results("data/cl_13_14.csv", league=False)
    europa_results = get_results("data/europa_13_14.csv", league=False)

    rated_teams = get_teams(bpl_results, bundesliga_results, ligue1_results, seriea_results, laliga_results, eredivisie_results, spfl_results)
    results = merge_by_date(bpl_results, cl_results, europa_results, bundesliga_results, ligue1_results, seriea_results, laliga_results, eredivisie_results, spfl_results)

    glicko_env = glicko.Glicko2(volatility=0.25)

    teams = rate_teams_by_glicko(results, glicko_env, winner_takes_all, rated_teams).values()

    teams_by_glicko = list(sorted(teams, key=lambda x: x.glicko.mu))
    teams_by_95pct = list(sorted(teams, key=lambda x: x.ninetyfive()))

    output(teams, rated_teams)
