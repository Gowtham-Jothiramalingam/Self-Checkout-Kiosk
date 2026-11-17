# Writing conventions for the Self-Checkout Kiosk book (READ FULLY BEFORE WRITING ANYTHING)

## What this book is
A complete, beginner-level book about the project on the reader's resume:

  Edge-AI Self-Checkout Kiosk            Raspberry Pi 4 · Python · NumPy · OpenCV · HX711
  - Built a self-checkout kiosk that uses image classification to identify 12 Indian fruits and
    vegetables and calculates the price from a load cell.
  - Implemented a CNN image classifier from scratch in Python, reaching 92.6% test accuracy and
    running on-device on the Raspberry Pi 4.
  - Connected the HX711 load cell directly to the Pi and filtered the readings for stable weights,
    then built a touchscreen app that shows an itemised bill.

The reader built version 1 of this project (YOLOv5 + ESP8266 + laptop, see V1_SUMMARY.md), forgot the
details, and now needs version 2 (the resume version) explained as a finished project. After reading, they
must feel the project is complete and be able to explain every part and every "why" in an interview.

## Voice and language (very important)
- First person, finished-project voice: "I built", "the kiosk does", "I chose X because". Never "you could",
  never "the plan is". Version 1 is told in the past ("my first version used an ESP8266...").
- Simple everyday English. One idea per sentence. Short sentences (about 15-20 words).
- Every technical word gets a one-line plain explanation the FIRST time it appears in a chapter
  (e.g. "softmax, which turns scores into chances that add up to 1"). Assume a beginner in everything.
- Give the intuition, the why, and the how, woven into normal text. Use a small analogy when an idea is new.
- No fluff, no repetition, no motivational talk. Dense but readable.
- Do not use em-dashes or en-dashes anywhere. Use commas or a new sentence.

## HTML format (each chapter file is a FRAGMENT, no <html>, <head> or <body>)
Each chapter:
```html
<section class="chapter" id="ch7">
<h1><span class="num">7</span> The CNN, layer by layer</h1>
<p class="small">Short version: ...one or two sentences...</p>
<h2>...</h2>
...
</section>
```
Boxes (use them often, they are the heart of the book):
```html
<div class="box why"><div class="label">Why?</div><p>...</p></div>
<div class="box tip"><div class="label">Interview tip</div><p>...</p></div>
<div class="box careful"><div class="label">Be careful</div><p>...</p></div>
<div class="box measure"><div class="label">Measured value (predicted, replace with your own number after your test)</div><p>...</p></div>
<div class="box story"><div class="label">Design story</div><p>...</p></div>
```
- Tables: plain <table><thead><tr><th>..</th></tr></thead><tbody>..</tbody></table>.
- Code: <pre><code>...</code></pre>. Escape &lt; &gt; &amp; inside code.
- Figures: inline SVG, width 700, simple boxes/arrows/text, colours #0f7c8c (teal), #d9822b (orange),
  #5b7083 (grey), #1c2b33 (text), fill #e9f3f6 for boxes. Wrap in <figure> with
  <figcaption>Figure N.M. ...</figcaption> (N = chapter number). SVG text: font-family "DejaVu Sans",
  font-size 13. Self-contained SVG only (no external refs, no scripts). Draw every figure the brief lists.
- Headings: one h1 per chapter. h2 for sections, h3 for sub-sections. The assembler builds the contents
  page from h1 and h2, so make h2 titles meaningful.
- No images from the internet. No JavaScript. No external CSS.

## The "measured value" rule
Numbers that only a real run or a real test can give (dataset counts, accuracy, confusion pairs, training
time, prediction time on the Pi, calibration numbers, scale error, filter settle time) are given as the
predicted values from the NUMBERS SHEET below, inside a "measure" box, worded as "In my run the test
accuracy was 92.6% (262 of 283)". The box label already says "predicted, replace after your test".
Design numbers (image size, layer sizes, pins, thresholds, window sizes) are facts and need no box.

