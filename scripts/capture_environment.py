"""Capture environment provenance into reproduction/environment.json and environment.md."""
import json, os, pathlib, platform, subprocess, sys, datetime

root = pathlib.Path(__file__).resolve().parents[1]
out_dir = root / "reproduction"
out_dir.mkdir(exist_ok=True)


def _tool_runtimes():
    """Record the runtimes the study's tools actually use, not merely what is first on PATH."""
    import subprocess, sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1] / "src"))
    out = {}
    try:
        from ccstudy import tools as _t
        cands = {"java_pmd": getattr(_t, "JAVA17", None), "java_cognitive_java": getattr(_t, "JAVA21", None)}
        for key, home in cands.items():
            if home is None:
                continue
            exe = _pl.Path(home) / "bin" / "java.exe"
            if not exe.exists():
                exe = _pl.Path(home) / "bin" / "java"
            if exe.exists():
                r = subprocess.run([str(exe), "-version"], capture_output=True, text=True, timeout=60)
                out[key] = (r.stderr or r.stdout).strip().splitlines()[0]
        go = getattr(_t, "GO", None) or (_pl.Path(__file__).resolve().parents[1] / "tools" / "go" / "bin" / "go.exe")
        go = _pl.Path(go)
        if go.exists():
            out["go"] = subprocess.run([str(go), "version"], capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:  # never fail the capture because a tool is absent
        out["error"] = f"{type(e).__name__}: {e}"
    out["manuscript_build"] = "Microsoft Word with pywin32 COM automation (scripts/build_manuscript.py); required only to rebuild the .docx/.pdf, not for any number"
    return out

def run(cmd, shell=False):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=shell)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"ERROR: {e}"

env = {
    "tool_runtimes": _tool_runtimes(),
    "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "os": platform.platform(),
    "os_version": platform.version(),
    "machine": platform.machine(),
    "processor": platform.processor(),
    "cpu_count_logical": os.cpu_count(),
    "python": sys.version,
    "python_executable": sys.executable,
}
env["cpu_name"] = run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"])
env["ram_bytes"] = run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"])
env["gpu"] = run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) -join '; '"])
env["nvidia_smi"] = run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
env["git"] = run(["git", "--version"])
env["node"] = run(["node", "--version"])
env["java"] = run(["java", "-version"])
env["docker"] = run(["docker", "--version"])
env["cargo"] = run([str(pathlib.Path.home() / ".cargo" / "bin" / "cargo.exe"), "--version"])
env["rustc"] = run([str(pathlib.Path.home() / ".cargo" / "bin" / "rustc.exe"), "--version"])
env["pip_freeze"] = run([sys.executable, "-m", "pip", "freeze"]).splitlines()
try:
    import torch
    env["torch"] = {"version": torch.__version__, "cuda": torch.version.cuda, "cuda_available": torch.cuda.is_available(),
                    "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}
except Exception as e:
    env["torch"] = f"ERROR: {e}"
(out_dir / "environment.json").write_text(json.dumps(env, indent=1), encoding="utf-8")
(out_dir / "requirements-freeze.txt").write_text("\n".join(env["pip_freeze"]) + "\n", encoding="utf-8")
md = ["# Environment provenance", "", f"Captured (UTC): {env['captured_utc']}", "",
      "| Item | Value |", "|---|---|"]
for k in ["os", "os_version", "machine", "cpu_name", "cpu_count_logical", "ram_bytes", "gpu", "nvidia_smi", "python", "python_executable", "git", "node", "java", "docker", "cargo", "rustc", "torch"]:
    v = env[k]
    if isinstance(v, (dict, list)):
        v = json.dumps(v)
    v = str(v).replace("\n", " / ").replace("|", "\\|")
    md.append(f"| {k} | {v} |")
md.append("")
md.append("Full pip freeze: `reproduction/requirements-freeze.txt`.")
(out_dir / "environment.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
