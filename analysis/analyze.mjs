// How surprising is it that every full-bearded U.S. president was born in Ohio?
// Runs a handful of probability models over the CSVs in ./data.
//
//   node analysis/analyze.mjs

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DATA = join(dirname(fileURLToPath(import.meta.url)), "..", "data");

function readCsv(name) {
  const [header, ...rows] = readFileSync(join(DATA, name), "utf8")
    .trim()
    .split(/\r?\n/)
    .map(line => line.split(","));
  return rows.map(r => Object.fromEntries(header.map((h, i) => [h, r[i]])));
}

const presidents = readCsv("presidents.csv").map(p => ({
  ...p,
  took_office: Number(p.took_office),
  left_office: p.left_office ? Number(p.left_office) : 9999,
  birth_year: Number(p.birth_year),
}));
const nominees = readCsv("nominees_1856_1916.csv");
const census = readCsv("state_population_1790_1920.csv");
const robinson = new Map(
  readCsv("robinson_facial_hair_1842_1972.csv").map(r => [Number(r.year), r])
);

const ABBR = {
  Alabama: "AL",
  Alaska: "AK",
  Arizona: "AZ",
  Arkansas: "AR",
  California: "CA",
  Colorado: "CO",
  Connecticut: "CT",
  Delaware: "DE",
  "District of Columbia": "DC",
  Florida: "FL",
  Georgia: "GA",
  Hawaii: "HI",
  Idaho: "ID",
  Illinois: "IL",
  Indiana: "IN",
  Iowa: "IA",
  Kansas: "KS",
  Kentucky: "KY",
  Louisiana: "LA",
  Maine: "ME",
  Maryland: "MD",
  Massachusetts: "MA",
  Michigan: "MI",
  Minnesota: "MN",
  Mississippi: "MS",
  Missouri: "MO",
  Montana: "MT",
  Nebraska: "NE",
  Nevada: "NV",
  "New Hampshire": "NH",
  "New Jersey": "NJ",
  "New Mexico": "NM",
  "New York": "NY",
  "North Carolina": "NC",
  "North Dakota": "ND",
  Ohio: "OH",
  Oklahoma: "OK",
  Oregon: "OR",
  Pennsylvania: "PA",
  "Rhode Island": "RI",
  "South Carolina": "SC",
  "South Dakota": "SD",
  Tennessee: "TN",
  Texas: "TX",
  Utah: "UT",
  Vermont: "VT",
  Virginia: "VA",
  Washington: "WA",
  "West Virginia": "WV",
  Wisconsin: "WI",
  Wyoming: "WY",
};

// ---------- helpers ----------

const pct = (x, d = 1) => `${(100 * x).toFixed(d)}%`;
const oneIn = x => `1 in ${Math.round(1 / x).toLocaleString("en-US")}`;
const isFullBeard = p => p.facial_hair === "full_beard";
const isAnyBeard = p => ["full_beard", "chin_beard"].includes(p.facial_hair);

function choose(n, k) {
  if (k < 0 || k > n) return 0;
  let r = 1;
  for (let i = 1; i <= k; i++) r = (r * (n - k + i)) / i;
  return r;
}

// P(X >= k) for X ~ Hypergeometric(population N, K successes, n draws).
// This is the one-sided Fisher exact test p-value for a 2x2 table.
function hypergeomTail(N, K, n, k) {
  let p = 0;
  for (let x = k; x <= Math.min(K, n); x++)
    p += (choose(K, x) * choose(N - K, n - x)) / choose(N, n);
  return p;
}

function binomTail(n, p, k) {
  let s = 0;
  for (let x = k; x <= n; x++) s += choose(n, x) * p ** x * (1 - p) ** (n - x);
  return s;
}

