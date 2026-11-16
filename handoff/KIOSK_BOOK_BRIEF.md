# Brief: write the "Edge-AI Self-Checkout Kiosk" project book (single session, no subagents)

You are producing one PDF book plus working code for the project on the reader's resume. Read, in this
order, before writing anything: CONVENTIONS.md (voice, HTML format, numbers sheet), V1_SUMMARY.md
(what version 1 truly was), then this file. The v1 folder next to this handoff folder (../src, ../GUI TWO
FRAME, ../README.md, ../"Self-Checkout Kiosk.pdf") is the old project; read it for facts and tone only.

## Deliverables (all inside a folder named book/ next to this file)
1. Chapter fragments, written in this order and saved to disk as each is finished:
   book/ch01-05.html, book/ch06-09.html, book/ch10-13.html, book/ch14-16.html, book/ch17.html, book/ch18-21.html
2. Code in book/src/ (complete, runnable, beginner comments, names exactly as in CONVENTIONS):
   classifier/cnn_numpy.py, classifier/prepare_dataset.py, classifier/train.py, classifier/gradient_check.py,
   kiosk/hx711.py, kiosk/weight_filter.py, kiosk/calibrate.py, kiosk/camera.py, kiosk/bill.py,
   kiosk/kiosk_app.py, kiosk/prices.csv, kiosk/config.json, README.md
3. book/assemble.py and book/style.css: copy them from this handoff folder, then run
   python3 book/assemble.py to produce book/Self_Checkout_Kiosk_Project_Book.pdf.
4. Smoke tests you MUST run (no real fruit photos exist on this machine):
   - gradient_check.py on the real Net in float64: report the biggest relative difference (expect < 1e-5).
   - train.py --synthetic: trains the real Net on a small synthetic set (coloured shapes drawn with
     OpenCV or NumPy, 12 classes, 64 x 64) for a few epochs and must reach well above chance, saving
     weights.npz and metrics.json and a confusion matrix. This proves the code learns. Fruit numbers
     in the book stay as the predicted values from the numbers sheet.
   - bill.py and weight_filter.py doctests or a tiny __main__ demo with made-up readings.
   - python3 -m py_compile on every file. hx711.py, camera.py and kiosk_app.py cannot run without the Pi;
     they must import cleanly with a fake GPIO when RPi.GPIO is missing (a small stub inside hx711.py
     under try/except ImportError, so the app can be demoed on a laptop with a "simulated scale" flag).
   Say in your final message exactly what ran and what did not.

## Target size and quality
- About 100 to 120 A4 pages, 40,000 to 50,000 words of prose plus code. Many Why boxes (3 to 6 per
  chapter), Interview tips, Be careful boxes, Measured value boxes with the predicted numbers, Design
  story boxes where the v1 to v2 move explains a choice. At least 2 SVG figures per chapter in chapters
  1 to 16, each drawn to show the real mechanism (not decoration).
- Every technical word explained once in plain English. The reader is a beginner in everything.
- Finished-project first-person voice throughout. No em-dashes. No "you could". No "the plan is".
- All numbers from the numbers sheet. If a chapter needs a number the sheet does not give, choose a
  sensible one, state it as predicted in a measure box, and ADD it to CONVENTIONS.md so later chapters
  agree.

## Working method (single session, can take time)
- Write one chapter group per turn. Save the file, then run a quick check (section ids present, no
  em-dashes, every <section> closed, figure count, word count) before moving on. If the session is
  interrupted, the next turn starts by listing book/ and continuing with the first missing file.
- Write chapter 17 (the code) by first writing the real source files in book/src/, running the smoke
  tests, and only then embedding the files into ch17.html with a small Python script that HTML-escapes
  them and verifies the embedded text is identical to the source files.
- After all six fragments exist: run assemble.py, open the PDF (pdfinfo page count, pdftoppm a few pages
  if available) and fix anything that renders badly. Then deliver the PDF, the README and the src folder.

## Chapter plan (h1 titles; cover the listed content; add what a careful teacher would add)

