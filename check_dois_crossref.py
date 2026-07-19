import sys
import re
import json
import time
import urllib.request
import urllib.error

MAILTO = "jcerrell29@cmc.edu"

def extract_dois(bib_path):
    text = open(bib_path, "r", encoding="utf-8", errors="ignore").read()
    raw = re.findall(r'doi\s*=\s*[{"]([^}"]+)[}"]', text, flags=re.IGNORECASE)
    cleaned = []
    for d in raw:
        d = d.strip()
        d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
        cleaned.append(d)
    return cleaned

def extract_entries(bib_path):
    text = open(bib_path, "r", encoding="utf-8", errors="ignore").read()
    return re.findall(r'@\w+\{([^,]+),', text)

def extract_arxiv_preprints(bib_path):
    text = open(bib_path, "r", encoding="utf-8", errors="ignore").read()
    blocks = re.split(r'(?=@\w+\{)', text)
    found = []
    for block in blocks:
        if re.search(r'eprinttype\s*=\s*[{"]arxiv[}"]', block, flags=re.IGNORECASE):
            key_match = re.match(r'@\w+\{([^,]+),', block)
            eprint_match = re.search(r'eprint\s*=\s*[{"]([^}"]+)[}"]', block, flags=re.IGNORECASE)
            key = key_match.group(1) if key_match else "unknown"
            eprint = eprint_match.group(1) if eprint_match else "unknown"
            found.append((key, eprint))
    return found

def check_doi(doi):
    url = f"https://api.crossref.org/works/{doi}?mailto={MAILTO}"
    req = urllib.request.Request(url, headers={"User-Agent": f"can-it-ford-citation-check/1.0 (mailto:{MAILTO})"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"doi": doi, "status": "NOT_FOUND", "title": None, "retracted": False, "updates": []}
        return {"doi": doi, "status": f"HTTP_ERROR_{e.code}", "title": None, "retracted": False, "updates": []}
    except Exception as e:
        return {"doi": doi, "status": f"ERROR_{type(e).__name__}", "title": None, "retracted": False, "updates": []}

    msg = data.get("message", {})
    title_list = msg.get("title", [])
    title = title_list[0] if title_list else None
    updates = msg.get("update-to", [])
    update_types = [u.get("type") for u in updates]
    retracted = any(t == "retraction" for t in update_types)
    return {"doi": doi, "status": "OK", "title": title, "retracted": retracted, "updates": update_types}

def main():
    if len(sys.argv) < 2:
        print("usage: python3 check_dois_crossref.py path/to/references.bib")
        sys.exit(1)

    bib_path = sys.argv[1]
    all_entries = extract_entries(bib_path)
    dois = extract_dois(bib_path)
    arxiv_preprints = extract_arxiv_preprints(bib_path)

    print(f"{len(all_entries)} total bibtex entries in {bib_path}")
    print(f"{len(dois)} have a doi field, will check against Crossref")
    print(f"{len(arxiv_preprints)} are arXiv preprints with no doi field, will list only, not checked")
    accounted_for = len(dois) + len(arxiv_preprints)
    if accounted_for < len(all_entries):
        print(f"WARNING: {len(all_entries) - accounted_for} entries have neither a doi field nor an arxiv eprint field, not checked at all, review manually")
    print("")

    if arxiv_preprints:
        print("arXiv preprints (expected NOT_FOUND on Crossref, DataCite-registered, not a red flag):")
        for key, eprint in arxiv_preprints:
            print(f"  {key}  arXiv:{eprint}")
        print("")

    results = []
    for i, doi in enumerate(dois):
        result = check_doi(doi)
        results.append(result)
        flag = ""
        if result["status"] != "OK":
            flag = "  <-- CHECK MANUALLY, DID NOT RESOLVE"
        elif result["retracted"]:
            flag = "  <-- RETRACTED, DO NOT CITE"
        elif result["updates"]:
            flag = f"  <-- has update-to: {result['updates']}"
        title_display = result["title"][:70] if result["title"] else "(no title returned)"
        print(f"[{i+1}/{len(dois)}] {doi}  {result['status']}{flag}")
        print(f"    {title_display}")
        time.sleep(0.3)

    print("")
    bad = [r for r in results if r["status"] != "OK"]
    retracted = [r for r in results if r["retracted"]]
    print(f"summary: {len(dois)} checked, {len(bad)} did not resolve, {len(retracted)} retracted")

if __name__ == "__main__":
    main()