// State population shares for a census year. West Virginia is folded into
// Virginia before 1863 and Maine into Massachusetts before 1820, so births are
// attributed to the state that existed at the time.
function stateShares(year, field) {
  const byState = {};
  for (const r of census) {
    if (Number(r.census_year) !== year) continue;
    let s = ABBR[r.state];
    if (s === "WV" && year < 1863) s = "VA";
    if (s === "ME" && year < 1820) s = "MA";
    byState[s] = (byState[s] ?? 0) + Number(r[field] || 0);
  }
  const total = Object.values(byState).reduce((a, b) => a + b, 0);
  return Object.fromEntries(
    Object.entries(byState).map(([s, v]) => [s, v / total])
  );
}

// Linear interpolation between the censuses bracketing `year`.
function sharesAt(year, field) {
  const lo = Math.max(1790, Math.floor(year / 10) * 10);
  const hi = Math.min(1920, lo + 10);
  const a = stateShares(lo, field);
  const b = stateShares(hi, field);
  const t = hi === lo ? 0 : (year - lo) / (hi - lo);
  const states = new Set([...Object.keys(a), ...Object.keys(b)]);
  return Object.fromEntries(
    [...states].map(s => [s, (1 - t) * (a[s] ?? 0) + t * (b[s] ?? 0)])
  );
}

const beardRate = year => Number(robinson.get(year)?.beard_pct) / 100;

function section(title) {
  console.log(`\n## ${title}\n`);
}

// ---------- 0. The facts ----------

section("0. The bearded presidents");
for (const p of presidents.filter(isAnyBeard))
  console.log(
    `${p.name.padEnd(22)} ${p.facial_hair.padEnd(11)} born ${p.birth_state}, ` +
      `elected from ${p.home_state}, took office ${p.took_office}`
  );

const fullBeards = presidents.filter(isFullBeard);

// ---------- 1. Ohio's weight in the country ----------

section("1. Ohio's share of the U.S. population (census)");
console.log("year  total  white  rank(by total)");
for (let y = 1800; y <= 1920; y += 10) {
  const t = stateShares(y, "total_population");
  const w = stateShares(y, "white_population");
  const rank =
    Object.entries(t)
      .sort((a, b) => b[1] - a[1])
      .findIndex(([s]) => s === "OH") + 1;
  console.log(
    `${y}  ${pct(t.OH).padStart(5)}  ${pct(w.OH).padStart(5)}  #${rank}`
  );
}

// ---------- 2. Naive birth lottery ----------

section(
  "2. Naive birth lottery: each bearded president drawn from his birth cohort"
);
let naiveTotal = 1;
let naiveWhite = 1;
for (const p of fullBeards) {
  const t = sharesAt(p.birth_year, "total_population").OH;
  const w = sharesAt(p.birth_year, "white_population").OH;
  naiveTotal *= t;
  naiveWhite *= w;
  console.log(
    `${p.name.padEnd(22)} born ${p.birth_year}: Ohio = ${pct(t)} of all, ${pct(w)} of white Americans`
  );
}
console.log(
  `\nP(all 4 Ohio) using total population: ${naiveTotal.toExponential(2)} (${oneIn(naiveTotal)})`
);
console.log(
  `P(all 4 Ohio) using white population: ${naiveWhite.toExponential(2)} (${oneIn(naiveWhite)})`
);

// ---------- 3. Look-elsewhere correction ----------

section("3. Look-elsewhere: P(all 4 born in the SAME state, any state)");
const cohort = fullBeards.map(p => sharesAt(p.birth_year, "white_population"));
const sameState = {};
for (const s of Object.keys(cohort[0]))
  sameState[s] = cohort.reduce((acc, shares) => acc * (shares[s] ?? 0), 1);
const anyState = Object.values(sameState).reduce((a, b) => a + b, 0);
console.log(
  `P(any single state) = ${anyState.toExponential(2)} (${oneIn(anyState)})`
);
console.log(`Ohio's slice of that = ${pct(sameState.OH / anyState)}`);
console.log(
  "Top contributors: " +
    Object.entries(sameState)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([s, v]) => `${s} ${pct(v / anyState, 0)}`)
      .join(", ")
);

