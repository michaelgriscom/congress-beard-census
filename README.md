# congress-beard-census

Blind-coded facial hair of every U.S. member of Congress, governor and Union
Army general with a portrait on Wikimedia Commons, 1789–2026, plus the analysis
behind the blog post "How surprising is it that every bearded president was born
in Ohio?" on [michaelgris.com](https://michaelgris.com).

| Group                      | Men coded | Coverage                                                       |
| -------------------------- | --------- | -------------------------------------------------------------- |
| Members of Congress        | 10,241    | about 95% of members serving from the 1860s on; 50–70% before 1849 |
| Governors                  | 2,185     | every governor with a Wikidata portrait                        |
| Union generals (full rank) | 596       | all of them                                                    |

## Headline results

Share of men in Congress with a full beard (beard plus mustache):

| 1825 | 1849 | 1861 | 1869 | 1881 | 1893 | 1905 | 1921 | 1953 | 2026 |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| 1%   | 9%   | 25%  | 34%  | 42%  | 28%  | 12%  | 3%   | 0%   | 8.5% |

- **Men kept the style of their generation.** Among members serving 1865–1889,
  full beards ran 17% for men born in the 1800s, 47% for the 1820s and 10% for
  the 1850s. Chin beards without a mustache belong to men born around
  1805–1815, mustaches to men born in the 1840s–50s. See
  `charts/beard-cohort-chart.html`.
- **Union generals were about twice as bearded as congressmen of the same
  years**: 49% full beards vs 27% (p ≈ 4 × 10⁻⁸). Ohio-born generals: 62%.
- **Party barely mattered**: 30% of Republicans vs 27% of Democrats, 1856–1896.
- **Beards are back**: 8.5% of men in Congress in 2026, the most since about
  1910.
- **Outside check**: in 1908 the _Los Angeles Times_ counted 10 beards in 103
  pictures of congressmen; the census gives 10% full beards (13% any beard) for
  that year.

`analysis/README.md` has the full write-up, including the step-by-step odds
for the Ohio presidents.

## Data (`data/`)

- **`facial_hair_census.csv`**: one row per coded person (Congress and
  governors).
  - `wikidata`: Wikidata ID. The portrait is that item's P18 image, listed in
    `coding/images.json`.
  - `name`, `gender` (`M`/`F`), `birth_year`.
  - `congress_terms`: semicolon-separated `start-end:state:party:chamber`
    (`house` or `senate`).
  - `governor_terms`: semicolon-separated `start-end:state:party`.
  - `facial_hair`: `full_beard`, `goatee_mustache`, `beard_no_mustache` (chin
    beard or chin curtain with a shaved upper lip), `sideburns` (whiskers not
    joined across the chin), `mustache`, `clean`, `woman` or `unusable`.
- **`union_generals_facial_hair.csv`**: the 596 full-rank Union generals and
  the 200 congressmen (1861–1869) coded on the same contact sheets as
  controls, with each general's birth state.
- **`born_in_state_1870_1880.csv`**: U.S.-born population by state of birth,
  transcribed from the 1870 (Table VI) and 1880 (Table X) census nativity
  tables.
- **`presidents.csv`**, **`nominees_1856_1916.csv`**: presidents and
  major-party nominees with facial hair, birth state and Union-general status.
- **`state_population_1790_1920.csv`**: total and white population by state.
- **`robinson_facial_hair_1842_1972.csv`**: British men's facial hair by year,
  digitized by this project from Robinson (1975). Traced from a chart, so about ±3 points.
- **`wikidata_people.json`**: birth year, birth state(s), military branch and
  Civil War service from Wikidata for every coded person and Union general,
  keyed by Wikidata ID (used by `analysis/followups/`).
- **`congress_facial_hair_sample.csv`**: the 789-row pilot sample that came
  before the census.

## How the portraits were coded

1. **Portraits**: each person's Wikidata image (P18), downloaded from Wikimedia
   Commons as a 250px thumbnail. Member lists come from
   [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators);
   governors and genders from Wikidata; generals from Wikipedia's
   [list of Union generals](<https://en.wikipedia.org/wiki/List_of_American_Civil_War_generals_(Union)>).
2. **Blind contact sheets**: portraits were cropped to the face (OpenCV Haar
   cascades), shuffled, and laid out 24 to a sheet, labeled only by cell
   number, so the coder never saw a name, year, party or state.
3. **Coding guide written first**: `coding/CODING_GUIDE.md` defines the
   categories and the borderline rules.
4. **Second look**: cells flagged as tiny, mis-cropped or borderline were
   re-coded from the uncropped image (`coding/recheck_*`).
5. **Consistency**: two independent passes over 709 portraits agreed on 96% of
   full-beard calls (Cohen's κ = 0.87). 200 portraits re-coded in a later
   batch matched 95% on full beard or not.

The coding was done by an AI model (Claude) working sheet by sheet, not by a
panel of people.

### Caveats

- A portrait isn't always from the years someone served, so a member from 1846
  may appear with the beard he grew in 1866.
- Coverage is thinner before 1849, and early portraits are paintings and
  engravings.
- General portraits are mostly wartime photographs of men in their 30s and
  40s, and the coder could see uniforms.
- Borderline sideburns (how far down the cheek counts) are the least
  consistent category. Full-beard calls are the most reliable.

## Reproducing

```bash
node analysis/analyze.mjs   # every number in the post, from data/ (no dependencies)
node charts/cohort-data.mjs # the data embedded in charts/beard-cohort-chart.html
python3 analysis/followups/analyses.py  # Ohio exports, generals by age, veterans
```

Rebuilding the census from scratch needs Python 3 with `pyyaml`, `pillow` and
`opencv-python-headless<5`. From inside `coding/`:

1. `python3 fetch_inputs.py` downloads the member lists.
2. `python3 download_portraits.py <list.tsv>` or `python3 slow_download.py`
   fetches the portraits into `img/`. Commons rate-limits heavily.
3. `python3 make_batch.py <name>` builds blind contact sheets. Codes go in
   `codes_<name>.txt`, one line per sheet.
4. `python3 make_recheck.py <name> <batches...>` builds second-look sheets.
5. `python3 census.py` merges everything and prints rates for men.

`coding/batches/*.json` records which person sits in which cell of every
sheet, so each code in `coding/codes_*.txt` can be traced back to a Wikidata
ID. `coding/generals/` holds the Union general list, birthplaces and their
download scripts.

## Sources and licenses

The code in this repository and the datasets it produces (the CSVs under
`data/` and the coding files under `coding/`) are MIT licensed (see
[LICENSE](LICENSE)). The upstream sources below keep their own terms.

- Member and term data: unitedstates/congress-legislators (public domain).
- Wikidata (CC0). Portraits are on Wikimedia Commons under their individual
  licenses and are not redistributed here.
- U.S. Census Bureau: 1870 and 1880 census volumes, and Working Paper 56 for
  state population totals.
- Dwight E. Robinson, "Style Changes: Cyclical, Inexorable, and Foreseeable,"
  _Harvard Business Review_, Nov–Dec 1975 (Exhibit II).
