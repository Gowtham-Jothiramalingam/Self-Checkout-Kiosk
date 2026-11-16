# How to use this handoff kit (for you, Gowtham)

This folder lets a fresh Claude session (any account, Fable 5.1, single agent) write the kiosk project
book at the same quality as the robotic fish book.

## Step 1. Get this folder into the new session
Easiest: push the whole Self-Checkout-Kiosk-main folder (this handoff folder included) to a GitHub
repository, then start a Claude Code session on that repository from your phone. If you cannot use
GitHub, upload handoff.zip (next to this file) and ask Claude to unzip it first.

## Step 2. Paste this as the first message
---------------------------------------------------------------------------------------------------
Read handoff/00_START_HERE.md, handoff/CONVENTIONS.md, handoff/V1_SUMMARY.md and handoff/KIOSK_BOOK_BRIEF.md
completely before doing anything. Then write the complete "Edge-AI Self-Checkout Kiosk" project book and
code exactly as the brief says, as a single session with no subagents. Work one chapter group per turn,
save each file to disk as soon as it is finished, and tell me in one line what you finished and what is
next. If a turn is cut off, start the next one by listing book/ and continuing from the first missing
file. Do not ask me questions unless something would make the work useless; make sensible choices and
record every new number in CONVENTIONS.md so the chapters stay consistent. Quality bar: the same as a
printed textbook for a beginner, finished-project voice, every "why" explained, predicted numbers in the
purple boxes. When all chapters exist, copy handoff/assemble.py and handoff/style.css into book/, run
assemble.py, check the PDF, and give me the PDF, the README and the src folder.
---------------------------------------------------------------------------------------------------
Then simply reply "continue" after each turn until the PDF arrives. Expect 8 to 12 turns.

## Step 3. After you get the PDF
Every purple "Measured value" box holds a predicted number. When you later make the dataset crops and
train the model for real, replace those numbers with yours (search the HTML for "predicted"). The code
is written so your real run produces exactly the files and numbers the book talks about.

## What is in this folder
- CONVENTIONS.md   writing rules, HTML format, and the full numbers sheet (pins, layers, predicted results)
- V1_SUMMARY.md    true facts about version 1 (YOLOv5, ESP8266, laptop) for the design-story chapters
- KIOSK_BOOK_BRIEF.md   the chapter-by-chapter plan, code deliverables, smoke tests, working method
- style.css        the print stylesheet (A4)
- assemble.py      joins the chapters, adds cover and contents, prints the PDF (Chrome or weasyprint)