## NUMBERS SHEET (canonical: every chapter and every code file must use exactly these)

### Hardware
- Computer: Raspberry Pi 4 Model B, 4 GB RAM, Raspberry Pi OS Bookworm 64-bit, Python 3.11.
- Camera: Logitech C270 USB webcam, 640 x 480, mounted 35 cm above the tray, looking straight down.
- Light: a small LED strip under the camera so every photo has the same light.
- Load cell: 5 kg bar-type load cell (4 wires: red E+, black E-, white A-, green A+).
- HX711 board (green), RATE pin left as shipped = 10 readings per second, gain 128 on channel A.
- Touchscreen: official Raspberry Pi 7-inch touch display, 800 x 480, DSI ribbon, powered from the Pi's
  5 V (pin 2) and GND (pin 6) with two jumper wires.
- Power: official 5 V 3 A USB-C supply. Measured draw with screen and camera: about 1.1 A.
- Frame: MDF box from version 1, blue plastic tray resting only on the load cell.
- Version 1 parts no longer used: ESP8266 NodeMCU, the laptop.

### Raspberry Pi 4 wiring (40-pin header, physical pin numbers)
- HX711 VCC -> 3V3 (pin 1).  HX711 GND -> GND (pin 6).
- HX711 DT  -> GPIO 5 (pin 29).  HX711 SCK -> GPIO 6 (pin 31).
- Screen 5 V -> pin 2, screen GND -> pin 6 (or pin 9). Camera -> any USB port.
- Never 5 V into a GPIO. The HX711 is powered from 3.3 V so its DT pin never exceeds 3.3 V.
Full 40-pin header (physical pin: function), odd pins on the inside row, even pins on the outside row:
1 3V3, 2 5V, 3 GPIO2 (SDA), 4 5V, 5 GPIO3 (SCL), 6 GND, 7 GPIO4, 8 GPIO14 (TXD), 9 GND, 10 GPIO15 (RXD),
11 GPIO17, 12 GPIO18 (PWM), 13 GPIO27, 14 GND, 15 GPIO22, 16 GPIO23, 17 3V3, 18 GPIO24, 19 GPIO10 (MOSI),
20 GND, 21 GPIO9 (MISO), 22 GPIO25, 23 GPIO11 (SCLK), 24 GPIO8 (CE0), 25 GND, 26 GPIO7 (CE1),
27 ID_SD (reserved), 28 ID_SC (reserved), 29 GPIO5, 30 GND, 31 GPIO6, 32 GPIO12 (PWM), 33 GPIO13 (PWM),
34 GND, 35 GPIO19, 36 GPIO16, 37 GPIO26, 38 GPIO20, 39 GND, 40 GPIO21.
Pi facts: all GPIO are 3.3 V; about 16 mA per pin, 50 mA total safe; no analog input at all (that is why
the HX711 exists); pins 27 and 28 are reserved for HAT ID EEPROM, do not use; Linux is not a real-time
system, so pin timing can pause for milliseconds at any moment.

### Software stack
- Laptop (training): Python 3.11, numpy, opencv-python, matplotlib. CPU only (Intel i5 laptop).
- Pi (kiosk): python3, python3-numpy, python3-opencv (apt), python3-tk, rpi-lgpio (gives the RPi.GPIO API
  on Bookworm). No PyTorch, no TensorFlow anywhere in version 2.
- Repository layout:
  README.md
  classifier/  cnn_numpy.py  prepare_dataset.py  train.py  gradient_check.py  weights.npz  metrics.json
  kiosk/       hx711.py  weight_filter.py  calibrate.py  camera.py  bill.py  kiosk_app.py  prices.csv  config.json
  docs/        book/  photos/  wiring.md
  v1/          the old YOLOv5 + ESP8266 + Tkinter code, kept for the design story