// ---------- 4. Condition on who actually became president ----------

section(
  "4. Condition on the actual presidents of the beard era (Fisher exact test)"
);
for (const [lo, hi] of [
  [1861, 1913],
  [1865, 1897],
]) {
  const era = presidents.filter(p => p.took_office < hi && p.left_office > lo);
  const ohio = era.filter(p => p.birth_state === "OH");
  for (const [label, test] of [
    ["full beard", isFullBeard],
    ["any beard (incl. Lincoln)", isAnyBeard],
  ]) {
    const bearded = era.filter(test);
    const both = bearded.filter(p => p.birth_state === "OH").length;
    // Lincoln is outside the narrower window, so "any beard" adds nothing there.
    if (test === isAnyBeard && !era.some(p => p.facial_hair === "chin_beard"))
      continue;
    const p = hypergeomTail(era.length, ohio.length, bearded.length, both);
    console.log(
      `${lo}-${hi}: ${era.length} presidents, ${ohio.length} Ohio-born, ` +
        `${bearded.length} with ${label}, ${both} of them Ohio-born -> ` +
        `P(>= ${both} Ohio by chance) = ${pct(p)} (${oneIn(p)})`
    );
  }
}

// ---------- 5. Fashion model ----------

section(
  "5. Fashion model: each president bearded with P = beard share of men that year"
);
// Robinson's "beard" category includes any chin beard, so using it as the
// probability of a *full* beard overstates beards and makes the Ohio pattern
// look more surprising, not less.
for (const [lo, hi] of [
  [1849, 1929],
  [1857, 1921],
]) {
  const pool = presidents.filter(
    p => p.took_office >= lo && p.took_office <= hi
  );
  const b = p => beardRate(p.took_office);
  const expected = pool.reduce((a, p) => a + b(p), 0);
  const states = [...new Set(pool.map(p => p.birth_state))];
  const noneOutside = s =>
    pool.filter(p => p.birth_state !== s).reduce((a, p) => a * (1 - b(p)), 1);
  const someInside = s =>
    1 -
    pool.filter(p => p.birth_state === s).reduce((a, p) => a * (1 - b(p)), 1);
  const pOhio = noneOutside("OH") * someInside("OH");
  const pAny = states.reduce((a, s) => a + noneOutside(s) * someInside(s), 0);
  console.log(
    `Presidents inaugurated ${lo}-${hi} (${pool.length} people): ` +
      `expected bearded = ${expected.toFixed(1)}, actual full beards = ${pool.filter(isFullBeard).length}`
  );
  console.log(
    `  P(every bearded president is Ohio-born)       = ${pct(pOhio)} (${oneIn(pOhio)})`
  );
  console.log(
    `  P(every bearded president shares ANY one state) = ${pct(pAny)} (${oneIn(pAny)})`
  );
}
console.log("\nBeard share (Robinson) at each beard-era inauguration:");
for (const p of presidents.filter(
  p => p.took_office >= 1857 && p.took_office <= 1913
))
  console.log(
    `  ${String(p.took_office)} ${p.name.padEnd(22)} ${p.birth_state}  ${pct(beardRate(p.took_office), 0).padStart(4)}  ${p.facial_hair}`
  );

// ---------- 6. Widen the sample: losing nominees ----------

