// Node adapter: per-function Cognitive Complexity from four JS/TS implementations.
// Usage: node src/js_cc.mjs <tool> <file-list.txt> > out.json
//   tool in: cogplexity | oxlint | maintainability | sonarjs421
// Each output row: {file, name, line, endLine, value, tool, extra}
// Runs from the tools/node package so that the packages resolve.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const NODE_DIR = path.resolve(here, "..", "tools", "node");
const require = createRequire(path.join(NODE_DIR, "package.json"));

const [tool, listFile] = process.argv.slice(2);
const files = fs.readFileSync(listFile, "utf8").split(/\r?\n/).filter(Boolean);
const rows = [];
const errors = [];

function isTS(f) { return /\.(ts|tsx|mts|cts)$/i.test(f); }
function isJSX(f) { return /\.(jsx|tsx)$/i.test(f); }

async function parseWithTsEslint(file, code) {
  const parser = require("@typescript-eslint/parser");
  const res = parser.parseForESLint(code, {
    ecmaVersion: "latest", sourceType: "module", range: true, loc: true, tokens: false, comment: false,
    ecmaFeatures: { jsx: isJSX(file) || /\.js$/i.test(file) }, filePath: file, jsDocParsingMode: "none",
  });
  return res;
}

function addParents(node, parent) {
  if (!node || typeof node !== "object") return;
  if (Array.isArray(node)) { for (const n of node) addParents(n, parent); return; }
  if (typeof node.type !== "string") return;
  node.parent = parent;
  for (const k of Object.keys(node)) {
    if (k === "parent" || k === "loc" || k === "range") continue;
    const v = node[k];
    if (v && typeof v === "object") addParents(v, node);
  }
}

function functionName(node) {
  if (node.id && node.id.name) return node.id.name;
  const p = node.parent;
  if (!p) return "<anonymous>";
  if (p.type === "VariableDeclarator" && p.id && p.id.name) return p.id.name;
  if (p.type === "Property" && p.key) return p.key.name || (p.key.value != null ? String(p.key.value) : "<anonymous>");
  if ((p.type === "MethodDefinition" || p.type === "PropertyDefinition") && p.key) return p.key.name || String(p.key.value ?? "<anonymous>");
  if (p.type === "AssignmentExpression" && p.left) return p.left.name || (p.left.property && p.left.property.name) || "<anonymous>";
  return "<anonymous>";
}

async function runCogplexity(file, code) {
  const { score } = await import(pathToFileURL(path.join(NODE_DIR, "node_modules", "cogplexity", "src", "score.js")).href);
  const res = await parseWithTsEslint(file, code);
  const out = score(res.ast, code, { scopeManager: res.scopeManager });
  for (const f of out.functions) {
    rows.push({ file, tool: "cogplexity", name: f.name || "<anonymous>", line: f.loc.start.line, nameLine: f.nameLoc ? f.nameLoc.start.line : f.loc.start.line,
      endLine: f.loc.end.line, value: f.score, extra: { depth: f.depth, parent: f.parent, nesting: f.nesting,
        increments: f.increments.map(i => ({ c: i.construct, a: i.amount, n: i.nesting, l: i.loc.start.line, op: i.operator })) } });
  }
}

async function runOxlint(file, code) {
  const { analyzeFileComplexity } = await import(pathToFileURL(path.join(NODE_DIR, "node_modules", "oxlint-plugin-complexity", "dist", "standalone.js")).href);
  const out = analyzeFileComplexity(code, file);
  for (const f of out.functions) {
    rows.push({ file, tool: "oxlint-plugin-complexity", name: f.name || "<anonymous>", line: f.startLine, endLine: f.endLine, value: f.cognitive,
      extra: { cyclomatic: f.cyclomatic, points: (f.cognitivePoints || []).slice(0, 60) } });
  }
}