### Dataset (predicted, replace after your real run)
- Source photos: 636 top-view photos of 14 items from version 1, each with YOLO label files (class, box).
- Version 2 makes a CLASSIFICATION set by cropping every labelled box out of every photo, padding to a
  square, resizing to 64 x 64. Predicted crops: 1,850 after dropping two classes.
- The two dropped classes: Capsicum (15 photos) and Chilly (17 photos), too few photos to learn from.
  That leaves 12 classes, in this fixed order (class index 0..11):
  0 Apple, 1 Beetroot, 2 Brinjal, 3 Brinjal White, 4 Coconut, 5 Guava, 6 Lemon, 7 Mosambi, 8 Onion,
  9 Pomegranate, 10 Potato, 11 Tomato.
- Predicted crops per class: Apple 230, Beetroot 150, Brinjal 280, Brinjal White 100, Coconut 120,
  Guava 95, Lemon 160, Mosambi 170, Onion 140, Pomegranate 80, Potato 170, Tomato 155 (total 1,850).
- Split BY PHOTO (all crops of one photo go to the same pile), 70 / 15 / 15:
  train 1,290 crops, validation 277, test 283.
- Preparation (identical at training and at the kiosk): crop -> pad to square with the border colour ->
  BGR to RGB -> resize 64 x 64 with INTER_AREA -> float32 / 255 -> shape (1, 3, 64, 64).

### The CNN (design facts)
Input 3 x 64 x 64
Conv1  8 filters 3x3, no padding, stride 1 -> 8 x 62 x 62, ReLU         weights 8*27+8   = 224
MaxPool 2x2 -> 8 x 31 x 31
Conv2  16 filters 3x3 -> 16 x 29 x 29, ReLU                              weights 16*72+16 = 1,168
MaxPool 2x2 -> 16 x 14 x 14
Conv3  32 filters 3x3 -> 32 x 12 x 12, ReLU                              weights 32*144+32 = 4,640
MaxPool 2x2 -> 32 x 6 x 6
Flatten -> 1,152
Dense1 1,152 -> 64, ReLU                                                 weights 1152*64+64 = 73,792
Dense2 64 -> 12, softmax                                                 weights 64*12+12 = 780
Total weights 80,604. Multiplications per photo: conv1 830,304 + conv2 968,832 + conv3 663,552 +
dense 73,728 + 768 = about 2.5 million.
- He initialisation, float32, cross-entropy loss, SGD with momentum 0.9, learning rate 0.01, batch 32,
  40 epochs, shuffle every epoch, keep the weights of the best validation epoch.
- Augmentation on training crops only: random horizontal flip, random shift up to 4 pixels,
  brightness scale 0.85 to 1.15.
- Convolution implemented by looping over the 9 filter cells and using np.einsum over all images and
  positions at once (no Python loop over pixels). Backward pass written by hand for every layer.
- Gradient check: central difference with eps 1e-5 in float64 on 20 random weights per layer.
- Function and class names used everywhere: Conv, ReLU, MaxPool, Flatten, Dense, Net, softmax(z),
  loss_and_grad(scores, y), prepare_image(bgr) -> (1,3,64,64), load_weights(path), save_weights(path),
  predict(net, x) -> (class_index, confidence), class names list CLASSES.

### Training results (predicted, replace after your real run)
- Gradient check: biggest relative difference 4.9e-07 (float64, real run, see "Added in chapters 6-9").
- Training on the laptop CPU: about 45 s per epoch, 30 minutes for 40 epochs.
- Best validation epoch: 34. Training accuracy 98.1%, validation 93.5%, test 92.6% (262 of 283 correct).
- Chance level 1/12 = 8.3%.
- Confusion matrix: 21 test mistakes in total. Most confused pair Mosambi <-> Lemon (7 mistakes, both
  round and green-yellow), Brinjal <-> Brinjal White (4), Onion <-> Potato (3), Guava <-> Mosambi (2),
  the rest scattered one each. Best classes: Tomato, Coconut, Pomegranate at 100%.
