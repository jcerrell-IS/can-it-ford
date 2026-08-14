#!/usr/bin/env python3
"""Verify every DOI cited in DISPATCH 11 against Crossref. Primary-source check.
Prints title, print/online year, journal, type, authors, and any update-to /
retraction flag. No claim in the deliverable may cite a DOI this script cannot
resolve."""
import json, time, urllib.error, urllib.parse, urllib.request

DOIS = [
    # (label as written in the dispatch, doi)
    ("Smith, Modra, Felder 2019 [T1]",            "10.1111/jfr3.12527"),
    ("Al-Qadami 2021 full-scale [T1]",            "10.1007/s11069-021-04949-6"),
    ("Arrighi 2015 drag/lift [T1]",               "10.1016/J.JFLUIDSTRUCTS.2015.06.010"),
    ("Xia/Falconer/Xiao/Wang 2013 [T1]",          "10.1007/s11069-013-0889-2"),
    ("Hu/Li/Wang/Fang 2023 [T1]",                 "10.1016/j.jhydrol.2023.129525"),
    ("Martinez-Gomariz 2017 [T1]",                "10.1080/1573062X.2017.1301501"),
    ("Teo/Xia/Falconer/Lin 2012 [T1]",            "10.1080/15715124.2012.674040"),
    ("Shah/Mustaffa/M-Gomariz/Yusof 2020? [T2]",  "10.1111/jfr3.12657"),
    ("Al-Qadami 2022 MOVING perpendicular [T2]",  "10.1111/jfr3.12828"),
    ("He et al 2026 closest match [T2]",          "10.1115/1.4071177"),
    ("Zheng Xin & Su Donghai 2021 [T3]",          "10.1177/0954407020942005"),
    ("Shah et al 2018 force balance",             "10.1051/matecconf/201820307003"),
    ("Pregnolato 2017 speed-depth",               "10.1016/j.trd.2017.06.020"),
    ("Kramer/Terheiden/Wieprecht 2016 head",      "10.1016/J.IJDRR.2016.04.003"),
    ("Al-Qadami 2023 exposed/stationary",         "10.3390/su151713262"),
    ("Azhar 2023",                                "10.1111/jfr3.12885"),
    ("Xiong 2024",                                "10.1029/2023WR036739"),
    ("Azhar/Bui/Pauwels 2026 watertightness",     "10.1111/jfr3.70181"),
    ("Steffen et al 2008 PPC convergence",        "10.3970/CMES.2008.031.107"),
    ("Zhang et al 2026 ADD-as-confirmed",         "10.1016/j.cma.2025.118428"),
    ("Qian et al 2022 FLAGGED FABRICATED",        "10.1016/j.cma.2022.114965"),
    ("Hu et al 2018 CPIC",                        "10.1145/3197517.3201293"),
    ("Canelas 2018 DualSPHysics-Chrono",          "10.1016/J.APOR.2018.04.015"),
    ("Zhao et al 2019 in/outflow BC",             "10.1016/J.COMPFLUID.2018.10.007"),

    # --- Tier 4, identified this session. Kramer 2021 IS the ~0.3% benchmark. ---
    ("Kramer 2021 sphere heave decay [T4 0.3%]",  "10.3390/en14020269"),
    ("Grift 2019 accelerating plate [T4]",        "10.1017/jfm.2019.102"),
    ("Waugh & Ellis 1969 sphere/free surf [T4]",  "10.2514/3.62822"),
    ("Chung 1977 added mass/damping [T4]",        "10.2514/3.63081"),
    ("Kamra 2019 dambreak + cylinder [T4]",       "10.1016/J.JFLUIDSTRUCTS.2019.01.015"),

    # --- The CFD/MBD fording lineage absent from the dispatch's tiers ---
    ("Wasfy 2015 MBD+SPH vehicle fording",        "10.1115/DETC2015-47142"),
    ("Yamashita 2022 amphibious surf zone",       "10.1016/j.oceaneng.2022.111607"),
    ("Yamashita 2023 data-driven shallow water",  "10.1115/detc2023-115254"),
    ("Yamashita 2024 vehicle mobility",           "10.1115/1.4064971"),
    ("Tison 2021 amphibious egress, drivetrain",  "10.4271/2021-01-0252"),
    ("Liu 2023 self-propelled river crossing",    "10.1063/5.0174148"),

    # --- The two IJRBM Shah papers the year amendment actually refers to ---
    ("Shah IJRBM 19:1-23  issued2019/print2021",  "10.1080/15715124.2019.1566240"),
    ("Shah IJRBM 19:25-41 issued2019/print2021",  "10.1080/15715124.2019.1687487"),
]

def fetch(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    req = urllib.request.Request(url, headers={
        # Crossref's "polite pool" asks for a contact address. This is the same
        # institutional address already recorded as the author of every commit in
        # this public repo, so it adds no new exposure. Do not put a personal
        # address here.
        "User-Agent": "can-it-ford-citation-audit/1.0 "
                      "(mailto:jcerrell29@students.claremontmckenna.edu)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["message"]

def yr(d, key):
    v = d.get(key, {}).get("date-parts", [[None]])[0][0]
    return v

for label, doi in DOIS:
    try:
        m = fetch(doi)
    except urllib.error.HTTPError as e:
        print(f"!! UNRESOLVED  {doi}\n   {label}\n   HTTP {e.code}\n")
        continue
    except Exception as e:
        print(f"!! ERROR       {doi}\n   {label}\n   {type(e).__name__}: {e}\n")
        continue
    title = (m.get("title") or ["(no title)"])[0]
    auths = "; ".join(a.get("family", a.get("name", "?")) for a in m.get("author", []))
    print(f"OK  {doi}")
    print(f"    cited-as : {label}")
    print(f"    title    : {title}")
    print(f"    print/onl: {yr(m,'published-print')} / {yr(m,'published-online')}   issued: {yr(m,'issued')}")
    print(f"    journal  : {(m.get('container-title') or [''])[0]}")
    print(f"    type     : {m.get('type')}   vol {m.get('volume')} iss {m.get('issue')} p {m.get('page')}")
    print(f"    authors  : {auths}")
    if m.get("update-to"):
        print(f"    ** UPDATE-TO FLAG: {[(u.get('type'), u.get('DOI')) for u in m['update-to']]}")
    print()
    time.sleep(0.15)
