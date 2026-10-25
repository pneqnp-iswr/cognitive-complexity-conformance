"""Configure the local SonarQube Community Build for per-function metric extraction.
Creates one quality profile per language ('cc-study-<lang>') that activates ONLY the Cognitive
Complexity rule (S3776) with threshold 0 and the cyclomatic-complexity rule with threshold 0/1,
so every function yields one issue whose message carries the metric value. Makes them default.
Also creates a user token saved to data/sonar_token.txt (git-ignored).
Idempotent."""
import json, pathlib, sys, requests

BASE = "http://localhost:9000"
AUTH = ("admin", "admin")
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / "data" / "sonar_token.txt"

# language key -> list of (rule key, {param: value})
RULES = {
    "py":   [("python:S3776", {"threshold": "0"}), ("python:FunctionComplexity", {"maximumFunctionComplexityThreshold": "0"})],
    "java": [("java:S3776", {"Threshold": "0"}), ("java:S1541", {"Threshold": "0"})],
    "js":   [("javascript:S3776", {"threshold": "0"}), ("javascript:S1541", {"maximumFunctionComplexityThreshold": "0"})],
    "ts":   [("typescript:S3776", {"threshold": "0"}), ("typescript:S1541", {"Threshold": "0"})],
    "go":   [("go:S3776", {"threshold": "0"})],
}

def api(method, path, **kw):
    r = requests.request(method, BASE + path, auth=AUTH, timeout=60, **kw)
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
    return r

def main():
    print("server version:", api("GET", "/api/server/version").text)
    for lang, rules in RULES.items():
        name = f"cc-study-{lang}"
        profs = api("GET", "/api/qualityprofiles/search", params={"language": lang}).json()["profiles"]
        prof = next((p for p in profs if p["name"] == name), None)
        if not prof:
            prof = api("POST", "/api/qualityprofiles/create", data={"language": lang, "name": name}).json()["profile"]
            print("created profile", lang, prof["key"])
        key = prof["key"]
        # deactivate everything first (fresh profiles are empty; keep idempotent)
        active = api("GET", "/api/rules/search", params={"qprofile": key, "activation": "true", "ps": 500}).json()["rules"]
        wanted = {r for r, _ in rules}
        for r in active:
            if r["key"] not in wanted:
                api("POST", "/api/qualityprofiles/deactivate_rule", data={"key": key, "rule": r["key"]})
        for rule, params in rules:
            p = ";".join(f"{k}={v}" for k, v in params.items())
            api("POST", "/api/qualityprofiles/activate_rule", data={"key": key, "rule": rule, "params": p, "severity": "MAJOR"})
        api("POST", "/api/qualityprofiles/set_default", data={"language": lang, "qualityProfile": name})
        active = api("GET", "/api/rules/search", params={"qprofile": key, "activation": "true", "ps": 500, "f": "params,actives"}).json()
        print(lang, name, "active rules:", [(a["key"]) for a in active["rules"]],
              "params:", {k: [(p["key"], p["value"]) for p in v[0]["params"]] for k, v in active.get("actives", {}).items()})
    # token
    if not TOKEN_FILE.exists():
        toks = api("GET", "/api/user_tokens/search").json()["userTokens"]
        if any(t["name"] == "cc-study" for t in toks):
            api("POST", "/api/user_tokens/revoke", data={"name": "cc-study"})
        tok = api("POST", "/api/user_tokens/generate", data={"name": "cc-study", "type": "GLOBAL_ANALYSIS_TOKEN"}).json()["token"]
        TOKEN_FILE.parent.mkdir(exist_ok=True, parents=True)
        TOKEN_FILE.write_text(tok, encoding="utf-8")
        print("token written to", TOKEN_FILE)
    else:
        print("token exists at", TOKEN_FILE)

if __name__ == "__main__":
    main()