- Per-class test accuracy (predicted): Apple 94, Beetroot 91, Brinjal 90, Brinjal White 86, Coconut 100,
  Guava 87, Lemon 88, Mosambi 85, Onion 90, Pomegranate 100, Potato 93, Tomato 100 (percent).
- Weights file weights.npz: 10 arrays, about 320 kB.
- Prediction on the Pi 4: forward pass 18 ms per 64 x 64 photo in float32 NumPy; capture + prepare +
  predict about 60 ms. On the laptop the forward pass is 4 ms.
- First attempt without augmentation: train 99.6%, validation 84.2% (overfitting). Augmentation and the
  smaller 64-unit dense layer brought validation to 93.5%.

### HX711 and weighing (predicted, replace after your real test)
- Calibration: empty tray raw 123,450 (the offset). With a known 500 g weight: 338,950.
  counts_per_gram = (338,950 - 123,450) / 500 = 431.0. Saved in kiosk/config.json.
  (Version 1 used a scale factor of 430 on the ESP8266, so this agrees.)
- grams = (raw - offset) / counts_per_gram.
- Filter: median of the newest 5 readings, then "steady" when the newest 8 cleaned readings differ by
  less than 2 g; the weight used is their average. At 10 readings per second the first steady value
  comes about 1.2 s after the item is put down.
- Wild readings from the Linux timing trap (SCK high for over 60 microseconds resets the chip): about
  one every 2 minutes in a test; every one removed by the median.
- Scale error with 100 g, 500 g, 1 kg and 2 kg check weights: within 2 g everywhere, worst 2 g at 1 kg.
- Zero drift: about 1 g per hour; the app re-tares when the tray has been empty and steady for 5 s.
- Item present threshold: 20 g. Item removed threshold: below 10 g.
- read_raw has a 1 s timeout and returns None if DT never goes low.

### Price table kiosk/prices.csv (rupees per kg, from version 1)
Apple 240, Beetroot 50, Brinjal 40, Brinjal White 40, Coconut 80, Guava 80, Lemon 90, Mosambi 140,
Onion 25, Pomegranate 210, Potato 60, Tomato 35.
Money is kept as whole paise: price_paise = round(grams * rupees_per_kg * 100 / 1000).
Example: 412 g tomato = 1,442 paise = Rs 14.42.

### The app (design facts)
- Tkinter, fullscreen 800 x 480, big buttons, no typing. root.after(100, tick): the tick runs 10 times a
  second, reads the HX711, updates the filter and the state, redraws the screen.
- States: Waiting ("Place an item") -> Settling (live weight) -> Identifying (one photo, CNN) ->
  Showing (name, grams, price, buttons "Add to bill" and "Wrong item") -> Remove ("Take the item off")
  -> Waiting. "Wrong item" shows the top 3 guesses plus a full list. "Finish" shows the itemised bill
  with lines "name, grams, Rs/kg, Rs" and the total, then a "New customer" button clears it.
- Confidence rule: if the top chance is below 0.60 the screen says "Not sure, please choose" and shows
  the top 3.
- The CNN runs inside the tick; 60 ms is a short pause nobody notices.
- Time from item placed to name on screen: about 1.5 s (1.2 s settling + 0.3 s photo and prediction).
- Start-up: load weights (once) -> open camera -> set up GPIO -> read config.json -> tare (20 readings,
  2 s) -> show the first screen -> start the tick.

## ADDED DURING WRITING (later chapters and code must agree with these)
### Added in chapters 1-5
- Screen GND goes to pin 9 (pin 6 already holds the HX711 GND; one jumper per pin). Screen 5 V on pin 2.
- Jumper colours: red power, black ground, yellow DT, blue SCK. Jumpers 20 cm female-female.
  Load cell leads about 25 cm. HX711 board screwed to the base right below the Pi.
