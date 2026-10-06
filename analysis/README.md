# Presidential beards and Ohio: research notes

Research behind the blog post "How surprising is it that every bearded
president was born in Ohio?" on michaelgris.com. Every number in the post can
be reproduced from the files in `data/`.

Run the numbers with:

```bash
node analysis/analyze.mjs
```

## The claim, precisely

| President         | Facial hair in office     | Born | Elected from | In office |
| ----------------- | ------------------------- | ---- | ------------ | --------- |
| Abraham Lincoln   | Chin curtain, no mustache | KY   | IL           | 1861–65   |
| Ulysses S. Grant  | Full beard                | OH   | IL           | 1869–77   |
| Rutherford Hayes  | Full beard                | OH   | OH           | 1877–81   |
| James Garfield    | Full beard                | OH   | OH           | 1881      |
| Benjamin Harrison | Full beard                | OH   | IN           | 1889–93   |

The claim depends on two definitions:

- **"Full beard"** has to mean beard plus mustache. Count Lincoln's chin beard
  and it becomes 4 of 5.
- **"From Ohio"** has to mean born there. Grant was elected from Illinois and
  Harrison from Indiana, so by political home state it's 2 of 4.

All four full-bearded presidents were also **Republicans** and **Union Army
generals**. That turns out to be the main explanation.

## Statistics that answer the question

Each row is a different null hypothesis. The headline number depends heavily
on which one you pick, and that's probably the most interesting part of the
post.

| #   | Question                                                                                                               | Result                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 2   | Naive: each bearded president is a random American from his birth cohort. P(all 4 Ohio)?                               | 1 in ~44,000 (total pop.), 1 in ~20,000 (white pop.) |
| 3   | Look-elsewhere: P(all 4 share _some_ birth state)?                                                                     | 1 in ~790 (New York accounts for 72%)                |
| 4   | Given who actually served 1861–1913 (11 presidents, 6 Ohio-born), P(all 4 full beards land on Ohioans)?                | **4.5% (1 in 22)**; 17.5% if Lincoln counts          |
| 5   | Fashion model: each president bearded with P = share of men with beards that year (Robinson). P(only Ohioans bearded)? | 2.0–4.4% (1 in 23 to 1 in 51)                        |
| 6   | Widen to all major-party nominees 1856–1916 (22 people, 7 full beards). Beard–Ohio association?                        | p = 5.4%                                             |
| 6b  | Same, Republican nominees only (11 people)                                                                             | **p = 65%, i.e. no association**                     |
| 7   | Ohio-born winners of the 14 elections 1868–1920, vs. Ohio's share of the population                                    | 9 of 14; 1 in ~500,000                               |
| 8   | Union generals vs. everyone else among nominees 1856–1916: share with full beards                                      | 71% vs. 13% (p = 1.4%)                               |

How to read it:

1. **The naive odds (1 in tens of thousands) are badly misleading.** Ohio was
   a big state then: 3rd most populous from 1840 to 1880, and about 9–10% of
   white Americans when the bearded presidents were born.
2. **The real anomaly is Ohio, not beards.** Ohio-born men won 9 of the 14
   elections from 1868 to 1920. A population-proportional lottery would almost
   never produce that. Historians have explanations: Ohio was a populous swing
   state; until 1885 it voted for state offices in October, a closely watched
   preview of November; it sent about 320,000 men to the Union Army (3rd most,
   highest per capita); and it was the Republican base.
3. **Once you take the actual roster of presidents as given, the beard
   pattern is mildly surprising, around 1 in 20 to 1 in 50.** The total count
   is just what fashion predicts (about 5 bearded presidents expected and 5
   observed, counting Lincoln). The only odd part is which ones had them.
4. **The mechanism is the Union Army.** Two-thirds of Civil War generals had
   beards. Among the period's nominees, 5 of 7 Union generals had full beards
   vs. 2 of 15 others. Every president who had commanded troops as a Union
   general was a bearded Ohioan. (Andrew Johnson held the rank only as
   military governor of Tennessee.) Among Republican nominees alone, being from Ohio says
   nothing about having a beard. The full census of 596 Union generals
   confirms the link: 49% had full beards vs 27% of congressmen of the same
   years (see "Union generals" below).
5. **The streak nearly broke twice.** Three bearded non-Ohioans were
   nominated: Frémont (GA, 1856), Blaine (PA, 1884) and Hughes (NY, 1916).
   Blaine lost New York by 1,047 votes out of about 1.17 million, and Hughes
   lost California by 3,773. About 525 New Yorkers switching in 1884, or
   about 1,900 Californians in 1916, would have put a non-Ohioan with a full
   beard in the White House. (Third-party
   bonus: Populist James B. Weaver in 1892 was also a bearded, Ohio-born
   Union general.)