async function runMaintainability(file, code) {
  // Use the rule's own traversal with a fake context so that maxComplexity can be 0 (the ESLint schema forbids 0).
  const mod = require(path.join(NODE_DIR, "node_modules", "eslint-plugin-maintainability", "src", "rules", "maintainability", "cognitive-complexity.js"));
  const rule = mod.cognitiveComplexity || mod.default || mod;
  const parser = require("@typescript-eslint/parser");
  const res = parser.parseForESLint(code, { ecmaVersion: "latest", sourceType: "module", range: true, loc: true, tokens: true, comment: true,
    ecmaFeatures: { jsx: isJSX(file) || /\.js$/i.test(file) }, filePath: file, jsDocParsingMode: "none" });
  addParents(res.ast, null);
  const reports = [];
  const { SourceCode } = require("eslint");
  const sc = new SourceCode({ text: code, ast: res.ast, scopeManager: res.scopeManager, visitorKeys: res.visitorKeys, parserServices: res.services });
  const ctx = { options: [{ maxComplexity: 0, includeMetrics: false }], filename: file, physicalFilename: file, cwd: path.dirname(file),
    report: (r) => reports.push(r), getFilename: () => file, getPhysicalFilename: () => file, sourceCode: sc, getSourceCode: () => sc, settings: {}, parserOptions: {}, languageOptions: {} };
  const visitor = rule.create(ctx);
  function walk(n) {
    if (!n || typeof n !== "object" || typeof n.type !== "string") return;
    const h = visitor[n.type];
    if (h) h(n);
    for (const k of Object.keys(n)) {
      if (k === "parent" || k === "loc" || k === "range") continue;
      const v = n[k];
      if (Array.isArray(v)) v.forEach(walk); else if (v && typeof v === "object" && typeof v.type === "string") walk(v);
    }
  }
  walk(res.ast);
  for (const r of reports) {
    const node = r.node;
    rows.push({ file, tool: "eslint-plugin-maintainability", name: functionName(node), line: node.loc.start.line, endLine: node.loc.end.line,
      value: Number(r.data.complexity), extra: { conditionals: r.data.conditionals, loops: r.data.loops, nesting: r.data.nesting } });
  }
}

async function runSonarjs421(file, code) {
  // eslint-plugin-sonarjs 4.2.1 (archived snapshot of SonarJS's S3776 rule) via the ESLint Linter with threshold 0.
  const { Linter } = require("eslint");
  const sonarjs = require("eslint-plugin-sonarjs");
  const tsParser = require("@typescript-eslint/parser");
  const linter = new Linter({ configType: "flat", cwd: path.dirname(file) });
  const cfg = [{ files: ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs", "**/*.ts", "**/*.tsx", "**/*.mts", "**/*.cts"], plugins: { sonarjs }, languageOptions: { parser: tsParser, parserOptions: { ecmaVersion: "latest", sourceType: "module", ecmaFeatures: { jsx: isJSX(file) || /\.js$/i.test(file) } } },
    rules: { "sonarjs/cognitive-complexity": ["error", 0] } }];
  const msgs = linter.verify(code, cfg, { filename: path.basename(file) });
  if (process.env.JSCC_DEBUG) console.error(JSON.stringify(msgs).slice(0, 2000));
  for (const m of msgs) {
    if (m.ruleId !== "sonarjs/cognitive-complexity") { if (m.fatal) errors.push({ file, msg: m.message }); continue; }
    let value = null, secondaries = null;
    try { const j = JSON.parse(m.message); value = j.cost ?? null; secondaries = (j.secondaryLocations || []).map(s => ({ l: s.line, m: s.message }));
      if (value == null) { const mm = /from (\d+) to the/.exec(j.message || ""); if (mm) value = Number(mm[1]); } }
    catch { const mm = /from (\d+) to the/.exec(m.message); if (mm) value = Number(mm[1]); }
    rows.push({ file, tool: "eslint-plugin-sonarjs-4.2.1", name: "", line: m.line, endLine: m.endLine, value, extra: { secondaries } });
  }
}

const runners = { cogplexity: runCogplexity, oxlint: runOxlint, maintainability: runMaintainability, sonarjs421: runSonarjs421 };
if (!runners[tool]) { console.error("unknown tool " + tool); process.exit(2); }
for (const file of files) {
  let code;
  try { code = fs.readFileSync(file, "utf8"); } catch (e) { errors.push({ file, msg: String(e) }); continue; }
  try { await runners[tool](file, code); } catch (e) { errors.push({ file, msg: String(e && e.message || e).slice(0, 300) }); }
}
process.stdout.write(JSON.stringify({ tool, rows, errors }));