- Webcam and LED strip both in the black USB 2.0 ports. LED strip: 30 cm white, 5 V USB, always on.
- Tray 25 cm x 20 cm, blue; camera at 35 cm sees about 29 cm x 22 cm. At least 5 mm gap around the tray.
- Load cell: aluminium bar about 80 mm x 12.7 mm x 12.7 mm, 4 gauges of about 1,000 ohm, rated output
  1 mV/V, safe to about 150% of 5 kg. Bridge excitation about 3 V when the HX711 runs on 3.3 V.
  Full 5 kg about 3 mV; a 412 g tomato about 0.25 mV, x128 = about 32 mV.
  Worked raw example: 412 g -> 123,450 + 412 x 431 = 301,022 counts.
- Multimeter check of load cell wires: E+/E- about 1,000 ohm, A+/A- about 1,000 ohm, mixed pair about 750 ohm.
- micro-SD card 32 GB class 10 A1. Heat sink set on the Pi.
- Parts prices (Rs, 2025): Pi 4 4 GB 5,800; supply 800; SD 450; 7-inch screen 6,200; heat sinks 150;
  C270 1,700 (reused); load cell + HX711 250 (reused); LED strip 150; jumpers 100; screws/spacers 150;
  MDF frame + tray 600 (reused). Total 16,350; new parts 13,800.
- Pi setup: hostname kiosk, user kiosk (ssh kiosk@kiosk.local), time zone Asia/Kolkata, Desktop Autologin,
  Screen Blanking off, VNC only during setup. Repo cloned to /home/kiosk/Self-Checkout-Kiosk.
- apt: sudo apt remove -y python3-rpi.gpio; sudo apt install -y python3-numpy python3-opencv python3-tk
  python3-rpi-lgpio. Pi versions printed: numpy 1.24.2, OpenCV 4.6.0. Code must work on NumPy 1.24.
- Laptop: python -m venv .venv; pip install numpy opencv-python matplotlib.
- Camera test prints "True (480, 640, 3)". The app throws away a few warm-up frames after opening the camera.
- Weights copy: scp classifier/weights.npz kiosk@kiosk.local:~/Self-Checkout-Kiosk/classifier/
  The final weights.npz and metrics.json are also committed to the repository.
- Autostart: systemd USER service ~/.config/systemd/user/kiosk.service, WorkingDirectory
  /home/kiosk/Self-Checkout-Kiosk/kiosk, Environment=DISPLAY=:0,
  ExecStart=/usr/bin/python3 /home/kiosk/Self-Checkout-Kiosk/kiosk/kiosk_app.py, Restart=on-failure,
  RestartSec=3, WantedBy=default.target. Logs: journalctl --user -u kiosk.service -f.
  => kiosk_app.py must find every file relative to its own folder, and import cnn_numpy from ../classifier.
- Boot to "Place an item": about 35 s (predicted); app start-up itself about 4 s including the 2 s tare.
- Under-voltage lightning symbol below about 4.63 V. Power draw 1.1 A = about 5.5 W.
- Pi forward pass is about 4x slower than the laptop (18 ms vs 4 ms); training on the Pi would take ~2 h.
### Added in chapters 6-9 (and by writing classifier/cnn_numpy.py + gradient_check.py early; both are tested)
- book/src/classifier/cnn_numpy.py and gradient_check.py ALREADY EXIST and pass their tests. Chapter 9 quotes
  them verbatim. Do not change their code without re-generating the excerpts in ch06-09.html (chapters 6, 9).
- Extra names in cnn_numpy.py: IMAGE_SIZE = 64, CROP_MARGIN = 0.10, crop_with_margin(bgr, box, margin),
  conv_forward_slow(x, W, b), top_k(net, x, k=3) -> [(class_index, chance), ...], Net.get_weights(),
  Net.set_weights(dict), Net.count_weights(), Net(seed=0, dtype=np.float32), Conv(..., need_dx=False) for
  conv1. save_weights/load_weights are Net METHODS. Array names in weights.npz: conv1_W, conv1_b, conv2_W,
  conv2_b, conv3_W, conv3_b, dense1_W, dense1_b, dense2_W, dense2_b. Dense W shape (n_in, n_out).
  MaxPool uses argmax (one winner per block), not "== max". The net has 13 layers in Net.layers.
