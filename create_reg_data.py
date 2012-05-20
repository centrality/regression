#!/usr/bin/env python3
"""
data formats

PROFESSOR = {
    "P_MUKHERJEE": {
        "salary": {
            2004: {
                "": {"gross", "base", "overtime", "extra"},
                "Δ": {"gross", "base", "overtime", "extra"},
                "p": {"gross", "base", "overtime", "extra"},
            }
        },
        "centrality": {
            2004: {"pagerank", "citations", "Δpagerank", "Δcitations"}
        },
        "phd_year": 1970,
        "papers": set(["hep-th/049382", "1183.2066"])
    }
}

CENTRALITY = {
    "hep-th/04392": {
        2004: { "pagerank":1, "citations":2, "Δpagerank":0.5, "Δcitations":2 },
        ...
        2011: { "pagerank":1, "citations":2, "Δpagerank":0.5, "Δcitations":2 }
    },
}


"""
import os
import csv
from collections import namedtuple
from collections import defaultdict
infinite_dict = lambda : defaultdict(infinite_dict)


ABSPATH = os.path.dirname(__file__)
CENTRALITY_DIR = os.path.join(ABSPATH, 'raw', 'centrality')
SALARY_FILE = os.path.join(ABSPATH, 'raw', 'salary', 'hep-th_2004_2010.csv')
PAPER_FILE = os.path.join(ABSPATH, 'raw', 'paper',
                          'hep-th_ucprofpapers_2004_2010.csv')
OUTPUT_DIR = os.path.join(ABSPATH, 'output')
PHD_FILE = os.path.join(ABSPATH, 'raw', 'prof', 'hep-th_phdyear_2004_2010.csv')


YEARS = range(2004, 2011)
CENTRALITY = infinite_dict()
PROFESSOR = infinite_dict()


def load_centrality():
    '''Loads and normalizes the input centralities and calculates the changes.'''
    # parse and load
    for filename in os.listdir(CENTRALITY_DIR):
        field, year, etc = filename.split("_")
        year = int(year)
        with open(os.path.join(CENTRALITY_DIR, filename), 'rt') as f:
            f.readline()
            for line in f.readlines():
                paper = line.split(",")
                id = paper[0]
                citations = int(paper[2])
                pagerank = float(paper[5])
                CENTRALITY[id][year] = {"pagerank":pagerank, "citations":citations}
    # calculate delta centrality
    for id in CENTRALITY:
        for year in YEARS:
            curr = CENTRALITY[id][year]
            prev = CENTRALITY[id][year - 1]
            curr["Δpagerank"] = (curr["pagerank"] or 0) - (prev["pagerank"] or 0)
            curr["Δcitations"] = (curr["citations"] or 0) - (prev["citations"] or 0)
    # @@@@@ It seems some papers don't have centralities!


def load_salary():
    '''Loads and normalizes the input salaries and calculates the changes.'''
    SALARY_TYPES = ("gross", "base", "overtime", "extra")
    # parse and load
    with open(SALARY_FILE, "rt") as f:
        for info in map(namedtuple("SalaryInfo", ['author_key', 'year', 'gross', 'base', 'overtime', 'extra', 'x0', 'x1', 'x2', 'x3'])._make, csv.reader(f)):
            PROFESSOR[info.author_key]["salary"][info.year] = {
                "": {
                    "gross": info.gross,
                    "base": info.base,
                    "overtime": info.overtime,
                    "extra": info.extra,
                },
                "Δ": defaultdict(),	# default is None
                "p": defaultdict(),
            }
    for author_key, prof in PROFESSOR.items():
        salary = prof["salary"]
        for year in YEARS:
            if year in salary and year-1 in salary:
                curr = salary[year]
                prev = salary[year-1]
                for t in SALARY_TYPES:
                    curr["d"][t] = curr[""][t] - prev[""][t]
                    curr["p"][t] = curr["Δ"][t] / prev[""][t]


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
    KEYWORDS = ("pagerank", "citations", "Δpagerank", "Δcitations")
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

# Doesn't work right now

#def export_diff(outfolder):
    #if os.path.exists(outfolder) is False:
        #os.makedirs(outfolder)
    #for year in YEARS:
        #filename = "diff_%d.csv" % year
        #with open(os.path.join(outfolder, filename), "w") as f:
            #f.write("author_id,years_since_phd,gross,base,Δgross,Δbase,pgross,pbase,Δcitations,Δpagerank\n")
            #for author_id, prof in PROFESSOR.items():
                #if year in prof["salary"] and \
                   #year in prof["centrality"] and \
                   #prof["salary"][year]["Δgross"] != 0 and \
                   #'phd_year' in prof:
                    ## author_id, Δgross, Δbase, Δcitations, Δpagerank
                    #args = [author_id, year-prof["phd_year"],
                            #prof["salary"][year]["gross"], prof["salary"][year]["base"],
                            #prof["salary"][year]["Δgross"], prof["salary"][year]["Δbase"],
                            #prof["salary"][year]["pgross"], prof["salary"][year]["pbase"],
                            #prof["centrality"][year]["Δcitations"], prof["centrality"][year]["Δpagerank"]]
                    #f.write(",".join([str(arg) for arg in args]))
                    #f.write('\n')
            #f.flush()


#def export_summary(outfolder, year):
    #if os.path.exists(outfolder) is False:
        #os.makedirs(outfolder)
    #filename = "summary_%d.csv" % year
    #with open(os.path.join(outfolder, filename), "w") as f:
        #f.write("author_id,years_since_phd,gross,base,citations,pagerank\n")
        #for author_id, prof in PROFESSOR.items():
            #if year in prof["salary"] and year in prof["centrality"] and "phd_year" in prof:
                #args = [author_id, year-prof["phd_year"],
                        #prof["salary"][year]["gross"], prof["salary"][year]["base"],
                        #prof["centrality"][year]["citations"], prof["centrality"][year]["pagerank"]]
                #f.write(",".join([str(arg) for arg in args]))
                #f.write('\n')
        #f.flush()


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
    #print('exporting...')
    #export_diff(OUTPUT_DIR)
    #export_summary(OUTPUT_DIR, YEARS[-1])
    #print('and we\'re done!')