section(
  "6. Widen the sample: major-party nominees 1856-1916 (distinct people)"
);
const people = [...new Map(nominees.map(n => [n.name, n])).values()].map(n => ({
  ...n,
  // Count a nominee's beard as of any campaign (Lincoln: chin beard by 1864).
  facial_hair: nominees.some(
    m => m.name === n.name && m.facial_hair === "full_beard"
  )
    ? "full_beard"
    : n.facial_hair,
}));
for (const [label, pool] of [
  ["All major-party nominees", people],
  ["Republican nominees only", people.filter(n => n.party === "Republican")],
]) {
  const ohio = pool.filter(n => n.birth_state === "OH");
  const bearded = pool.filter(isFullBeard);
  const both = bearded.filter(n => n.birth_state === "OH");
  const p = hypergeomTail(
    pool.length,
    ohio.length,
    bearded.length,
    both.length
  );
  console.log(
    `${label}: ${pool.length} people, ${ohio.length} Ohio-born, ${bearded.length} full beards ` +
      `(${bearded.map(n => `${n.name.split(" ").at(-1)}-${n.birth_state}`).join(", ")}), ` +
      `${both.length} Ohio-born -> P = ${pct(p)}`
  );
}

// ---------- 7. The real anomaly: Ohio's grip on the presidency ----------

section("7. Ohio's grip on the presidency, 1868-1920");
const winners = {
  1868: "Ulysses S. Grant",
  1872: "Ulysses S. Grant",
  1876: "Rutherford B. Hayes",
  1880: "James A. Garfield",
  1884: "Grover Cleveland",
  1888: "Benjamin Harrison",
  1892: "Grover Cleveland",
  1896: "William McKinley",
  1900: "William McKinley",
  1904: "Theodore Roosevelt",
  1908: "William Howard Taft",
  1912: "Woodrow Wilson",
  1916: "Woodrow Wilson",
  1920: "Warren G. Harding",
};
const elections = Object.entries(winners).map(([year, name]) => ({
  year,
  winner: presidents.find(p => p.name === name),
}));
const ohioWins = elections.filter(e => e.winner.birth_state === "OH");
console.log(
  elections
    .map(e => `${e.year} ${e.winner.name} (${e.winner.birth_state})`)
    .join("\n")
);
// Weight each election by Ohio's share of white Americans in the winner's birth
// cohort; the median winner here was born around 1840, when Ohio peaked.
const ohioShare = sharesAt(1840, "white_population").OH;
const pDyn = binomTail(elections.length, ohioShare, ohioWins.length);
console.log(
  `\nOhio-born winners: ${ohioWins.length} of ${elections.length}. If each election were a ` +
    `draw weighted by Ohio's ${pct(ohioShare)} share of white Americans (1840, near its peak): ` +
    `P(>= ${ohioWins.length}) = ${pDyn.toExponential(1)} (${oneIn(pDyn)})`
);
const allOhio = presidents.filter(p => p.birth_state === "OH").length;
console.log(
  `All-time: ${allOhio} of ${presidents.length} presidents (${pct(allOhio / presidents.length)}) were Ohio-born.`
);

// ---------- 8. The mechanism: Union generals ----------

section("8. Union generals among nominees 1856-1916 (distinct people)");
const generals = people.filter(n => n.union_general === "yes");
const nonGenerals = people.filter(n => n.union_general !== "yes");
const row = g =>
  `${g.filter(isFullBeard).length} full beard / ${g.length}  ` +
  `(${pct(g.filter(isFullBeard).length / g.length, 0)})`;
console.log(
  `Union generals: ${row(generals)}  -> ${generals.map(n => `${n.name.split(" ").at(-1)}(${n.birth_state}, ${n.facial_hair})`).join(", ")}`
);
console.log(`Everyone else:  ${row(nonGenerals)}`);
const gp = hypergeomTail(
  people.length,
  generals.length,
  people.filter(isFullBeard).length,
  generals.filter(isFullBeard).length
);
console.log(
  `Fisher one-sided P(general <-> full beard association by chance) = ${pct(gp)}`
);
const genPres = presidents.filter(p => p.union_general === "yes");
console.log(
  `Presidents who were Union Army generals: ${genPres.map(p => `${p.name} (${p.birth_state}, ${p.facial_hair})`).join("; ")}`
);

// ---------- 9. U.S. Congress beard rates (coded portraits) ----------