## Beard popularity over time

From Robinson's count of men pictured in the _Illustrated London News_
(5-year moving averages, digitized from his chart; see the data notes below):

| Year | Beard | Mustache only | Any facial hair |
| ---- | ----- | ------------- | --------------- |
| 1850 | 16%   | 4%            | 70%             |
| 1860 | 34%   | 8%            | 83%             |
| 1870 | 35%   | 8%            | 82%             |
| 1880 | 44%   | 22%           | 93%             |
| 1890 | 43%   | 26%           | 91%             |
| 1900 | 28%   | 48%           | 81%             |
| 1910 | 24%   | 42%           | 71%             |
| 1920 | 11%   | 41%           | 54%             |
| 1950 | 3%    | 22%           | 25%             |

Beards were at their peak from about 1858 to 1895. The 1869–1893 run of
bearded presidents falls right inside it. After about 1895 mustaches took
over (Cleveland, TR, Taft), and by 1913 presidents were clean-shaven.

## Beards in the U.S. Congress

The British series isn't American, so I built an American one: a census of
every member of Congress and every governor who has a portrait on Wikimedia
Commons (via Wikidata). Each portrait was face-cropped and placed on a shuffled
contact sheet labeled only with a cell number, so the coder couldn't see the
name, year, party or state. Cells the coder flagged (tiny faces, missed crops,
borderline calls) got a second look uncropped. Women are excluded. That's
10,241 men in Congress and 2,185 governors (`data/facial_hair_census.csv`).

| Year | Men coded | Share of those serving | Full beard |
| ---- | --------- | ---------------------- | ---------- |
| 1825 | 187       | 48%                    | 1%         |
| 1849 | 316       | 68%                    | 9%         |
| 1861 | 415       | 90%                    | 25%        |
| 1869 | 444       | 94%                    | 34%        |
| 1881 | 501       | 94%                    | 42%        |
| 1893 | 605       | 97%                    | 28%        |
| 1905 | 594       | 98%                    | 12%        |
| 1921 | 711       | 99%                    | 3%         |
| 1953 | 625       | 99%                    | 0%         |
| 2025 | 435       | 100%                   | 7%         |

What it shows:

- **The full-beard peak was about 1881, at 42% of men in Congress.** It was
  under 10% before 1850 and gone by the 1930s. The full-bearded presidents
  (1869–1893) sit right on the peak. Beards are now back to 7%, the highest
  in a century.
- **Generation matters as much as the year.** Men kept the style of their
  youth. Among members serving 1865–1889, full beards were 17% for men born in
  the 1800s, 32% in the 1810s, 47% in the 1820s, 39% in the 1830s, 26% in the
  1840s and 10% in the 1850s. Lincoln and Andrew Johnson (born 1808–09) belong
  to the chin-curtain generation; the four bearded presidents (born 1822–33)
  to the most bearded one.
- **Party barely mattered.** From 1856 to 1896, 30% of Republicans and 27% of
  Democrats had full beards (p = 0.17). (A 60-per-decade pilot sample had
  suggested 44% vs 29%; the full census shows that was sampling noise.)
- **Ohio Republicans were somewhat hairier.** From 1866 to 1896, 46% of Ohio's
  Republican members had full beards, against 31% of other Republicans
  (p = 0.04, counting a member once per decade served).

## Union generals

All 596 full-rank Union generals from Wikipedia's list have a portrait, mostly
wartime photographs. They were coded blind on the same contact sheets as 200
randomly chosen men who served in Congress in 1861–1869 (`data/union_generals_facial_hair.csv`).

- **Generals: 49% full beards (292 of 595). Same-era congressmen: 27% (54 of
  199).** p ≈ 4 × 10⁻⁸; odds ratio 2.6. The congressmen had more chin curtains
  and neck beards, which fits their being older.
- **Ohio-born generals: 62% (40 of 65) vs 48% of other generals** (p = 0.05).
- **Ohio produced 12.5% of U.S.-born generals** with a known birthplace (65 of
  520), tied with Pennsylvania for second behind New York, against Ohio's 9%
  of the native-born population.
- The controls' new codes matched their original codes 89% of the time (95% on
  full beard or not), a check on coding consistency.

Caveats: the general portraits are wartime photos of men mostly in their 30s
and 40s, while Congress portraits come from any point in a career. The coder
could see uniforms. Benjamin Harrison was a brevet (honorary) general, so he
isn't on the full-rank list.

## The presidents' odds, step by step

P(at least 3 presidents from 1849–1929 have full beards and all were born in
the same state). Only Ohio had 3 or more presidents in that span, so "any
state" and "Ohio" are the same here. Each president's beard probability comes
from the census (section 11 of the script).

