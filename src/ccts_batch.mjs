// Batch driver for cognitive-complexity-ts: one node process for all files (its CLI handles a single file only).
// Usage: node src/ccts_batch.mjs <file-list.txt>  -> JSON {results: {absPath: fileOutput}, errors: [{file, msg}]}
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const NODE_DIR = path.resolve(here, "..", "tools", "node");
const require = createRequire(path.join(NODE_DIR, "package.json"));
const { getFileOutput } = require("cognitive-complexity-ts/build/src/cognitive-complexity/output.js");
const files = fs.readFileSync(process.argv[2], "utf8").split(/\r?\n/).filter(Boolean);
const results = {}; const errors = [];
for (const f of files) {
  try {
    results[f] = await getFileOutput(f);
  } catch (e) {
    errors.push({ file: f, msg: String(e && e.message || e).slice(0, 300) });
  }
}
process.stdout.write(JSON.stringify({ results, errors }));
