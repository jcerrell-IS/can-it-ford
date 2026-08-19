#!/usr/bin/env python3
"""Stationarity across the comparable Vista population. Pure stdlib, runs on the
LOGIN NODE in seconds. Deliberately NOT submitted to the gg partition: filling
7,800 idle cores with a job that takes seconds on one core is the same waste as
an idle idev session."""
import csv, os, sys
sys.path.insert(0, "/work/11603/jcerrell0629/vista")
from r9_stationarity import analyze, effective_sample_size
ROOT="/work/11603/jcerrell0629"
paths=[l.strip() for l in open("/work/11603/jcerrell0629/vista/r9_comparable.txt") if l.strip()]
w=csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["path","n","chan","discard","winlen","n_eff","stationary"])
for rel in paths:
    p=os.path.join(ROOT,rel)
    cols={}
    try:
        with open(p,newline="",errors="replace") as fh:
            rd=csv.DictReader(fh)
            for f in rd.fieldnames: cols[f.strip()]=[]
            for row in rd:
                for f in rd.fieldnames:
                    try: cols[f.strip()].append(float(row[f]))
                    except (TypeError,ValueError): pass
    except Exception as e:
        w.writerow([rel,-1,"ERR",str(e)[:40],"","",""]); continue
    for ch in ("dx","dmag","vx","vmag"):
        if ch not in cols or len(cols[ch])<20:
            w.writerow([rel,len(cols.get(ch,[])),ch,"","","","not-evaluable"]); continue
        r=analyze(cols[ch],ch)
        st=r["stationary_at_5pct"]
        w.writerow([rel,r["n_total"],ch,r["recommended_discard"],r["window_len"],
                    f"{r['n_eff']:.4f}", "n/a" if st is None else ("yes" if st else "NO")])