| Model                                                         | Odds        |
| ------------------------------------------------------------- | ----------- |
| Ohio's population, all four Ohio-born (1870 nativity, whites) | 1 in 13,000 |
| ...any one state                                              | 1 in 1,400  |
| Actual presidents taken as given, flat beard rate             | 1 in 98     |
| Beard rate by inauguration year                               | 1 in 45     |
| Beard rate by year and generation (men born within 5 years)   | 1 in 18     |
| ...and Union generals get the generals' odds ratio (2.6)      | 1 in 9      |

The leftover luck is mostly that Chester Arthur (44%) and Grover Cleveland
(42%), contemporaries of the bearded four, didn't grow full beards. Each step
takes something as given; the numbers measure how much of the coincidence is
left to explain, not the odds that history went this way. With four
presidents, read them as orders of magnitude.

## Published U.S. data

I found no published year-by-year series for American men. The closest:

- **Nevada politicians, 1873–1899.** Elaine Pedersen coded 475 photographs:
  45% mustache only, 21.9% beard and mustache, 8.4% no facial hair. This is
  the closest to a published American politician sample, but it covers only
  the West and the end of the beard era.
- **Congress, 1893 and 1908.** The _Los Angeles Times_ wrote in 1893 that there
  were "few faces among our statesmen… which were shaven every morning." In
  1908 it counted 10 beards in 103 pictures of congressmen, under the headline
  "Statesmen Are Smooth Shaven." Both are quoted in Logan Daugherty, "The
  Crusade Against the Whisker."
- **Civil War generals.** About two-thirds had beards (h2g2, from Warner's
  lists; see Sources).

## Ohio's weight in the country

| Census | Ohio, % of U.S. | Ohio, % of white pop. | Rank |
| ------ | --------------- | --------------------- | ---- |
| 1820   | 6.0%            | 7.3%                  | 5    |
| 1830   | 7.3%            | 8.8%                  | 4    |
| 1840   | 8.9%            | 10.6%                 | 3    |
| 1860   | 7.4%            | 8.6%                  | 3    |
| 1880   | 6.4%            | 7.2%                  | 3    |
| 1900   | 5.5%            | 6.1%                  | 4    |

Ohio had 21–24 electoral votes from 1868 to 1920, about 4.5–7% of the
total.
Overall, 7 of 45 presidents (16%) were born in Ohio, second only to
Virginia's 8.

### By state of birth

Residence shares count people who moved to Ohio and miss Ohioans who left.
The 1870 and 1880 censuses tabulated the native-born by state of birth
(1870 Table VI, "Special nativity"; 1880 Table X). Since presidents must be
natural-born citizens, the share of the native-born born in each state is the
better denominator. Ohio-born people were 8.0% of the native-born in 1870 and
7.6% in 1880. That's more than Ohio's share of residents, because Ohio
exported people west.

Using each president's nearest census (section 10 of the script):

|                                            | Odds        |
| ------------------------------------------ | ----------- |
| All four born in Ohio                      | 1 in 27,754 |
| All four born in the same state, any state | 1 in 2,949  |

Ohio is 11% of the same-state total. New York (50%) and Pennsylvania (28%)
are most of the rest. Dropping territories, DC and people born at sea from the
denominator moves this by under 4%.

## Data files (`../data/`)

- `presidents.csv`: every president, with birth state, home state, years in
  office, party, facial hair in office, and Union-general status (beard era
  only).
- `nominees_1856_1916.csv`: Republican and Democratic nominees for every
  election from 1856 to 1916, with facial hair, birth state, and Union-general
  status. Facial hair follows Nicholas Whyte's list.
- `state_population_1790_1920.csv`: total and white population by state for
  each census, using current state borders. The script folds WV into VA before
  1863 and ME into MA before 1820.
- `robinson_facial_hair_1842_1972.csv`: digitized from Exhibit II of Robinson
  (1975) by tracing the plotted areas pixel by pixel against the printed
  gridlines. Values are good to about ±3 points and ±1–2 years, and the five
  categories don't add up exactly to the "any facial hair" panel. Years before
  1843 and after 1970 were dropped because of edge artifacts.
- `born_in_state_1870_1880.csv`: the native-born U.S. population by state
  or territory of birth, from the "Total of the United States" row of 1870
  Table VI and 1880 Table X. Transcribed from page scans. Virginia and West
  Virginia are combined because 1870 combined them. The 1870 columns
  reproduce the printed race totals exactly, except white, which comes up
  15,000 (0.05%) short. The 1880 column sums to within 9 of the printed
  43,475,840.
