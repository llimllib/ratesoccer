import requests, cPickle, csv, codecs, time, operator
from bs4 import BeautifulSoup
import glicko

# Set the glicko parameters environment
#TODO: find proper params?
GlickoEnv = glicko.Glicko2()

class Team(object):
    def __init__(self, name):
        self.name = name
        self.glicko = GlickoEnv.create_rating()
        self.historical = [(self.glicko, None, None)]

    def update(self, opponent, result, date=None, use_glicko=None):
        # We need to upate against the glicko of our opponent *before* the match,
        # so this parameter allows us to pass it in.
        if use_glicko: opponent_glicko = use_glicko
        else:          opponent_glicko = opponent.glicko

        self.glicko = GlickoEnv.rate(self.glicko, [(result, opponent_glicko)])
        self.historical.append((self.glicko, opponent, result, date))

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

def rate_teams_by_glicko(results):
    teams = {}

    for home, hscore, ascore, away, date, _ in results:
        if home not in teams: teams[home] = Team(home)
        if away not in teams: teams[away] = Team(away)

        if "rsenal" in home: print home, away

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

def get_results(filename):
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
            row[4] = time.strptime(row[4], "%A %d %B %Y")
        except ValueError:
            try:
                row[4] = time.strptime(row[4], "%A, %B %d, %Y")
            except ValueError:
                print row
                raise
        row[0] = normalize_name(row[0])
        row[3] = normalize_name(row[3])
    return results

def merge_by_date(*lists):
    return sorted(reduce(operator.add, lists), key=operator.itemgetter(4))

if __name__=="__main__":
    bpl_results = get_results("data/bpl_13_14.csv")
    cl_results = get_results("data/cl_13_14.csv")
    europa_results = get_results("data/europa_13_14.csv")
    bundesliga_results = get_results("data/bundesliga_13_14.csv")
    ligue1_results = get_results("data/ligue1_13_14.csv")
    seriea_results = get_results("data/seriea_13_14.csv")
    laliga_results = get_results("data/laliga_13_14.csv")
    results = merge_by_date(bpl_results, cl_results, europa_results, bundesliga_results, ligue1_results, seriea_results, laliga_results)
    teams = rate_teams_by_glicko(results)
    teams_by_glicko = list(sorted((t for _, t in teams.iteritems()), key=lambda x: x.glicko.mu))