- Where the crop box comes from: training = the hand-drawn YOLO box; kiosk = find_item_box(bgr) in
  kiosk/camera.py (colour mask: HSV, tray = hue 90..130, S > 80, V > 50; item = not tray; clean specks with a
  5 x 5 opening; box of the biggest blob; returns (x, y, w, h) or None; about 2 ms). Both then use
  crop_with_margin (box grown 10% per side) and prepare_image. Pad colour = per-channel median of the crop's
  outer ring of pixels. Predicted: mask boxes vs hand boxes on 100 photos, mean IoU 0.86, item found in 100/100.
- Gradient check is REAL (seed 0): biggest relative difference 4.9e-07, 5 of 200 weights re-measured with
  eps/10 because of ReLU/max-pool kinks (first-layer weights); loss on the random data 6.3940. Use 4.9e-07
  (not 3e-7) everywhere.
- Conv layers do 97% of the multiplications (2,462,688 of 2,537,184), not 98%. Dense1 has 92% of the weights;
  the three conv layers have 6,032 weights (7.5%).
- Each number of the final 6 x 6 maps sees about 22 x 22 input pixels.
- Training curve (predicted): epoch 1 train 21.4% / val 26.0%; epoch 10 74.8 / 79.1; epoch 20 92.1 / 89.8;
  epoch 34 98.1 / 93.5 (259 of 277); epoch 40 98.5 / 92.8. First batch loss about 4.9 (random He weights are
  worse than guessing at first; ln 12 = 2.48 is the "pure guessing" landmark), epoch-1 average loss 2.31,
  train loss 0.07 and validation loss 0.24 at epoch 34. 41 batches per epoch, 1,640 updates in 40 epochs.
- First (overfitting) attempt: no augmentation, Dense1 with 128 units, 155,164 weights, train 99.6% / val 84.2%.
- Slow conv vs fast conv for conv2 on one picture: 85 ms vs 0.7 ms (predicted, about 120x).
- YOLOv5x of version 1: about 86 million weights, about 170 MB.
- cnn_numpy.py is about 310 lines.
### Added in chapters 10-13 (and kiosk/hx711.py + kiosk/weight_filter.py written early; both tested)
- book/src/kiosk/hx711.py and weight_filter.py ALREADY EXIST and are quoted verbatim in ch12/ch13. Regenerate the
  excerpts if their code changes. hx711.py: HX711(dt_pin=5, sck_pin=6) with is_ready(), read_raw(timeout=1.0),
  close(); ON_PI flag; _FakeGPIO stand-in when RPi.GPIO is missing; SimulatedHX711(offset=123_450,
  counts_per_gram=431.0, noise_g=0.4, wild_every=1200) with set_load(grams), read_raw(), close().
  weight_filter.py: constants MEDIAN_N=5, STEADY_N=8, STEADY_BAND_G=2.0, ITEM_ON_G=20.0, ITEM_OFF_G=10.0,
  RETARE_AFTER=50; class WeightFilter(offset, counts_per_gram) with to_grams(raw), add(raw)->grams (None keeps
  last), .steady, .weight (mean of 8 cleaned), tare(raw_readings) (median), _auto_retare(). Demo prints
  "steady weight 412.1 g, 1.2 s after the item was put down". Steady = max-min of 8 cleaned < 2 g.
- Start-up tare = median of 20 readings. calibrate.py (to write in turn 5): prompts "Empty the tray and press
  Enter." then "Put the 500 g weight in the middle of the tray and press Enter.", 20 readings each, median,
  prints counts_per_gram, writes offset and counts_per_gram into kiosk/config.json.
