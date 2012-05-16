"""
format for the professor dictionary
{<author_key>: {"name":<name>, "author_key":<author_key>,
                "salary": {"gross", "base", "overtime", "extra",
                             "dgross", "dbase", "dovertime", "dextra"},
                "centrality": {<year> :{"pagerank", "citations",
                                 "dpagerank", "dcitations"}}}

CENTRALITY = {<arxiv_id>: {<year>: {"pagerank", "citations"}}}


"""
import os


ABSPATH = os.path.dirname(__file__)
CENTRALITY_DIR = os.path.join(ABSPATH, 'raw', 'centrality')
SALARY_FILE = os.path.join(ABSPATH, 'raw', 'salary', 'hep-th_2004_2010.csv')
PAPER_FILE = os.path.join(ABSPATH, 'raw', 'paper',
                          'hep-th_ucprofpapers_2004_2010.csv')
OUTPUT_DIR = os.path.join(ABSPATH, 'output')
PHD_FILE = os.path.join(ABSPATH, 'raw', 'prof', 'hep-th_phdyear_2004_2010.csv')


YEARS = range(2004, 2011)
CENTRALITY = {}
PROFESSOR = {}


def load_centrality():
    # parse and load
    for filename in os.listdir(CENTRALITY_DIR):
        field, year, etc = filename.split("_")
        year = int(year)
        with open(os.path.join(CENTRALITY_DIR, filename)) as f:
            f.readline()
            for line in f.readlines():
                paper = line.split(",")
                id = paper[0]
                citations = int(paper[2])
                pagerank = float(paper[5])
                if id not in CENTRALITY:
                    CENTRALITY[id] = {}
                CENTRALITY[id][year] = {"pagerank":pagerank, "citations":citations}

    # fill in years w/o data
    for id in CENTRALITY:
        for year in YEARS:
            if year not in CENTRALITY[id]:
                CENTRALITY[id][year] = {"pagerank":0.0, "citations":0}

    # calculate delta centrality
    for id in CENTRALITY:
        for year in YEARS:
            curr = CENTRALITY[id][year]
            dpagerank = curr["pagerank"]
            dcitations = curr["citations"]
            if year-1 in CENTRALITY[id]:
                prev = CENTRALITY[id][year-1]
                dpagerank -= prev["pagerank"]
                dcitations -= prev["citations"]
            curr["dpagerank"] = dpagerank
            curr["dcitations"] = dcitations


def load_salary():
    # parse and load
    with open(SALARY_FILE) as f:
        for line in f.readlines():
            parts = line.split(",")
            author_key = parts[0]
            year = int(parts[1])
            gross = float(parts[2])
            base = float(parts[3])
            overtime = float(parts[4])
            extra = float(parts[5])
            if author_key not in PROFESSOR:
                PROFESSOR[author_key] = {}
            if "salary" not in PROFESSOR[author_key]:
                PROFESSOR[author_key]["salary"] = {}
            PROFESSOR[author_key]["salary"][year] = {
                    "year": year,
                    "gross": gross,
                    "base": base,
                    "overtime": overtime,
                    "extra": extra,
                    "dgross": 0.0,
                    "dbase": 0.0,
                    "dovertime": 0.0,
                    "dextra": 0.0
            }
    for author_key, prof in PROFESSOR.items():
        if "salary" not in prof:
            prof["salary"] = {}
        salary = prof["salary"]
        for year in YEARS:
            if year in salary and year-1 in salary:
                curr = salary[year]
                prev = salary[year-1]
                for key in ("gross", "base", "overtime", "extra"):
                    curr["d"+key] = curr[key] - prev[key]


def load_salary():
    # parse and load
    with open(SALARY_FILE) as f:
        for line in f.readlines():
            parts = line.split(",")
            author_key = parts[0]
            year = int(parts[1])
            gross = float(parts[2])
            base = float(parts[3])
            overtime = float(parts[4])
            extra = float(parts[5])
            if author_key not in PROFESSOR:
                PROFESSOR[author_key] = {}
            if "salary" not in PROFESSOR[author_key]:
                PROFESSOR[author_key]["salary"] = {}
            PROFESSOR[author_key]["salary"][year] = {
                    "year": year,
                    "gross": gross,
                    "base": base,
                    "overtime": overtime,
                    "extra": extra,
                    "dgross": 0.0,
                    "dbase": 0.0,
                    "dovertime": 0.0,
                    "dextra": 0.0
            }
    for author_key, prof in PROFESSOR.items():
        if "salary" not in prof:
            prof["salary"] = {}
        salary = prof["salary"]
        for year in YEARS:
            if year in salary and year-1 in salary:
                curr = salary[year]
                prev = salary[year-1]
                for key in ("gross", "base", "overtime", "extra"):
                    curr["d"+key] = curr[key] - prev[key]


