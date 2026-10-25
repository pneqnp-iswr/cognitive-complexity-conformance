"""Capture the exact SonarQube Docker RepoDigest used by the local study container.

The original protocol recorded an abbreviated digest. A mutable `sonarqube:community` tag is insufficient for a
long-lived replication recipe. This script resolves the image backing the existing `sonarqube` container when possible,
falls back to the locally cached `sonarqube:community` image, and writes the exact immutable reference to
`reproduction/sonarqube_image_digest.txt`.

It also updates the Docker command in reproduction/README.md to use that immutable reference. No network pull occurs.
"""
from __future__ import annotations
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "reproduction" / "sonarqube_image_digest.txt"
README = ROOT / "reproduction" / "README.md"


def run(*args: str) -> str:
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return p.stdout.strip()


def main() -> int:
    image_ref = None
    try:
        image_id = run("docker", "inspect", "sonarqube", "--format", "{{.Image}}")
        raw = run("docker", "image", "inspect", image_id, "--format", "{{json .RepoDigests}}")
    except Exception:
        try:
            raw = run("docker", "image", "inspect", "sonarqube:community", "--format", "{{json .RepoDigests}}")
        except Exception as e:
            print(f"WARNING: unable to resolve local SonarQube RepoDigest: {e}")
            return 0
    try:
        digs = json.loads(raw)
    except json.JSONDecodeError:
        digs = []
    for d in digs or []:
        if "@sha256:" in d and (d.startswith("sonarqube@") or "/sonarqube@" in d):
            image_ref = d
            break
    if not image_ref:
        print("WARNING: local SonarQube image has no RepoDigest; leaving reproduction command unchanged")
        return 0
    OUT.write_text(image_ref + "\n", encoding="utf-8")
    s = README.read_text(encoding="utf-8")
    # Replace only the image argument of the documented docker run command; repeated execution is idempotent.
    s2, n = re.subn(r"(?<=SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true\s)(?:sonarqube:community|sonarqube@sha256:[0-9a-f]{64})", image_ref, s)
    if n == 0 and image_ref not in s:
        print("WARNING: documented docker command anchor not found; digest file was still written")
    elif s2 != s:
        README.write_text(s2, encoding="utf-8")
    print(image_ref)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