section("9. U.S. Congress: share of members with beards, from coded portraits");
const ANY_BEARD = ["full_beard", "beard_no_mustache", "goatee_mustache"];
const coded = readCsv("congress_facial_hair_sample.csv").filter(
  r => !["unusable", "woman", "not_downloaded"].includes(r.facial_hair)
);
const share = (rows, cats) => [
  rows.filter(r => cats.includes(r.facial_hair)).length,
  rows.length,
];
// Two-sided Fisher exact test: sum of all tables no likelier than the observed one.
function fisherTwoSided([k1, n1], [k2, n2]) {
  const N = n1 + n2;
  const K = k1 + k2;
  const p = x => (choose(K, x) * choose(N - K, n1 - x)) / choose(N, n1);
  const p0 = p(k1);
  let total = 0;
  for (let x = Math.max(0, n1 - (N - K)); x <= Math.min(K, n1); x++)
    if (p(x) <= p0 * (1 + 1e-9)) total += p(x);
  return total;
}
const fmt = ([k, n]) => `${k}/${n} (${pct(k / n, 0)})`;

console.log("year  n   full beard  any beard  mustache only  clean-shaven");
for (const year of [...new Set(coded.map(r => r.snapshot_year))]) {
  const rows = coded.filter(
    r => r.snapshot_year === year && r.sample === "random"
  );
  const [full, n] = share(rows, ["full_beard"]);
  const [any] = share(rows, ANY_BEARD);
  const [mus] = share(rows, ["mustache"]);
  const [clean] = share(rows, ["clean"]);
  console.log(
    `${year}  ${String(n).padEnd(3)} ${pct(full / n, 0).padStart(6)}     ${pct(any / n, 0).padStart(6)}     ` +
      `${pct(mus / n, 0).padStart(6)}        ${pct(clean / n, 0).padStart(6)}`
  );
}

const era = r => r.snapshot_year >= "1856" && r.snapshot_year <= "1896";
const rep = share(
  coded.filter(
    r => era(r) && r.sample === "random" && r.party === "Republican"
  ),
  ["full_beard"]
);
const dem = share(
  coded.filter(r => era(r) && r.sample === "random" && r.party === "Democrat"),
  ["full_beard"]
);
console.log(
  `\nFull beards 1856-1896: Republicans ${fmt(rep)}, Democrats ${fmt(dem)}; ` +
    `two-sided Fisher p = ${fisherTwoSided(rep, dem).toFixed(3)}`
);

const ohioEra = r => r.snapshot_year >= "1856" && r.snapshot_year <= "1906";
const ohioRows = coded.filter(r => ohioEra(r) && r.state === "OH");
const others = coded.filter(
  r => ohioEra(r) && r.sample === "random" && r.state !== "OH"
);
const oh = share(ohioRows, ["full_beard"]);
const ot = share(others, ["full_beard"]);
console.log(
  `Full beards 1856-1906: Ohio members ${fmt(oh)}, everyone else ${fmt(ot)}; ` +
    `two-sided Fisher p = ${fisherTwoSided(oh, ot).toFixed(2)}`
);
const ohR = share(
  ohioRows.filter(
    r =>
      r.party === "Republican" &&
      r.snapshot_year >= "1866" &&
      r.snapshot_year <= "1896"
  ),
  ["full_beard"]
);
const otR = share(
  others.filter(
    r =>
      r.party === "Republican" &&
      r.snapshot_year >= "1866" &&
      r.snapshot_year <= "1896"
  ),
  ["full_beard"]
);
console.log(
  `Republicans only, 1866-1896: Ohio ${fmt(ohR)}, others ${fmt(otR)}; ` +
    `two-sided Fisher p = ${fisherTwoSided(ohR, otR).toFixed(2)}`
);

// ---------- 10. Birth lottery using where people were actually born ----------

