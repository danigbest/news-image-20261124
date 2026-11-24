# The World in One Day — 24 November 2026

make.fun bounty: Sum up 24 November's world news in one image
https://make.fun/bounty/news-image-20261124

## The entry

A one-page newspaper front page for Tuesday, 24 November 2026.
Forty stories from 23–24 November 2026, gathered from public news
wires and laid out as a broadsheet: a masthead, one lead story, three
top stories, and the rest of the world in a four-column grid. Every
story carries its category, its date (23 or 24 Nov), and a certainty
tag: CONFIRMED (reported by multiple sources), REPORTED (a claim from
one side, or a filing not yet decided), or RUMORED (unverified).

## Layout

- Masthead: "THE WORLD IN ONE DAY", Tuesday 24 November 2026.
- Lead story: the US–Iran standoff in the Strait of Hormuz.
- Three top stories: the COP31 climate talks, the Kerch Bridge
  strike, and the claimed sinking of a Russian corvette.
- The rest of the world: the remaining 36 stories in a grid,
  colour-coded by category (red for geopolitics and war, blue for
  technology and diplomacy, green for economy and climate, teal for
  science and health, rust for disasters, plum for sport and culture).
- Footer: the compilation note and the story count.

## Stories (40)

1. Tankers struck by mines as US–Iran standoff deepens — Geopolitics — 24 Nov — CONFIRMED
2. Climate talks collapse over fossil fuels — Climate — 23 Nov — CONFIRMED
3. Ukraine strikes Kerch Bridge again — War — 24 Nov — CONFIRMED
4. Ukraine says it sank a Russian corvette off Libya — War — 23 Nov — REPORTED
5. Israeli strike kills Hamas security chief — War — 24 Nov — CONFIRMED
6. NATO sends AWACS to Poland after Russian missiles land — Geopolitics — 23 Nov — CONFIRMED
7. EU moves to cut 60 Russian banks from SWIFT — Geopolitics — 23 Nov — CONFIRMED
8. Russia warns Estonia is nearing open war — Geopolitics — 24 Nov — REPORTED
9. Ukraine–Russia talks end without breakthrough — Geopolitics — 24 Nov — CONFIRMED
10. Democrats win biggest House majority since 1992 — US Politics — 23 Nov — CONFIRMED
11. Nvidia brings Jensen Huang back as CEO — Technology — 23 Nov — CONFIRMED
12. Trump orders fast-track federal executions — US Politics — 23 Nov — CONFIRMED
13. Fourteen nations back ICJ Rohingya genocide ruling — Law — 23 Nov — CONFIRMED
14. Tajikistan starts withdrawal from ICC during Putin visit — World Politics — 23 Nov — CONFIRMED
15. Trump and Pashinyan launch TRIPP corridor — Diplomacy — 23 Nov — CONFIRMED
16. Stocks surge as Nvidia jumps 31.5% — Economy — 24 Nov — CONFIRMED
17. Sanofi to buy Insmed for $41 billion — Business — 24 Nov — CONFIRMED
18. DR Congo reimposes cobalt export ban — Economy — 24 Nov — CONFIRMED
19. Anthropic publishes Claude-written VP versus VNP proof — AI/Science — 24 Nov — RUMORED
20. Gemini agents cut quantum algorithm cost 290-fold — AI/Science — 24 Nov — CONFIRMED
21. OpenAI delays open-source reasoning model — AI — 23 Nov — CONFIRMED
22. Amazon to buy Decart's AI optimization tech — Technology — 23 Nov — CONFIRMED
23. OpenAI and Cisco launch Shirudo security runtime — Technology — 23 Nov — CONFIRMED
24. UN chief urges AI risk framework within a year — AI/Policy — 23 Nov — CONFIRMED
25. Oregon and Virginia sue SpaceX over Grok images — Tech/Law — 24 Nov — REPORTED
26. China opens Tiangong to first foreign astronaut — Space — 24 Nov — CONFIRMED
27. Space-tested coating keeps medicines stable in orbit — Science — 23 Nov — CONFIRMED
28. Pennsylvania measles outbreak claims ninth life — Health — 24 Nov — CONFIRMED
29. FDA approves Roche breast cancer drug — Health — 24 Nov — CONFIRMED
30. Deadly floods in China force 500,000 to flee — Disaster — 24 Nov — CONFIRMED
31. Florida river breaks 1953 flood record — Disaster — 24 Nov — CONFIRMED
32. Magnitude 5.6 earthquake strikes Nepal — Disaster — 24 Nov — CONFIRMED
33. Factory blaze in Indonesia kills 24 — Disaster — 23 Nov — CONFIRMED
34. Commanders stun Bengals 22–20 on final kick — Sport — 23 Nov — CONFIRMED
35. 49ers thrash Vikings 35–10 in Mexico City — Sport — 23 Nov — CONFIRMED
36. Miley Cyrus marries drummer Maxx Morando — Entertainment — 23 Nov — CONFIRMED
37. Mexico to try 'El Chapo Isidro' despite US bid — Latin America — 24 Nov — CONFIRMED
38. Super Bowl heads to IMAX theaters — Entertainment — 24 Nov — CONFIRMED
39. South Korea offers $375,000 to catch AI exam cheats — Education/AI — 24 Nov — CONFIRMED
40. Fighting in DR Congo traps Ebola responders — Health/Conflict — 24 Nov — CONFIRMED

## How it was made

`render.py` draws `output/entry.png` (1024x1024) with Pillow and the
fonts bundled in `fonts/` (Playfair Display for headlines, Inter for
body text, Libre Franklin for kickers, DejaVu Sans Bold for tags).
Run it with `python3 render.py` from this directory.

`main.py` is the entrypoint the grader runs. It uses only the Python
standard library: it copies the bundled `output/entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`. The grading sandbox has no Pillow
and a read-only `/bot`, so the image is drawn once here and copied
there, which is the approach the bounty rules name as the simplest
entry. Two runs write the same bytes.

## Verification

Render, then run the entrypoint the way the grader does:

    python3 render.py
    MAKEFUN_OUTPUT_DIR=/tmp/out python3 -P -s main.py
    sha256sum output/entry.png /tmp/out/entry.png

Both hashes must match and the program must exit 0.