### Group 1: book/ch01-05.html
1 The kiosk on one page. One sentence; the three jobs (see, weigh, bill); Figure 1.1 whole-system block
  diagram (camera -> prepare -> CNN -> name; load cell -> HX711 -> two wires -> filter -> grams; price
  and bill -> touchscreen; all inside the Pi); what the title words mean (edge, AI, CNN, from scratch,
  load cell, HX711, itemised bill); why the project exists (loose produce has no barcode); the 40-second
  spoken explanation in a tip box; a table mapping each resume claim to the chapter that explains it.
2 The Raspberry Pi 4, from zero. What a single-board computer is versus a microcontroller; what is on
  the board (BCM2711 4-core 1.5 GHz, 4 GB RAM, micro-SD, USB-C power, 2 micro-HDMI, 4 USB, Ethernet,
  Wi-Fi, DSI display connector, CSI camera connector, 40-pin header); Raspberry Pi OS and Linux in plain
  words; the COMPLETE 40-pin header table from CONVENTIONS with a column "used in this project";
  Figure 2.1 SVG of the header with the four HX711 pins and the screen power pins highlighted orange;
  the three weak points (no analog input, 3.3 V pins, Linux timing) each with why it matters here;
  power needs (5 V 3 A, lightning symbol); SSH and VNC in one line; why a Pi and not an Arduino, ESP32,
  laptop, cloud server or Jetson (table).
3 The other parts, and why each one. Camera (C270, why fixed height and fixed light), load cell (strain
  gauges, Wheatstone bridge in simple words, 5 kg rating), HX711 (amplifier x128 + 24-bit ADC, why it
  exists), touchscreen (why touch, why 7 inch), power supply, frame, tray, LED light. Parts table with
  rupee prices and where bought. Figure 3.1 inside a load cell (bar, gauges, bridge). Figure 3.2 what
  the HX711 does (tiny voltage -> big voltage -> number).
4 Wiring, exactly. Pin-to-pin table for HX711, screen and camera; Figure 4.1 wiring diagram; the rules
  with why (3.3 V not 5 V for the HX711, short wires, tray touches nothing but the load cell, centre the
  tray on the cell, common ground); load cell wire colours and the "weight goes down when added" swap;
  first power-on checklist.
5 Software setup. Flashing Raspberry Pi OS Bookworm 64-bit with Imager; first boot; apt packages
  (python3-numpy, python3-opencv, python3-tk, rpi-lgpio) and why apt instead of pip on the Pi; enabling
  the DSI screen; testing the camera with a one-line OpenCV script; the laptop side (Python 3.11, numpy,
  opencv-python, matplotlib) for training; copying weights.npz to the Pi with scp; autostart of the
  kiosk app on boot (a systemd service, shown); the repository layout from CONVENTIONS. Figure 5.1 the
  two machines and what moves between them (photos stay on laptop, weights file goes to Pi).

### Group 2: book/ch06-09.html
6 A picture is just numbers (OpenCV). Pixels, (480, 640, 3), BGR vs RGB, the preparation steps table
  (crop box, pad to square, BGR to RGB, resize 64 x 64 INTER_AREA, divide by 255, reorder to
  (1, 3, 64, 64)) with why for each; prepare_image() code; the one rule that matters most (same
  preparation at training and at the kiosk); what OpenCV does and does NOT do in this project (interview
  tip: "OpenCV only prepares the image; the classifier is my own NumPy code"). Figure 6.1 the pipeline
  from camera frame to the (1,3,64,64) block. Figure 6.2 a tomato squashed vs padded to a square.
7 The CNN, layer by layer. Why not an ordinary dense network (12,288 inputs, too many weights, no
  understanding of position); convolution with a worked 5 x 5 example (Figure 7.1), filters, feature
  maps, weight sharing; output size formula and the conv weight formula; ReLU; max pooling with a
  worked example (Figure 7.2); flatten; dense; softmax with a worked table; confidence and the "softmax
  always adds to 1" warning; THE NETWORK OF THIS PROJECT as a full table (layer, output shape, how the
  shape is found, weights) exactly as in CONVENTIONS, total 80,604; where the weights are (dense1 has
  92%) versus where the work is (conv layers do 98% of the multiplications); Figure 7.3 the whole
  network as boxes.