- `facial_hair_census.csv`: every coded member of Congress and governor:
  Wikidata ID, name, gender, birth year, terms (`start-end:state:party`,
  semicolon-separated) and facial hair.
- `union_generals_facial_hair.csv`: the 596 Union generals and 200 Congress
  controls coded on the same sheets, with generals' birth states.
- `congress_facial_hair_sample.csv`: the earlier pilot sample: 789 rows (736 people) of sampled members
  of Congress with snapshot year, sample (`random` or `ohio`), chamber, state,
  party, coded facial hair and the Commons portrait file. 22 portraits couldn't
  be downloaded, 4 were unusable and 1 member was a woman (Jeannette Rankin);
  all are excluded from the rates.

## Caveats

- **The long beard series is British.** Robinson counted men in a London
  weekly, mostly notable and older men. The Congress sample is American but
  covers only one year per decade, and only politicians.
- **Robinson's "beard" includes chin beards like Lincoln's.** Using it as the
  probability of a _full_ beard overstates beards in model 5, which makes the
  Ohio pattern look more surprising, not less.
- **Population share stands in for birth share.** Frontier states like Ohio
  had higher birth rates than their population share suggests. That would
  raise Ohio's odds a little in models 2–3.
- **Small samples.** With 4–7 bearded people, every p-value above swings a
  lot with each coding decision. That's worth saying in the post.

## Possible further data

- **More Congress years.** Coding every Congress from 1855 to 1911, instead
  of one year per decade, would pin down the American peak and the speed of
  the collapse.
- **Vice-presidential nominees** would add about 30 more data points for
  1856–1916, for example William English (D, 1880, bearded, born in Indiana).
- **Union vs. Confederate generals by home state**, using Warner's _Generals
  in Blue_, would show whether Ohio officers were especially bearded.

## Sources

- Dwight E. Robinson, "Style Changes: Cyclical, Inexorable, and Foreseeable,"
  _Harvard Business Review_, Nov–Dec 1975 (Exhibit II).
  [PDF](https://societypg.smajda.com/feminist/files/2018/06/Robinson-1975-Style-Changes-Cyclical-Inexorable-and-Foreseeable.pdf).
  The full study is Robinson, "Fashions in Shaving and Trimming of the Beard:
  The Men of the Illustrated London News, 1842–1972," _American Journal of
  Sociology_ 81(5), 1976.
- Gibson & Jung, _Historical Census Statistics on Population Totals by Race,
  1790 to 1990_, U.S. Census Bureau Working Paper 56, tables 15–65.
  [census.gov](https://www.census.gov/library/working-papers/2002/demo/POP-twps0056.html)
- Nicholas Whyte, "Facial hair and Presidential elections."
  [nicholaswhyte.info](https://nicholaswhyte.info/presbeards.htm)
- [List of presidents of the United States with facial hair](https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States_with_facial_hair)
  (Wikipedia)
- [Ohio in the American Civil War](https://en.wikipedia.org/wiki/Ohio_in_the_American_Civil_War)
  (Wikipedia): about 320,000 soldiers, 19 major generals and 53 brigadier
  generals
- [1885 United States gubernatorial elections](https://en.wikipedia.org/wiki/1885_United_States_gubernatorial_elections)
  (Wikipedia): Ohio's last October election
- Civil War generals' facial hair (67.1% bearded, from Warner's lists): h2g2,
  [Facial Hair and the American Civil War](https://www.h2g2.com/edited_entry/A39115334).
  This is a community-written source; check it against Warner before
  publishing.
- 1884 New York margin (1,047 votes):
  [270towin](https://www.270towin.com/1884_Election/). 1916 California
  margin (3,773 votes):
  [Wikipedia](https://en.wikipedia.org/wiki/1916_United_States_presidential_election).
- Elaine L. Pedersen, "Men's Head and Facial Hair in the Far West: 1873 to
  1899," _Clothing and Textiles Research Journal_ 19(4), 2001, 158–170.
  [SAGE](https://journals.sagepub.com/doi/10.1177/0887302X0101900402);
  figures as reported by
  [Improbable Research](https://improbable.com/2014/08/01/hair-and-moustaches-in-the-far-west-1873-to-1899).
- Logan Daugherty, "'The Crusade Against the Whisker' and the Birth of the
  Modern Radical Beard," quoting the _Los Angeles Times_ of September 24, 1893
  and October 27, 1908.
  [PDF](https://journals.wichita.edu/index.php/ff/article/download/226/218/304)
- Congress members and terms:
  [unitedstates/congress-legislators](https://github.com/unitedstates/congress-legislators).
  Portraits: Wikidata image property (P18), files on Wikimedia Commons.
