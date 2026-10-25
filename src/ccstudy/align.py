"""Align tool rows to tree-sitter function units.

Rule (fixed in advance): a tool row for file F reported at line L is assigned to the unit U in F with
decl_line <= L <= body_line (the declaration header span) when exactly one such unit exists at the
smallest enclosing depth; if several units share the header span (e.g. one-line nested arrow functions),
prefer a unit whose kind is compatible with the tool's reporting convention (root functions first) and
whose name matches when the tool reports a name. Rows that cannot be assigned uniquely are kept as
'unaligned' and counted in the coverage tables; they are excluded from agreement statistics.
"""
from __future__ import annotations
import collections

def _name_matches(row_name: str, unit) -> bool:
    if not row_name:
        return True
    rn = row_name.split("::")[-1].split(".")[-1].split("(")[0].strip()
    return rn in ("", "<anonymous>") or rn == unit.name or unit.name in ("<anonymous>",)

def align(units_by_file: dict, rows: list, tool: str, metric: str = "cognitive"):
    """Returns (assigned: dict[(file, unit_idx)] -> row, unaligned: list[row], duplicates: list[row])."""
    assigned, unaligned, dups = {}, [], []
    index = {}
    for f, units in units_by_file.items():
        idx = collections.defaultdict(list)
        for u in units:
            for L in range(u.decl_line, u.body_line + 1):
                idx[L].append(u)
        index[f] = idx
    for r in rows:
        if r["tool"] != tool or r["metric"] != metric or r.get("line") is None:
            continue
        f = r["file"]
        cands = index.get(f, {}).get(r["line"], [])
        cands = [u for u in cands if _name_matches(r.get("name", ""), u)]
        if not cands:
            unaligned.append(r); continue
        if len(cands) > 1:
            # prefer the shallowest unit whose decl_line == reported line, then shallowest overall
            exact = [u for u in cands if u.decl_line == r["line"]]
            pool = exact or cands
            pool = sorted(pool, key=lambda u: (u.depth, u.decl_line))
            # if still ambiguous (same depth & same decl line), drop
            if len(pool) > 1 and pool[0].depth == pool[1].depth and pool[0].decl_line == pool[1].decl_line and r.get("name", "") in ("", "<anonymous>"):
                unaligned.append(r); continue
            u = pool[0]
        else:
            u = cands[0]
        key = (f, u.idx)
        if key in assigned:
            dups.append(r); continue
        assigned[key] = r
    return assigned, unaligned, dups
