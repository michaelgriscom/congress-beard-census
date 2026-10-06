// Rebuilds the data embedded in beard-cohort-chart.html: facial-hair style
// shares by 5-year birth group, for every man who served in Congress.
//
//   node charts/cohort-data.mjs > cohort.json

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const file = join(dirname(fileURLToPath(import.meta.url)), "..", "data", "facial_hair_census.csv");
const [header, ...lines] = readFileSync(file, "utf8").trim().split(/\r?\n/);
const cols = header.split(",");
const STYLES = ["full_beard", "goatee_mustache", "beard_no_mustache", "sideburns", "mustache", "clean"];

const groups = new Map();
for (const line of lines) {
  const r = Object.fromEntries(line.split(",").map((v, i) => [cols[i], v]));
  if (r.gender !== "M" || !r.congress_terms || !r.birth_year || !STYLES.includes(r.facial_hair)) continue;
  const bin = Math.floor(Number(r.birth_year) / 5) * 5;
  const counts = groups.get(bin) ?? {};
  counts[r.facial_hair] = (counts[r.facial_hair] ?? 0) + 1;
  groups.set(bin, counts);
}

const data = [];
for (let bin = 1770; bin <= 1880; bin += 5) {
  const counts = groups.get(bin) ?? {};
  const n = Object.values(counts).reduce((a, b) => a + b, 0);
  const row = { birth: bin + 2.5, n };
  for (const s of STYLES) row[s] = Math.round(((counts[s] ?? 0) / n) * 1e4) / 1e4;
  data.push(row);
}
console.log(JSON.stringify(data));