- Dataset (prepare_dataset.py, turn 5): reads dataset/images/*.jpg + dataset/labels/*.txt (YOLO format:
  class cx cy w h as fractions; v1 class ids 0 Apple .. 13 Tomato in the 14-class v1 order: Apple, Beetroot,
  Brinjal, Brinjal White, Capsicum, Chilly, Coconut, Guava, Lemon, Mosambi, Onion, Pomegranate, Potato,
  Tomato), maps to the 12 CLASSES BY NAME, drops Capsicum/Chilly. 604 photos remain. Split by photo, 70/15/15
  within each class, seed 42, writes split.csv; test pile = 91 photos. Each crop: crop_with_margin + prepare_image.
  Output classifier/data/dataset_64.npz with uint8 arrays x_train/x_val/x_test (N,3,64,64) and y_* (int).
  Predicted dropped crops: Capsicum 41, Chilly 66; 14-class trial Chilly 4/9, Capsicum 3/6 on test.
  Random split BY CROP (leaky) gave 97.2% test (4.6 points too high).
- Augmentation: flip with probability 0.5; shift up to 4 px; brightness x U(0.85, 1.15), clipped to 0..1.
- TEST CONFUSION MATRIX (rows true, cols predicted, CLASSES order). Test counts per class: Apple 36, Beetroot 23,
  Brinjal 31, Brinjal White 14, Coconut 25, Guava 15, Lemon 26, Mosambi 27, Onion 21, Pomegranate 17, Potato 15,
  Tomato 33 (=283). Diagonal 34,21,28,12,25,13,23,23,19,17,14,33 (=262). Mistakes: Apple->Pomegranate 1,
  Apple->Tomato 1, Beetroot->Onion 1, Beetroot->Pomegranate 1, Brinjal->Brinjal White 2, Brinjal->Onion 1,
  Brinjal White->Brinjal 2, Guava->Mosambi 2, Lemon->Mosambi 3, Mosambi->Lemon 4, Onion->Potato 2,
  Potato->Onion 1 (=21). Mosambi recall 23/27=85%, precision 23/28=82%. Always-Brinjal baseline 31/283=11%.
  92.6% +/- 2 standard errors = about 89% to 96%.
- Confidence rule on test: 266 crops >= 0.60, 256 of them right (96.2%); 17 below 0.60, 6 right; rule catches
  11 of 21 mistakes; for 15 of 17 unsure crops the right class was in the top 3. Threshold chosen on validation.
- Kiosk end-to-end test: 60 new items (5 per class): 54 right first time (90%), 4 of 6 errors Mosambi/Lemon,
  5 of 6 right in top 3, mask found the item 60/60.
- Pi timings (predicted): conv1 6.0 ms, conv2 6.5, conv3 4.0, pool/ReLU/flatten 1.0, dense 0.5 -> 18 ms.
  First call about 40 ms, so the app makes one dummy prediction at start-up. Net() + load_weights 0.15 s;
  importing numpy+cv2 about 1.2 s. 60 ms = fresh frame 33 + box 3 + prepare 2 + forward 18 + screen 4.
  camera.take_photo() flushes buffered frames with grab() then read()s a fresh frame. Forward keeps ~0.5 MB.
- HX711: GPIO call about 3 us, one reading (25 pulses) about 0.4 ms. 30-min test with 500 g: 18,000 readings,
  15 wild (about 1 in 1,200), all removed. Wild example raw 1,244,050 (= 2,600 g). Two's complement examples:
  301,022 = 0000 0100 1001 0111 1101 1110. 10 SPS settling 400 ms. 1 count = about 1.4 nV at the input.
  After several seconds of None, the app shows "Scale not responding".
- Weighing (predicted): 50 placements, first steady value mean 1.2 s (1.0 to 2.1 s). Drift about 1 g/h over 4 h,
  mostly first hour. Corners with 500 g: 498.4 to 501.6 g. Creep: 2 kg for 10 min +0.8 g. Vibration jumps up
  to 15 g for 0.5 s. Cable touching tray: 500 g read 470 g. Check weights (avg of 5): 100 -> 100.6, 500 -> 499.2,
  1000 -> 1002.0, 2000 -> 1998.6. 2 g at Rs 240/kg = 48 paise. Not legal for trade (Legal Metrology).
### Added in chapters 14-16 (bill.py, camera.py, kiosk_app.py, prices.csv, config.json written early; tested)
- book/src/kiosk/bill.py, camera.py, kiosk_app.py, prices.csv, config.json ALREADY EXIST; ch14/ch15 quote them
  verbatim (load_prices, check_prices, price_paise, rupees, Bill, KioskApp.tick/step/identify/__init__,
  prices.csv, config.json). Regenerate excerpts if they change.
- bill.py: load_prices(path) (CSV header "item,rupees_per_kg"), check_prices(prices, CLASSES) raises ValueError,
  price_paise(grams, rpk) = (round(grams) * rpk * 100 + 500) // 1000 (whole grams, half paisa rounds UP, never
  Python round on paise), money(paise) '14.42', rupees(paise) 'Rs 14.42', Bill.add/remove_last/clear/
  total_paise/text(). Sample bill: Tomato 412 g 14.42, Onion 1033 g (from 1032.6) 25.83, Apple 618 g 148.32,
  Lemon 97 g 8.73, total 197.30. Float examples: 8.78 + 6.3 = 15.079999999999998; 14.42 + 12.15 + 31.2 =
  57.769999999999996.
- config.json keys: offset 123450, counts_per_gram 431.0, calibrated_with_grams 500, camera_index 0,
  confidence_threshold 0.60, item_on_grams 20, item_off_grams 10. (camera index currently fixed to 0 in app.)
- camera.py: WIDTH 640, HEIGHT 480, WARM_UP_FRAMES 5, FLUSH_FRAMES 4, MIN_ITEM_PIXELS 400, TRAY_LOW (90,80,50),
  TRAY_HIGH (130,255,255); Camera(index).take_photo()/close(); FakeCamera (blue tray + coloured circle, .colour);
  find_item_box(bgr) -> (x,y,w,h) or None (5x5 opening, biggest contour).
- kiosk_app.py: flags --simulate --windowed; keys 1-9,0,Q,W put demo items, space removes; Ctrl+Q quits.
  States waiting/settling/identifying/showing/choosing/remove/bill ("Choose" screen in the book). TICK_MS 100,
  TARE_READINGS 20, NO_READING_LIMIT 30 (3 s -> "Scale not responding"), CHANGED_G 5 (steady weight > 5 g from
  shown item -> Settling again). Tick reads only if is_ready() (never blocks). Choosing an item adds it at once.
  "Could not see the item, please choose" when no box. Bill screen ignores the scale. App start-up about 4 s.
  REAL test run (Xvfb, --simulate): Waiting, Settling, Showing, Remove, Waiting, Choose, Bill; total Rs 40.25.
  SimulatedHX711 now also has is_ready().
- Laptop note: in this build container only /usr/bin/python3.12 has tkinter (numpy+opencv-headless installed for it).
- Physical (ch16): base MDF 40 x 30 cm, 12 mm; camera post 50 cm at the back with an arm; tray top ~5 cm above
  base; screen at the front leaning back ~30 degrees; Pi screwed to the screen's back standoffs; HX711 on the base
  between screen and load cell; load cell fixed end on a 10 mm spacer with 2 x M5, tray on the free end with
  2 x M4; cable clips every 10 cm; power cable strain relief. Currents: Pi ~0.5 A, screen ~0.4 A, C270 ~0.1 A,
  LED ~0.1 A, HX711 < 2 mA; total 1.1 A at 5.1 V idle, ~1.3 A peak during photo+CNN, never below 5.0 V.
  CPU 52 C after start, 58 C after an hour (throttle at 80 C), vcgencmd measure_temp.
