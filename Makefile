# Can It Ford. Run `make help`.
#
# PYTHON defaults to the miniforge env this project was developed in, because the
# system python3 on this machine has no numpy. Override it if yours differs:
#   make test PYTHON=/path/to/python

PYTHON ?= /opt/homebrew/Caskroom/miniforge/base/envs/can-it-ford/bin/python
PYTEST := $(PYTHON) -m pytest

.PHONY: help install test gates checks facts figures clean

help:
	@echo "make install   pip install -r requirements.txt"
	@echo "make test      run the pytest suite"
	@echo "make gates     run the physics and parameter gates"
	@echo "make checks    run the repository integrity checks"
	@echo "make facts     re-derive the headline numbers from the committed CSVs"
	@echo "make figures   rebuild the poster and paper figures"
	@echo ""
	@echo "PYTHON is $(PYTHON)"

install:
	$(PYTHON) -m pip install -r requirements.txt

# KNOWN STATE, measured 2026-08-26: 27 passed, 6 failed.
# All 6 failures are in tests/test_count_claims_check.py, where the checker returns an
# empty payload instead of a denial. That is a guardrail defect, not a physics defect,
# and it is left visible on purpose. See docs/REPRODUCE.md.
test:
	$(PYTEST) tests -q

gates:
	$(PYTHON) .claude/checks/params_check.py
	$(PYTHON) .claude/checks/physics_gates_literature.py

checks:
	$(PYTHON) .claude/checks/register_integrity.py

# Re-derives the headline numbers straight from the committed CSVs, so a reader can
# check the claims without a GPU. Each command is also printed in docs/CANONICAL_FACTS.md.
facts:
	@$(PYTHON) -c "import csv,collections; \
r=list(csv.DictReader(open('data/all_runs_inventory.csv'))); \
w=sum(int(x['n_water']) for x in r); v=sum(int(x['n_vehicle']) for x in r); \
print('gated runs           ', len(r)); \
print('grids                ', sorted({x['n_grid'] for x in r})); \
print('masses kg            ', sorted({x['mass_kg'] for x in r})); \
print('water particles      ', w); \
print('vehicle particles    ', v); \
print('total particles      ', w+v); \
print('largest run, water   ', max(int(x['n_water']) for x in r))"
	@$(PYTHON) -c "import csv,collections; \
print('verdicts             ', dict(collections.Counter(x['mode'] for x in csv.DictReader(open('data/failure_modes_by_run_classified.csv')))))"
	@$(PYTHON) -c "import csv,collections; \
s=list(csv.DictReader(open('data/scenario_sweep.csv'))); print('L1 conditions        ', len(s)); \
[print('FORD', c.replace('L1_verdict_','').ljust(16), dict(collections.Counter(x[c] for x in s))['FORD']) \
 for c in ['L1_verdict_small_passenger','L1_verdict_large_passenger','L1_verdict_large_4wd']]"

figures:
	$(PYTHON) analysis/make_poster_figures.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