def load_prof_paper():
    with open(PAPER_FILE) as f:
        for line in f.readlines():
            line = line.strip()
            author_key, arxiv_ids = line.split(",")
            arxiv_ids = arxiv_ids.split("|")
            if author_key not in PROFESSOR:
                PROFESSOR[author_key] = {}
            prof = PROFESSOR[author_key]
            prof["papers"] = set(arxiv_ids)


def load_prof_phd_year():
    with open(PHD_FILE) as f:
        f.readline()
        for line in f.readlines():
            line = line.strip()
            author_key, year = line.split(",")
            year = int(year)
            if author_key not in PROFESSOR:
                PROFESSOR[author_key] = {}
            PROFESSOR[author_key]["phd_year"] = year


def calc_prof_centrality():
    KEYWORDS = ("pagerank", "citations", "dpagerank", "dcitations")
    for author_key, prof in PROFESSOR.items():
        prof["centrality"] = {}
        for year in YEARS:
            prof["centrality"][year] = {}
            for keyword in KEYWORDS:
                prof["centrality"][year][keyword] = 0.0
            for paper in prof["papers"]:
                if paper in CENTRALITY:
                    for keyword in KEYWORDS:
                        prof["centrality"][year][keyword] += CENTRALITY[paper][year][keyword]


def export_diff(outfolder):
    if os.path.exists(outfolder) is False:
        os.makedirs(outfolder)
    for year in YEARS:
        filename = "diff_%d.csv" % year
        with open(os.path.join(outfolder, filename), "w") as f:
            f.write("author_id,dgross,dbase,dcitations,dpagerank\n")
            for author_id, prof in PROFESSOR.items():
                if year in prof["salary"] and year in prof["centrality"] and \
                                              prof["salary"][year]["dgross"] != 0:
                    # author_id, dgross, dbase, dcitations, dpagerank
                    f.write(author_id)
                    f.write(',')
                    f.write(str(prof["salary"][year]["dgross"]))
                    f.write(',')
                    f.write(str(prof["salary"][year]["dbase"]))
                    f.write(',')
                    f.write(str(prof["centrality"][year]["dcitations"]))
                    f.write(',')
                    f.write(str(prof["centrality"][year]["dpagerank"]))
                    f.write('\n')
            f.flush()


def export_summary(outfolder, year):
    if os.path.exists(outfolder) is False:
        os.makedirs(outfolder)
    filename = "summary_%d.csv" % year
    with open(os.path.join(outfolder, filename), "w") as f:
        f.write("author_id,years_since_phd,gross,base,citations,pagerank\n")
        for author_id, prof in PROFESSOR.items():
            if year in prof["salary"] and year in prof["centrality"] and 'phd_year' in prof:
                # author_id, gross, base, citations, pagerank
                f.write(author_id)
                f.write(',')
                f.write(str(year-prof['phd_year']))
                f.write(',')
                f.write(str(prof["salary"][year]["gross"]))
                f.write(',')
                f.write(str(prof["salary"][year]["base"]))
                f.write(',')
                f.write(str(prof["centrality"][year]["citations"]))
                f.write(',')
                f.write(str(prof["centrality"][year]["pagerank"]))
                f.write('\n')
        f.flush()


if __name__ == "__main__":
    print 'loading salary...'
    load_salary()
    print 'loading uc prof papers...'
    load_prof_paper()
    print 'loading uc prof phd year...'
    load_prof_phd_year()
    print 'loading centrality...'
    load_centrality()
    print 'calculating prof centrality...'
    calc_prof_centrality()
    print 'exporting...'
    export_diff(OUTPUT_DIR)
    export_summary(OUTPUT_DIR, YEARS[-1])
    print 'and we\'re done!'