8 How the CNN learns. Cross-entropy loss with a table; why not count mistakes; gradient descent with the
  foggy hill analogy; learning rate; momentum in one paragraph (a ball rolling); backpropagation as
  blame passing with the per-layer table (softmax+loss, dense, ReLU, flatten, maxpool, conv); batch,
  epoch, shuffle, He initialisation; overfitting and the four fixes; the gradient check and why it is the
  only real proof; the training curve of this project (Figure 8.1 SVG, train and validation accuracy per
  epoch with the best epoch 34 marked, predicted); the first attempt that overfitted (measure box).
9 The from-scratch code, explained. Walk through cnn_numpy.py piece by piece: the slow conv for
  understanding, the fast einsum conv (explain einsum letters), its backward pass, MaxPool with the mask,
  Dense, softmax and loss_and_grad, Net.forward/backward/step with momentum, save/load weights. Why
  float32. Why loop over the 9 filter cells and not over pixels (measure box: slow 85 ms vs fast 0.7 ms per
  image per layer on the laptop, predicted). The gradient check code. Interview tip: practise saying the
  conv and pool backward rows without looking.

### Group 3: book/ch10-13.html
10 The dataset, training, and what 92.6% means. Where the photos came from (v1's 636 top-view photos
   with YOLO boxes); turning detection boxes into classification crops (why: one item per crop, more
   samples, the kiosk also sees one item at a time) with Figure 10.1; dropping Capsicum and Chilly
   (why: 15 and 17 photos are too few; measure box); the 12 classes in their fixed order; splitting BY
   PHOTO (why: near-copies leak); the three piles; augmentation and why only on training; the training
   run (measure boxes: epochs, time, best epoch, train/val/test accuracy, 262 of 283); what 92.6% says
   and does not say; chance level; the confusion matrix as a 12 x 12 table (predicted, with the Mosambi
   and Lemon story) Figure 10.2; precision and recall for one class in plain words; what I would need to
   claim it in a real shop.
11 Running on the Pi (edge inference). Train on the laptop, run on the Pi; what moves (weights.npz);
   loading weights into the same layer code; counting the 2.5 million multiplications (table); measured
   18 ms on the Pi vs 4 ms on the laptop (measure box); choices that keep it light (predict once per
   item, 64 x 64, float32, no Python loops, load weights once); what edge buys (table: speed, no
   network, cost, privacy); the confidence rule 0.60 and the "Not sure" screen; Figure 11.1 the Pi
   timeline for one item (settle 1.2 s, photo, 60 ms predict, show).
12 Weighing: load cell and HX711. Strain gauges and the Wheatstone bridge; what the HX711 does
   (amplify x128, 24-bit ADC, 16,777,216 steps); the two wires DT and SCK; how one reading works
   (DT low = ready, 24 pulses biggest bit first, 25th pulse sets gain 128) with Figure 12.1 timing
   diagram; two's complement for 24 bits with an example; the timing trap (SCK high > 60 us resets the
   chip) and why the Pi hits it; 10 vs 80 readings per second; the read_raw() code with the timeout;
   the three ways to handle the trap (software filter chosen, pigpio, a microcontroller as in v1).
13 From raw number to steady grams. Tare (offset), calibration with a known weight (the worked numbers
   123,450 / 338,950 / 431.0, predicted), grams formula, why a straight line works; cleaning: median of 5
   (worked example with a 2,600 g wild value) and why median not average; steady rule (8 within 2 g);
   WeightFilter code; the filter at work Figure 13.1 (SVG time plot with a wild reading rejected and the
   first steady point); the cost: 1.2 s delay; zero drift and auto re-tare; off-centre load, creep,
   vibration table; scale error test with check weights (measure box).

### Group 4: book/ch14-16.html
14 Price, bill and the touchscreen app. prices.csv and why a file; price in paise and why (float trap
   with an example that goes wrong); the Bill class and its printed output; the state loop (Waiting,
   Settling, Identifying, Showing, Remove) Figure 14.1; why the weight starts the camera; why "Wrong
   item" exists (7 in 100 are wrong); Tkinter in plain words, the main loop, after(100, tick) and the
   classic while-True mistake; fullscreen 800 x 480 with big buttons; Figure 14.2 sketches of the three
   screens (Place an item / Showing / Bill); what happens on "Finish" and "New customer".
