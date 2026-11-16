#!/usr/bin/env python3
"""Join chapter fragments into one HTML book with cover + contents, then print to PDF.
Tries google-chrome / chromium first; falls back to weasyprint (pip install weasyprint)."""
import re, html, subprocess, sys, pathlib, datetime, shutil
root = pathlib.Path(__file__).resolve().parent
parts = ["ch01-05.html", "ch06-09.html", "ch10-13.html", "ch14-16.html", "ch17.html", "ch18-21.html"]
body = ""
for p in parts:
    f = root / p
    if not f.exists():
        print("WARNING, missing:", p); continue
    body += f.read_text(encoding="utf-8") + "\n"

toc, cur = [], None
for m in re.finditer(r'<(h1|h2)([^>]*)>(.*?)</\1>', body, flags=re.S):
    tag, inner = m.group(1), m.group(3)
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', inner)).strip()
    if tag == "h1":
        num, title = (text.split(" ", 1) + [""])[:2] if text[:1].isdigit() else ("", text)
        sec = re.search(r'id="(ch\d+)"', body[max(0, m.start()-200):m.start()])
        cur = {"num": num, "title": title, "id": sec.group(1) if sec else "", "subs": []}
        toc.append(cur)
    elif cur is not None:
        cur["subs"].append(text)

toc_html = '<section class="toc"><h1>Contents</h1><ol>'
for c in toc:
    toc_html += f'<li><span class="n">{html.escape(c["num"])}</span><a href="#{c["id"]}">{html.escape(c["title"])}</a>'
    if c["subs"]:
        toc_html += "<ul>" + "".join(f"<li>{html.escape(s)}</li>" for s in c["subs"]) + "</ul>"
    toc_html += "</li>"
toc_html += "</ol></section>"

today = datetime.date.today().strftime("%d %B %Y")
cover = f'''<section class="cover">
<div class="kicker">PROJECT BOOK · WRITTEN FOR A BEGINNER</div>
<h1>Edge-AI Self-Checkout Kiosk</h1>
<div class="sub">A from-scratch NumPy CNN, a load cell on a Raspberry Pi 4, and a touchscreen bill: every part, every wire, every line of code, and why it is there.</div>
<p class="small" style="margin-top:28px">Gowtham Jothiramalingam · M.Tech Signal Processing and Machine Learning, NIT Karnataka<br>
Raspberry Pi 4 · Python · NumPy · OpenCV · HX711 · Tkinter<br>{today}</p>
<p class="small" style="margin-top:40px; max-width:140mm">How to read this book: chapters 1 to 16 explain the kiosk part by part. Chapter 17 is the complete code. Chapter 18 is the build record, step by step. Chapters 19 and 20 are the problems, the design journey from version 1 and the limits. Chapter 21 is the interview question bank and the one-page cheat sheet. Purple "measured value" boxes hold the numbers from my runs; the label reminds me to replace each one with my own fresh number after I repeat the run.</p>
</section>'''

css = (root / "style.css").read_text(encoding="utf-8")
doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Edge-AI Self-Checkout Kiosk, Project Book</title>
<style>{css}</style></head><body>{cover}{toc_html}{body}</body></html>'''
out_html = root / "Self_Checkout_Kiosk_Project_Book.html"
out_html.write_text(doc, encoding="utf-8")
words = len(re.sub(r'<[^>]+>', ' ', body).split())
print("chapters:", len(toc), "| words:", words, "| html:", out_html)

out_pdf = root / "Self_Checkout_Kiosk_Project_Book.pdf"
chrome = next((c for c in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"] if shutil.which(c)), None)
if chrome:
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
           f"--print-to-pdf={out_pdf}", f"file://{out_html}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0: print(r.stderr[-1500:])
else:
    try:
        from weasyprint import HTML
        HTML(str(out_html)).write_pdf(str(out_pdf))
    except ImportError:
        print("No Chrome/Chromium and no weasyprint. Run: pip install weasyprint   (then rerun)"); sys.exit(1)
print("pdf:", out_pdf, "exists:", out_pdf.exists(), "size:", out_pdf.stat().st_size if out_pdf.exists() else 0)
