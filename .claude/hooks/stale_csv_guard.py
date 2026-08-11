import json, sys, re
data = json.load(sys.stdin)
ti = data.get("tool_input", {})
blob = (ti.get("command", "") + " " + ti.get("file_path", ""))
if "scenario_sweep.csv" not in blob:
    sys.exit(0)
confirms = re.search(r"wc\s+-l|head\s+-1|NF|awk|column", blob)
if not confirms:
    sys.stderr.write("BLOCKED: scenario_sweep.csv touched without a live column-count check. Run awk -F, 'NR==1{print NF}' <file> first and confirm 10 columns, not 5.\n")
    sys.exit(2)
sys.exit(0)
