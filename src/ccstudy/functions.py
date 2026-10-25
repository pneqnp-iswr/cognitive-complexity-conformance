"""Language-independent enumeration of function-like units with tree-sitter.

For every source file we produce a list of FunctionUnit records:
  file, lang, kind, name, qualified_name, decl_line (1-based line where the node starts),
  name_line (line of the identifier, or decl_line for anonymous), body_line, end_line,
  depth (0 = root, i.e. not enclosed by another function-like node), parent_id,
  has_nested (contains a nested function-like node), nested_count, class_name (enclosing class, if any),
  features: counts of syntactic constructs relevant to the spec (used for root-cause attribution).

Tool outputs are aligned to these units by (file, line) where the reported line falls within
[decl_line, body_line] of a unique unit (see align.py).
"""
from __future__ import annotations
import dataclasses, pathlib, re
from typing import Iterator
from tree_sitter_language_pack import get_parser

FUNCTION_NODES = {
    "python": {"function_definition": "function", "lambda": "lambda"},
    "java": {"method_declaration": "method", "constructor_declaration": "constructor", "lambda_expression": "lambda",
             "static_initializer": "initializer"},
    "javascript": {"function_declaration": "function", "function_expression": "function_expr", "arrow_function": "arrow",
                   "method_definition": "method", "generator_function_declaration": "function", "generator_function": "function_expr",
                   "function": "function_expr"},
    "typescript": {"function_declaration": "function", "function_expression": "function_expr", "arrow_function": "arrow",
                   "method_definition": "method", "generator_function_declaration": "function", "generator_function": "function_expr",
                   "function": "function_expr"},
    "go": {"function_declaration": "function", "method_declaration": "method", "func_literal": "lambda"},
}
CLASS_NODES = {"python": {"class_definition"}, "java": {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"},
               "javascript": {"class_declaration", "class"}, "typescript": {"class_declaration", "class", "abstract_class_declaration"}, "go": set()}
# anonymous class bodies in Java: 'object_creation_expression' containing 'class_body' -> methods inside are nested in the enclosing method
LANG_EXT = {"python": {".py"}, "java": {".java"}, "javascript": {".js", ".jsx", ".mjs", ".cjs"}, "typescript": {".ts", ".tsx"}, "go": {".go"}}

# feature counters: node types per language (for attribution)
FEATURES = {
    "python": {"if_statement": "if", "elif_clause": "elif", "else_clause": "else", "conditional_expression": "ternary",
               "for_statement": "for", "while_statement": "while", "except_clause": "catch", "match_statement": "match",
               "boolean_operator": "boolop", "list_comprehension": "comprehension", "set_comprehension": "comprehension",
               "dictionary_comprehension": "comprehension", "generator_expression": "comprehension", "if_clause": "comp_if",
               "try_statement": "try", "finally_clause": "finally", "with_statement": "with", "named_expression": "walrus",
               "lambda": "lambda", "function_definition": "nested_def", "class_definition": "nested_class", "not_operator": "not",
               "parenthesized_expression": "paren", "for_in_clause": "comp_for"},
    "java": {"if_statement": "if", "ternary_expression": "ternary", "switch_expression": "switch", "for_statement": "for",
             "enhanced_for_statement": "for", "while_statement": "while", "do_statement": "while", "catch_clause": "catch",
             "try_statement": "try", "try_with_resources_statement": "try", "finally_clause": "finally", "binary_expression": "binexpr",
             "lambda_expression": "lambda", "class_body": "anon_class", "labeled_statement": "label", "break_statement": "break",
             "continue_statement": "continue", "switch_block": "switch_block", "parenthesized_expression": "paren", "unary_expression": "unary"},
    "javascript": {"if_statement": "if", "else_clause": "else", "ternary_expression": "ternary", "switch_statement": "switch",
                   "for_statement": "for", "for_in_statement": "for", "while_statement": "while", "do_statement": "while",
                   "catch_clause": "catch", "try_statement": "try", "finally_clause": "finally", "binary_expression": "binexpr",
                   "arrow_function": "lambda", "function_expression": "nested_fn", "function_declaration": "nested_fn", "function": "nested_fn",
                   "labeled_statement": "label", "break_statement": "break", "continue_statement": "continue", "parenthesized_expression": "paren",
                   "unary_expression": "unary", "jsx_element": "jsx", "jsx_self_closing_element": "jsx", "member_expression": "member", "optional_chain": "optchain"},
    "go": {"if_statement": "if", "for_statement": "for", "expression_switch_statement": "switch", "type_switch_statement": "switch",
           "select_statement": "select", "binary_expression": "binexpr", "func_literal": "lambda", "labeled_statement": "label",
           "break_statement": "break", "continue_statement": "continue", "goto_statement": "goto", "parenthesized_expression": "paren",
           "unary_expression": "unary", "go_statement": "go", "defer_statement": "defer"},
}
FEATURES["typescript"] = dict(FEATURES["javascript"])

@dataclasses.dataclass
class FunctionUnit:
    file: str
    lang: str
    kind: str
    name: str
    qualified_name: str
    decl_line: int
    name_line: int
    body_line: int
    end_line: int
    depth: int
    parent_idx: int | None
    class_name: str | None
    has_nested: bool = False
    nested_count: int = 0
    features: dict = dataclasses.field(default_factory=dict)
    idx: int = -1
    logical_ops: dict = dataclasses.field(default_factory=dict)  # counts of && / || / and / or / ?? tokens
    recursion_direct: bool = False
    recursion_calls: int = 0  # textual count of `name(` inside the body (0 when not recursive)
    recursion_method: bool = False  # recursion through a receiver: self./this./cls./super./<receiver>.name(
    source_hash: str = ""
    has_body: bool = True  # False for abstract/interface methods and overload signatures (no body block)

def lang_of(path: str) -> str | None:
    suf = pathlib.Path(path).suffix.lower()
    for lang, exts in LANG_EXT.items():
        if suf in exts:
            return lang
    return None

def _name_of(node, lang):
    n = node.child_by_field_name("name")
    if n is not None:
        return n.text.decode("utf-8", "replace"), n.start_point[0] + 1
    # javascript arrow/function_expression assigned to a variable or property
    p = node.parent
    if lang in ("javascript", "typescript") and p is not None:
        if p.type in ("variable_declarator",):
            nm = p.child_by_field_name("name")
            if nm is not None:
                return nm.text.decode("utf-8", "replace"), nm.start_point[0] + 1
        if p.type in ("pair", "assignment_expression", "public_field_definition", "property_definition"):
            key = p.child_by_field_name("key") or p.child_by_field_name("left") or p.child_by_field_name("name")
            if key is not None:
                return key.text.decode("utf-8", "replace"), key.start_point[0] + 1
    return "<anonymous>", node.start_point[0] + 1

def _body_line(node, lang):
    b = node.child_by_field_name("body")
    if b is not None:
        return b.start_point[0] + 1
    return node.start_point[0] + 1

def _count_features(node, lang, stop_types):
    """Count feature node types inside `node` but not inside nested function-like nodes (except counting them)."""
    feats = {}
    ops = {}
    def rec(n):
        for c in n.children:
            if not c.is_named:
                continue
            f = FEATURES[lang].get(c.type)
            if f:
                feats[f] = feats.get(f, 0) + 1
            if lang in ("java", "go") and c.type == "if_statement":  # else / else-if live in the `alternative` field
                alt = c.child_by_field_name("alternative")
                if alt is not None:
                    k = "elif" if alt.type == "if_statement" else "else"
                    feats[k] = feats.get(k, 0) + 1
            if lang == "python" and c.type == "for_statement" and any(ch.type == "async" for ch in c.children):
                feats["async_for"] = feats.get("async_for", 0) + 1
            if c.type == "parenthesized_expression":
                # parenthesised sub-expression inside a boolean sequence or under a negation (the R15 construct)
                pop_ = n.child_by_field_name("operator") if n.type in ("binary_expression", "unary_expression") else None
                ptxt = pop_.text.decode("utf-8", "replace") if pop_ is not None else ""
                if n.type in ("boolean_operator", "not_operator") or (n.type == "binary_expression" and ptxt in ("&&", "||", "and", "or")) or (n.type == "unary_expression" and ptxt in ("!", "not")):
                    feats["paren_bool"] = feats.get("paren_bool", 0) + 1
            if lang == "go" and c.type == "if_statement":
                cond = c.child_by_field_name("condition")
                if cond is not None and cond.type == "binary_expression":
                    op = cond.child_by_field_name("operator"); l = cond.child_by_field_name("left"); r = cond.child_by_field_name("right")
                    if op is not None and op.text in (b"!=", b"==") and ((l is not None and l.type == "nil") or (r is not None and r.type == "nil")):
                        feats["if_nil_check"] = feats.get("if_nil_check", 0) + 1
            if c.type in ("binary_expression", "boolean_operator"):
                op = c.child_by_field_name("operator")
                if op is not None:
                    t = op.text.decode("utf-8", "replace")
                    if t in ("&&", "||", "and", "or", "??"):
                        ops[t] = ops.get(t, 0) + 1
            if c.type in stop_types:
                continue  # do not descend into nested function-like units
            rec(c)
    rec(node)
    return feats, ops

def enumerate_functions(path: str, source: bytes | None = None, lang: str | None = None) -> list[FunctionUnit]:
    lang = lang or lang_of(path)
    if lang is None:
        return []
    src = source if source is not None else pathlib.Path(path).read_bytes()
    parser = get_parser("tsx" if path.lower().endswith(".tsx") else lang)
    tree = parser.parse(src)
    fn_types = FUNCTION_NODES[lang]
    units: list[FunctionUnit] = []
    def walk(node, depth, parent_idx, class_stack, qual_stack):
        for c in node.children:
            if not c.is_named:
                continue
            if c.type in fn_types:
                name, name_line = _name_of(c, lang)
                qual = ".".join(qual_stack + [name])
                decl_start = c.start_point[0] + 1
                if lang == "python" and node.type == "decorated_definition":
                    decl_start = node.start_point[0] + 1  # include decorator lines in the header span
                if lang in ("javascript", "typescript") and c.type == "method_definition":
                    sib = c.prev_named_sibling  # TS decorators precede the method as sibling nodes in the class body
                    while sib is not None and sib.type == "decorator":
                        decl_start = sib.start_point[0] + 1; sib = sib.prev_named_sibling
                u = FunctionUnit(file=path, lang=lang, kind=fn_types[c.type], name=name, qualified_name=qual,
                                 decl_line=decl_start, name_line=name_line, body_line=_body_line(c, lang),
                                 end_line=c.end_point[0] + 1, depth=depth, parent_idx=parent_idx,
                                 class_name=class_stack[-1] if class_stack else None)
                u.idx = len(units)
                body_node = c.child_by_field_name("body")
                if lang in ("java", "javascript", "typescript", "go") and body_node is None:
                    u.has_body = False
                units.append(u)
                feats, ops = _count_features(c, lang, set(fn_types))
                u.features = feats; u.logical_ops = ops
                # direct recursion: identifier equal to own name called inside body (cheap textual check)
                body = c.child_by_field_name("body")
                if body is not None and name not in ("<anonymous>",):
                    txt = body.text
                    nb = re.escape(name.encode())
                    u.recursion_calls = len(re.findall(rb"(?<![A-Za-z0-9_$])" + nb + rb"\s*\(", txt))
                    u.recursion_direct = u.recursion_calls > 0
                    recv = b""
                    if lang == "go" and c.type == "method_declaration":
                        rp = c.child_by_field_name("receiver")
                        if rp is not None:
                            for pd in rp.named_children:
                                nm = pd.child_by_field_name("name")
                                if nm is not None:
                                    recv = re.escape(nm.text); break
                    recv_alt = rb"(?:self|this|cls|super" + (rb"|" + recv if recv else rb"") + rb")"
                    u.recursion_method = re.search(recv_alt + rb"\s*\.\s*" + nb + rb"\s*\(", txt) is not None
                walk(c, depth + 1, u.idx, class_stack, qual_stack + [name])
                if parent_idx is not None:
                    units[parent_idx].has_nested = True
                    units[parent_idx].nested_count += 1
            elif c.type in CLASS_NODES[lang] or (lang == "java" and c.type == "class_body" and node.type == "object_creation_expression"):
                cn = c.child_by_field_name("name")
                cname = cn.text.decode("utf-8", "replace") if cn is not None else "<anon>"
                # Java anonymous class bodies inside a method: methods inside count as nested units of that method
                walk(c, depth, parent_idx, class_stack + [cname], qual_stack + [cname] if cn is not None else qual_stack)
            else:
                walk(c, depth, parent_idx, class_stack, qual_stack)
    walk(tree.root_node, 0, None, [], [])
    # propagate has_nested up the chain (grandchildren)
    for u in units:
        p = u.parent_idx
        while p is not None:
            units[p].has_nested = True
            p = units[p].parent_idx
    return units

def iter_source_files(root: str, lang: str, exclude_dirs=("node_modules", "vendor", "third_party", "thirdparty", "dist", "build", ".git",
                                                            "site-packages", "venv", ".venv", "__pycache__", "testdata", "fixtures",
                                                            "__snapshots__", "generated", "gen", ".sonar_empty_bin", ".scannerwork")) -> Iterator[str]:
    root_p = pathlib.Path(root)
    exts = LANG_EXT[lang] if lang != "javascript" else LANG_EXT["javascript"] | LANG_EXT["typescript"]
    for p in sorted(root_p.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        rel = p.relative_to(root_p)
        if any(part in exclude_dirs or part.startswith(".") for part in rel.parts[:-1]):
            continue
        if any(m in p.name for m in (".min.js", ".min.ts", ".d.ts", "_pb2.py", ".pb.go", "_generated", ".generated.")):
            continue
        yield str(p)
