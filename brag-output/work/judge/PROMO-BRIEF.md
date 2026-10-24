# Grading brief: Fluxcase Kickstarter promo (v2)

You are one of SEVEN independent graders. Score the film out of 10 through your own lens (given in
your instructions). Be honest: no inflation, no invented problems. A 10 means that, through your lens,
you would run this unchanged as the paid promo for a Kickstarter launch and can name nothing concrete
that would make it better. Every point off needs a specific, fixable reason, a timestamp and the fix.

The owner's words about the previous cut: "This needs to be an ad. This needs to be a promotion for a
Kickstarter. This seems kind of half-assed." So judge it as an AD: does it grab, build energy, and make
someone want to back it? A clean product viewer is not enough.

## The film
23 s, 1920x1080, 30 fps, rendered from the real CAD with three.js; soundtrack written in code
(120 BPM: a beat is 0.5 s). Storyboard: `/home/user/test/brag-output/brag-plan.md`.

A stranger who watches once must come away knowing:
- what it is: magnetic vial cases for 3 mL and 10 mL vials
- why it is different: magnets in the base and lid pull the lid shut and hold it; no clips
- the range: five sizes, black PETG
- the ask: follow it on Kickstarter now, launching November 1, 2026

Owner decisions (not up for grading): the CTA is "Follow it on Kickstarter." (the page is a pre-launch
page until launch day), the end card carries a small "Renders shown.", and the end card shows all five
cases in frame. Second lines set in Archivo 800 sentence case are subheads, by design.

## Hard rules
- No invented claims: no backer counts, goals, reviews, ratings, dimensions, weights, prices, strength
  claims beyond "pulls shut and holds it". No vague slogans.
- No em dashes in on-screen copy. No purple gradients, pill buttons or emoji.
- Cases are black PETG only; magnets are solid silver discs (owner-confirmed), never rings.
- No maker name (The 3D Print Depot) and no mention of Texas.
- "Vials not included." must be on screen whenever vials are visible.
- Every line stays up long enough to read (about 0.3 s per word, from fully visible to gone).
- Hook in the first 2 seconds. Cuts land on beats.
- Brand: ink #111413, paper #F3F4F2, grey #E2E2E2, teal #74CABF, deep teal #1D6B62; Archivo (wide,
  heavy) headlines, JetBrains Mono small text.

## What to review (round folder given in your instructions)
- `sheet-1.jpg` .. `sheet-5.jpg`: every 0.25 s, labeled. Read all five in order; this is how you watch.
- `key-*.jpg`: full-resolution frames (file name = seconds). `frames/` has every sampled frame at full
  size if you need more (t-XX.XX.png).
- `waveform.png` and `/home/user/test/brag-output/work/scripts/music2.py` (the score, with its cue
  list): you cannot listen, so judge the sound from the code and the waveform.
- The renderer is `/home/user/test/brag-output/work/site/promo.html` if you need exact timings.

## Your answer (under 450 words)
SCORE: <integer 0-10>
VERDICT: one sentence.
ISSUES: numbered, most important first: timestamp, problem, exact fix, points it costs.
TO REACH 10: the short list.
