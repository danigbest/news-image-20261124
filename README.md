# The World in One Day — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/danigbest/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/danigbest/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

## What this is

A one-page news digest that sums up the world on Tuesday, 24 November 2026
in a single 1024×1024 image. One day, forty stories, one poster.

The front page leads with the Strait of Hormuz standoff — Iran's mine
claims, the US blockade, and the diplomacy around it — then three featured
stories (Ukraine's strikes on Russian ships, the Huawei trade-secret
verdict, and the Dow closing above 50,000 for the first time), followed by
a 33-item grid covering the rest of the day: NATO and airspace incidents,
the Houthi drone attack on Riyadh, Gaza, Colombia, markets, tech, space,
and sport.

Every item carries a certainty dot: green means confirmed by major outlets,
gold means reported by one or two sources, red means rumoured or denied.
The legend sits in the footer.

## How it was made

The poster is drawn from scratch with Pillow — no photos, no templates.
`render.py` lays out the masthead, the lead panel with a stylised strait
scene (ships, mines, warning marker), the featured cards, and the world
grid, then saves `output/entry.png`.

`main.py` is stdlib-only: it copies `output/entry.png` into
`$MAKEFUN_OUTPUT_DIR/entry.png`, which is what the grader runs.

## Run it

```sh
python3 render.py
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

## Sources

Stories were gathered from Reuters, AP, BBC, and AFP coverage of
24 November 2026, plus ESA, Zacks, and FBref for space, markets, and
sport. Headlines are the author's own paraphrases; figures are rounded
where the reporting differed between outlets.

## Competition

make.fun bounty: Sum up 24 November's world news in one image

https://make.fun/bounty/news-image-20261124