section(
  "10. Birth lottery by state of birth (1870/1880 census nativity tables)"
);
// Each president's odds are the state's share of the native-born population
// (everyone born in the U.S., wherever they lived) in the census nearest his
// election: 1870 for Grant (1868), 60% of the way to 1880 for Hayes (1876),
// and 1880 for Garfield (1880) and Harrison (1888). Territories, DC, people
// born at sea and the 1870 "not stated" stay in the denominator; dropping them
// moves the answer by under 4%.
const born = readCsv("born_in_state_1870_1880.csv").map(r => ({
  place: r.birthplace,
  y1870: Number(r.born_1870_total),
  y1880: Number(r.born_1880_total),
}));
const total = key => born.reduce((acc, r) => acc + r[key], 0);
const [t1870, t1880] = [total("y1870"), total("y1880")];
const weights = [0, 0.6, 1, 1]; // weight on 1880 for Grant, Hayes, Garfield, Harrison
const byPlace = born
  .map(r => {
    const shares = weights.map(
      w => (1 - w) * (r.y1870 / t1870) + w * (r.y1880 / t1880)
    );
    return { ...r, shares, all4: shares.reduce((a, b) => a * b, 1) };
  })
  .sort((a, b) => b.all4 - a.all4);
const sum = byPlace.reduce((acc, r) => acc + r.all4, 0);
const ohio = byPlace.find(r => r.place === "Ohio");
console.log(
  `Ohio's share of the native-born, per president: ${ohio.shares.map(s => pct(s)).join(" / ")}`
);
console.log(`P(all 4 born in Ohio) = ${oneIn(ohio.all4)}`);
console.log(`P(all 4 born in the same state, any state) = ${oneIn(sum)}`);
console.log(`Ohio's slice of that = ${pct(ohio.all4 / sum)}`);
console.log(
  "Top contributors: " +
    byPlace
      .slice(0, 5)
      .map(r => `${r.place} ${pct(r.all4 / sum, 0)}`)
      .join(", ")
);

// ---------- 11. Full portrait census and the presidents' beard odds ----------

section("11. Portrait census (men in Congress) and the odds for presidents");
// Every member of Congress and governor with a Wikimedia portrait, coded blind.
const terms = s =>
  s
    ? s.split(";").map(t => {
        const [span, state, party, chamber] = t.split(":");
        const [start, end] = span.split("-").map(Number);
        return { start, end, state, party, chamber };
      })
    : [];
const members = readCsv("facial_hair_census.csv")
  .filter(
    r => r.gender === "M" && !["unusable", "woman"].includes(r.facial_hair)
  )
  .map(r => ({
    ...r,
    birth_year: Number(r.birth_year) || null,
    congress: terms(r.congress_terms),
  }))
  .filter(r => r.congress.length);
const serving = (from, to) =>
  members.filter(m => m.congress.some(t => t.start <= to && t.end >= from));
const fullShare = rows => [rows.filter(isFullBeard).length, rows.length];

console.log("year  men coded  full beard");
for (const year of [1825, 1849, 1861, 1869, 1881, 1893, 1905, 1921, 2025]) {
  const [k, n] = fullShare(serving(year, year));
  console.log(`${year}  ${String(n).padStart(9)}  ${pct(k / n, 0)}`);
}

console.log("\nFull beard by birth decade, men serving 1865-1889:");
const era1865 = serving(1865, 1889);
for (let decade = 1800; decade <= 1850; decade += 10) {
  const [k, n] = fullShare(
    era1865.filter(m => m.birth_year >= decade && m.birth_year < decade + 10)
  );
  console.log(`  ${decade}s: ${pct(k / n, 0)} of ${n}`);
}

