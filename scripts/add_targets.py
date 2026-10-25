"""Annotate experiments/microcorpus/expected.csv with a `target` column: the single rule/construct each case
isolates (used for root-cause attribution). Idempotent."""
import csv, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "experiments" / "microcorpus" / "expected.csv"
COMMON = {
    "c01": "R11", "c02": "B1.1", "c03": "R2", "c04": "R2", "c05": "B1.1", "c06": "B1.2", "c06b": "B1.2", "c06c": "B1.2", "c06d": "B1.2",
    "c07": "B1.3", "c07b": "B1.3", "c07c": "B1.3", "c08": "B1.4", "c08b": "B1.4", "c09": "B1.5", "c09b": "B1.5", "c10": "B1.5", "c11": "B1.5",
    "c12": "R7", "c13": "R7", "c14": "B3.1", "c15": "B3", "c16": "B1.5", "c17": "R7", "c18": "B2.1", "c19": "B2.1", "c19b": "B1.1",
    "c20": "B3.1", "c21": "B3.1", "c22": "B2.4", "c23": "B1.7", "c24": "B1.7", "c25": "B1.7", "c26": "B1.7", "c27": "B1.7", "c28": "R15",
    "c29": "B1.7", "c30": "R15", "c31": "B1.7", "c32": "B1.7", "c33": "B1.7", "c34": "B1.7", "c35": "B1.7", "c36": "R14", "c37": "R14",
    "c38": "B1.8", "c39a": "B1.8", "c39b": "B1.8", "c40": "B2.6", "c41": "B2.6", "c43": "B2.6", "c47": "B2.6", "c48": "COMP", "c49": "COMP",
    "c50": "ELSE-LOOP", "c51": "ELSE-LOOP", "c52": "ELSE-LOOP", "c53": "R11", "c54": "B1.1", "c55": "B3.1", "c56": "B3", "c57": "B1.1",
    "c58": "B2.1", "c59": "COMP", "c60": "B1.7", "c61": "R11", "c62": "B1.3", "c63": "B1.6", "c66": "B2.6", "c67": "B1.7", "c68": "R14",
    "c69": "R11", "c70": "COMP", "c71": "R11", "c72": "R7", "c73": "R14", "c74": "B3.1", "c75": "B1.7", "c76": "B2.6", "c77": "B1.1",
    "c78": "B1.8", "c79": "R15", "c80": "B1.7", "c81": "R13", "c82": "R13", "c83": "R13", "c84": "B2.6", "c85": "R11", "c86": "B1.3",
    "c87": "B1.1", "c88": "B1.1", "c89": "B1.8", "c90": "B1.7", "c91": "B1.1", "c92": "R11", "c93": "B1.2", "c94": "B1.6", "c95": "B1.1",
    "c96": "B1.8", "c97": "B1.7", "C1": "C", "C2": "C", "C3": "C", "C4": "C", "sumOfPrimes": "B1.6", "getWords": "B1.2", "myMethod": "B3", "myMethod2": "B2.6",
}
LANG_SPECIFIC = {("python", "c42"): "A.3", ("python", "c44"): "A.3", ("python", "c45"): "A.3", ("python", "c46"): "A.3",
                 ("javascript", "c42"): "A.2", ("javascript", "c44"): "A.2", ("javascript", "c45"): "A.2",
                 ("python", "c64"): "B1.8", ("java", "c64"): "B1.6", ("javascript", "c64"): "B1.6", ("go", "c64"): "B1.6",
                 ("python", "c65"): "B1.7", ("go", "c65"): "B1.6", ("python", "c63"): "B1.1"}
rows = list(csv.DictReader(open(P, encoding="utf-8")))
for r in rows:
    cid = r["case_id"].split("-", 1)[1]
    r["target"] = LANG_SPECIFIC.get((r["lang"], cid)) or COMMON.get(cid) or "?"
missing = [r["case_id"] for r in rows if r["target"] == "?"]
assert not missing, missing
cols = [c for c in rows[0].keys() if c != "target"] + ["target"]
with open(P, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(rows)
print("targets written for", len(rows), "cases")
