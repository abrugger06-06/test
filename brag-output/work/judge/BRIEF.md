# Judge brief: Fluxcase Kickstarter launch ad

You are an independent judge. Score the ad out of 10. Be honest: do not inflate the score and do not
invent problems. A 10 means you would ship it unchanged as the launch video on a Kickstarter page and
can name nothing concrete that would make it better. Every point you take off must come with a
specific, fixable reason and the exact fix (what to change, at what timestamp).

## What the ad is
A 20 s, 1920x1080, 30 fps landscape video announcing that Fluxcase launches on Kickstarter on
November 1, 2026. It is rendered from the real CAD files (no stock footage, no AI images) with
three.js, and has a soundtrack written in code (120 BPM, so a beat is 0.5 s and a bar is 2 s).

A stranger who watches it once must come away knowing:
- what it is: 3D printed magnetic vial cases for 3 mL and 10 mL vials
- why it is different: magnets (solid discs) in the base and lid pull the lid shut and hold it there
- the range: 5 case sizes, all black PETG (the only material offered)
- how to get one: back it on Kickstarter, launching November 1, 2026

## Rules the ad must follow
- No invented claims: no backer counts, funding goals, reviews, ratings, dimensions, weights or prices.
- No vague slogans. Say plainly what it is.
- No em dashes in on-screen copy. No purple gradients, no pill-shaped buttons, no emoji as icons.
- Magnets are always silver. Cases are black PETG only (owner decision).
- Every line on screen stays up long enough to read (about 0.3 s per word).
- The hook lands in the first 2 seconds. Every cut lands on a beat (cuts at 2, 5, 9, 13, 16 s).
- Brand: ink #111413, background #F3F4F2, render grey #E2E2E2, teal #74CABF, deep teal #1D6B62.
  Type: Archivo (wide, heavy) for headlines, JetBrains Mono for labels.
- The owner asked that the material statement ("Black PETG...") be very small.
- The owner asked that the maker name (The 3D Print Depot) not appear anywhere, and that Texas not be mentioned.
- Wherever vials are shown, a small "Vials not included." line must be on screen.

## Facts that are allowed on screen
Magnets (solid discs) in the base and lid pull the case shut and hold it, no clips. PETG, 3D printed to order. Five cases: 12-Vial 3 mL, 6-Vial 3 mL, 4-Vial 10 mL, 8-Vial 10 mL,
7-Vial Mixed. Kickstarter launch November 1, 2026. No Kickstarter URL exists yet.

## What to review (all under the round folder you are given)
- `../../../brag-plan.md`: the storyboard with timings and sound.
- `sheet-1.jpg` .. `sheet-4.jpg`: every 0.25 s of the video, labeled with the timestamp. Read all four
  in order; this is how you watch the motion.
- `key-*.jpg`: full-resolution 1920x1080 frames at key moments (file name = seconds).
- `waveform.png`: the soundtrack's waveform (you cannot listen; use it and the storyboard's sound
  column to judge whether the hits line up with the picture).

## Your answer (keep it under 400 words)
SCORE: <integer 0-10>
VERDICT: one sentence.
ISSUES: a numbered list, most important first. Each item: timestamp(s), the problem, the exact fix,
and how many points it costs.
TO REACH 10: the short list of changes that would make you give 10.