// Union generals, coded on the same contact sheets as Congress controls.
const genRows = readCsv("union_generals_facial_hair.csv").filter(
  r => !["unusable", "woman"].includes(r.facial_hair)
);
const gens = fullShare(genRows.filter(r => r.group === "union_general"));
const ctrl = fullShare(genRows.filter(r => r.group !== "union_general"));
const odds = ([k, n]) => k / (n - k);
const generalOddsRatio = odds(gens) / odds(ctrl);
console.log(
  `\nUnion generals ${fmt(gens)} vs Congress 1861-1869 controls ${fmt(ctrl)}; ` +
    `two-sided Fisher p = ${fisherTwoSided(gens, ctrl).toExponential(1)}; ` +
    `odds ratio ${generalOddsRatio.toFixed(2)}`
);
const ohioGens = fullShare(
  genRows.filter(r => r.group === "union_general" && r.birth_state === "Ohio")
);
const otherGens = fullShare(
  genRows.filter(
    r =>
      r.group === "union_general" && r.birth_state && r.birth_state !== "Ohio"
  )
);
console.log(
  `Ohio-born generals ${fmt(ohioGens)} vs others ${fmt(otherGens)}; ` +
    `p = ${fisherTwoSided(ohioGens, otherGens).toFixed(3)}`
);

// P(at least 3 full beards among the presidents, all born in one state).
// Each president is bearded independently with probability p.
function atLeast(ps, k) {
  let dist = [1];
  for (const p of ps) {
    const next = new Array(dist.length + 1).fill(0);
    dist.forEach((v, i) => {
      next[i] += v * (1 - p);
      next[i + 1] += v * p;
    });
    dist = next;
  }
  return dist.slice(k).reduce((a, b) => a + b, 0);
}
function sameStateOdds(ps) {
  let total = 0;
  for (const state of new Set(ps.map(p => p.state))) {
    const inside = ps.filter(p => p.state === state).map(p => p.p);
    const outside = ps.filter(p => p.state !== state);
    total +=
      outside.reduce((acc, p) => acc * (1 - p.p), 1) * atLeast(inside, 3);
  }
  return total;
}
const beardEra = presidents.filter(
  p => p.took_office >= 1849 && p.took_office <= 1929
);
const byYear = p => fullShare(serving(p.took_office, p.took_office));
// Men born within 5 years of the president, serving within 4 years of his
// inauguration (with a half-count of smoothing).
const byGeneration = p => {
  const [k, n] = fullShare(
    serving(p.took_office - 4, p.took_office + 4).filter(
      m => m.birth_year && Math.abs(m.birth_year - p.birth_year) <= 5
    )
  );
  return [k + 0.5, n + 1];
};
// Age-adjusted generals odds ratio (Mantel-Haenszel by birth decade), from
// analysis/followups/analyses.py. The generation model already adjusts each
// president for age, so this is the ratio the post uses.
const AGE_ADJUSTED_GENERAL_ODDS_RATIO = 2.11;
const boost = (p, ratio = generalOddsRatio) => {
  const o = (p / (1 - p)) * ratio;
  return o / (1 + o);
};
const model = (rate, generals, ratio) =>
  beardEra.map(p => {
    const [k, n] = rate(p);
    const base = k / n;
    return {
      name: p.name,
      state: p.birth_state,
      p: generals && p.union_general === "yes" ? boost(base, ratio) : base,
    };
  });
const flat = model(byYear, false);
const meanP = flat.reduce((a, p) => a + p.p, 0) / flat.length;
const models = [
  ["Actual presidents, flat beard rate", flat.map(p => ({ ...p, p: meanP }))],
  ["Fashion by year", flat],
  ["Fashion by year + generation", model(byGeneration, false)],
  ["... + Union generals (raw odds ratio)", model(byGeneration, true)],
  [
    "... + Union generals (age-adjusted, post)",
    model(byGeneration, true, AGE_ADJUSTED_GENERAL_ODDS_RATIO),
  ],
];
console.log(
  `\nP(>= 3 full-bearded presidents 1849-1929, all born in one state):`
);
for (const [label, ps] of models) {
  const expected = ps.reduce((a, p) => a + p.p, 0);
  console.log(
    `  ${label.padEnd(44)} ${oneIn(sameStateOdds(ps)).padStart(10)}  ` +
      `(expected full beards ${expected.toFixed(1)})`
  );
}

