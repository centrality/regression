#!/usr/bin/env python3
"""
data formats

PROFESSOR = {
    "P_MUKHERJEE": {
        "salary": {
            2004: {
                "gross", "base", "overtime", "extra",
                "dgross", "dbase", "dovertime", "dextra"
            }
        },
        "centrality": {
            2004: {"pagerank", "citations", "dpagerank", "dcitations"}
        },
        "phd_year": 1970,
        "papers": set(["hep-th/049382", "1183.2066"])
    }
}

CENTRALITY = {
    "hep-th/04392": {
        2004: { "pagerank":1, "citations":2, "dpagerank":0.5, "dcitations":2 },
        ...
        2011: { "pagerank":1, "citations":2, "dpagerank":0.5, "dcitations":2 }
    },
}


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
                    "dgross": None,
                    "dbase": None,
                    "dovertime": None,
                    "dextra": None,
                    "pgross": None,
                    "pbase": None,
                    "povertime": None,
                    "pextra": None
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
                for key in ("gross", "base", "overtime", "extra"):
                    if prev[key]:
                        curr["p"+key] = curr["d"+key] / prev[key]


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
            f.write("author_id,years_since_phd,gross,base,dgross,dbase,pgross,pbase,dcitations,dpagerank\n")
            for author_id, prof in PROFESSOR.items():
                if year in prof["salary"] and \
                   year in prof["centrality"] and \
                   prof["salary"][year]["dgross"] != 0 and \
                   'phd_year' in prof:
                    # author_id, dgross, dbase, dcitations, dpagerank
                    args = [author_id, year-prof["phd_year"],
                            prof["salary"][year]["gross"], prof["salary"][year]["base"],
                            prof["salary"][year]["dgross"], prof["salary"][year]["dbase"],
                            prof["salary"][year]["pgross"], prof["salary"][year]["pbase"],
                            prof["centrality"][year]["dcitations"], prof["centrality"][year]["dpagerank"]]
                    f.write(",".join([str(arg) for arg in args]))
                    f.write('\n')
            f.flush()


def export_summary(outfolder, year):
    if os.path.exists(outfolder) is False:
        os.makedirs(outfolder)
    filename = "summary_%d.csv" % year
    with open(os.path.join(outfolder, filename), "w") as f:
        f.write("author_id,years_since_phd,gross,base,citations,pagerank\n")
        for author_id, prof in PROFESSOR.items():
            if year in prof["salary"] and year in prof["centrality"] and "phd_year" in prof:
                args = [author_id, year-prof["phd_year"],
                        prof["salary"][year]["gross"], prof["salary"][year]["base"],
                        prof["centrality"][year]["citations"], prof["centrality"][year]["pagerank"]]
                f.write(",".join([str(arg) for arg in args]))
                f.write('\n')
        f.flush()


if __name__ == "__main__":
    print('loading salary...')
    load_salary()
    print('loading uc prof papers and phd year...')
    load_prof_paper()
    load_prof_phd_year()
    print('loading centrality for papers...')
    load_centrality()
    print('calculating prof centrality...')
    calc_prof_centrality()
    print('exporting...')
    export_diff(OUTPUT_DIR)
    export_summary(OUTPUT_DIR, YEARS[-1])
    print('and we\'re done!')