15 How the program is organised. One file per job (table: file, job, chapter); start-up order; the tick
   step by step; shared state; error handling (HX711 timeout returns None, camera read fails -> message,
   low confidence -> choose); why the pieces can be tested alone (filter and bill on a laptop with
   made-up numbers, the model with saved photos, only hx711.py and camera.py need the hardware); the
   simulated-scale flag for laptop demos; the systemd autostart; Figure 15.1 the call graph.
16 Power, frame and the physical build. 5 V 3 A and the lightning symbol; current draw; camera height
   35 cm and the LED strip; the MDF frame from v1 reused; the tray resting only on the cell; cable
   routing; the screen mounted at a slant; Figure 16.1 side view of the kiosk with dimensions.

### Group 5: book/ch17.html  "The complete code"
   A one-page map (table of every file, function, class with one-line purpose); a top-to-bottom reading
   guide with Why boxes for the non-obvious choices; then EVERY source file from book/src embedded in
   full inside <pre><code> (escaped, verified identical); then "How to run it" (laptop: prepare_dataset,
   gradient_check, train; Pi: calibrate, kiosk_app; what each prints).

### Group 6: book/ch18-21.html
18 How I built and tested it, step by step. Nine phases with numbered micro-steps (0 parts, 1 laptop
   software, 2 dataset crops, 3 CNN code and gradient check, 4 training and tuning, 5 Pi setup, 6 HX711
   wiring and calibration, 7 app integration, 8 full kiosk test, 9 interview prep), each step one or two
   sentences, each phase ending with "What I saw" (predicted values) and "What I recorded" (plot, video,
   commit). Figure 18.1 the phases as a flow. A "done when" checklist table.
19 Problems and fixes. Troubleshooting table (at least 25 rows): works on test photos but not on the
   kiosk; two items mixed up; training accuracy high validation low; loss nan; weight jumps; never zero;
   off by a percentage; changes when moved; goes down when added; screen freezes; photo shows a hand;
   Pi restarts; camera not found (/dev/video0, permissions); GPIO permission on Bookworm; wrong Python
   package (RPi.GPIO vs rpi-lgpio); BGR/RGB swap; shapes mismatch after flatten; slow training (loops);
   memory error with a big batch; tkinter not found; display stays black (DSI cable); touch not working;
   weights.npz not found; prices.csv missing a class; etc. Then four Design story boxes (three devices
   became one; detection boxes became classification crops; the float money bug; the ESP8266 timing
   versus the Pi timing) and two build-problem stories using predicted values.
20 The design journey, limits and what I would improve. Version 1 to version 2 table (first idea,
   problem found, change made, why better, what it cost) covering: laptop -> Pi; ESP8266 + Wi-Fi ->
   HX711 on GPIO; YOLOv5x -> own NumPy CNN; 14 classes -> 12; float rupees -> paise; one reading ->
   filtered steady weight; no correction -> Wrong item button; hard-coded paths -> config files; the
   "how to tell it as a story" box; limits table (12 items only, one item at a time, accuracy measured
   on test crops not in a shop, look-alike items, hobby-grade scale, trusts the customer, no payment);
   improvements (not-sure top 3 already done; collect kiosk photos; use weight as a hint; quantised
   weights; MobileNet with TFLite for a product; certified scale; UPI QR for the total; photo kept with
   each bill line); "what I learned".
21 Interview questions and the one-page cheat sheet. About 65 questions with short confident
   first-person answers, grouped: big picture (6), Raspberry Pi and hardware (10, including 40-pin
   questions: why GPIO 5 and 6, why 3.3 V, what are pins 27 and 28, why no analog, what does rpi-lgpio
   do, power), images and OpenCV (5), the CNN (12 including backward pass of conv and pool, parameter
   count, einsum), training and data (10 including the split-by-photo reason, augmentation, overfitting,
   92.6%, confusion pair), running on the Pi (5), HX711 and weighing (10), the app (5), honest ones (is it
   finished, hardest part, what would you change, why from scratch when a framework would be better).
   Then the cheat sheet: two-column layout (<div class="kv">) with Numbers (layers, weights, pins,
   thresholds, calibration, accuracy), Formulas (<pre>), Words table, and "the five things to say
   clearly".