// ---------- 12. The post's population step (1870, white Americans) ----------

section("12. The post's birth lottery: 1870 census, white native-born Americans");
// The post uses one census and white Americans only: each state's share of
// white people born in the U.S. (the printed 1870 total, 28,095,665).
const WHITE_NATIVE_1870 = 28095665;
const whiteShares = readCsv("born_in_state_1870_1880.csv")
  .map(r => ({
    place: r.birthplace,
    p: Number(r.born_1870_white) / WHITE_NATIVE_1870,
  }))
  .sort((a, b) => b.p - a.p);
const ohioWhite = whiteShares.find(r => r.place === "Ohio").p;
const sumP4 = whiteShares.reduce((acc, r) => acc + r.p ** 4, 0);
console.log(
  `Ohio: ${pct(ohioWhite)} of white native-born; all four Ohio-born = ${oneIn(ohioWhite ** 4)}`
);
console.log(
  `All four born in the same state (sum of p^4) = ${sumP4.toFixed(10)} = ${oneIn(sumP4)}`
);
console.log(
  "Largest terms: " +
    whiteShares
      .slice(0, 4)
      .map(r => `${r.place} ${pct(r.p ** 4 / sumP4, 0)}`)
      .join(", ")
);

// ---------- 13. Spare facts from the census ----------

section("13. Spare facts from the census");
const fullIn = year => fullShare(serving(year, year));
const drought = [];
for (let year = 1900; year <= 2026; year++)
  if (fullIn(year)[0] === 0) drought.push(year);
console.log(
  `Years with no full beard in Congress: ${drought[0]}-${drought.at(-1)} (${drought.length} years)`
);

const servingAs = (from, to, test) =>
  members.filter(m =>
    m.congress.some(t => t.start <= to && t.end >= from && test(t))
  );
for (const party of ["Republican", "Democrat"])
  console.log(
    `2023-2026 ${party}s with full beards: ${fmt(fullShare(servingAs(2023, 2026, t => t.party === party)))}`
  );

const delegations = Object.entries(
  Object.groupBy(
    members.flatMap(m =>
      [
        ...new Set(
          m.congress
            .filter(t => t.start <= 1885 && t.end >= 1873)
            .map(t => t.state)
        ),
      ].map(state => ({ state, m }))
    ),
    r => r.state
  )
)
  .map(([state, rows]) => [state, fullShare(rows.map(r => r.m))])
  .filter(([, [, n]]) => n >= 25)
  .sort((a, b) => b[1][0] / b[1][1] - a[1][0] / a[1][1]);
const showDelegations = rows =>
  rows.map(([s, [k, n]]) => `${s} ${pct(k / n, 0)}`).join(", ");
console.log(
  `Most bearded delegations 1873-1885: ${showDelegations(delegations.slice(0, 3))}; ` +
    `least: ${showDelegations(delegations.slice(-3))}`
);

const governors = readCsv("facial_hair_census.csv").filter(
  r =>
    r.gender === "M" &&
    !["unusable", "woman"].includes(r.facial_hair) &&
    terms(r.governor_terms).some(t => t.start <= 1889 && t.end >= 1871)
);
console.log(
  `1871-1889: senators ${fmt(fullShare(servingAs(1871, 1889, t => t.chamber === "senate")))}, ` +
    `representatives ${fmt(fullShare(servingAs(1871, 1889, t => t.chamber === "house")))}, ` +
    `governors ${fmt(fullShare(governors))}`
);
const SOUTH = ["VA", "NC", "SC", "GA", "FL", "AL", "MS", "LA", "TX", "AR", "TN"];
console.log(
  `1871-1889: Southern members ${fmt(fullShare(servingAs(1871, 1889, t => SOUTH.includes(t.state))))}, ` +
    `others ${fmt(fullShare(servingAs(1871, 1889, t => !SOUTH.includes(t.state))))}`
);
