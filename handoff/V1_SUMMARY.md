# Version 1 of the kiosk: what really existed (facts from the old repo and the project report)

Use these facts for the "design journey" chapters and the v1 folder. They are TRUE and can be stated as such.

- Built as a B.Tech major project at SASTRA (2024) by a small team; the reader did the GUI, the load cell
  and the integration, and took part in the dataset work.
- Model: YOLOv5x (Ultralytics, PyTorch) trained on Google Colab GPU, batch size 16, 40 epochs.
  Dataset: 636 top-view photos of 14 Indian fruits and vegetables, taken by the team under different
  lighting, annotated with bounding boxes on MakeSense.ai, split 80/20 train/test.
  Class list and photo counts: Apple 60, Beetroot 41, Brinjal 60, Brinjal White 30, Capsicum 15,
  Chilly 17, Coconut 90, Guava 30, Lemon 39, Mosambi 60, Onion 40, Pomegranate 30, Potato 60, Tomato 64.
  Results: precision 92.0%, recall 91.9%, mAP@0.5 92.08%, mAP@0.5:0.95 61.7%. The confusion matrix showed
  Chilly (0.72) and Lemon (0.75) weakest, with background confusions.
- Hardware: 5 kg load cell + HX711 read by an ESP8266 NodeMCU (HX711 library, DT on GPIO 4, SCK on
  GPIO 5, set_scale(430), tare at start). The ESP8266 joined the phone hotspot "Gowtham" and ran a tiny
  HTTP server (ESP_MICRO.h helper); the Python script on the laptop fetched the weight with
  urllib.request.urlopen("http://192.168.43.92/") each time the user pressed "Add". The ESP8266
  returned the average of 10 readings as an integer.
- Camera: Logitech C270 webcam on top of an MDF frame, looking down at a blue tray.
- Software: one Python file Kiosk_main.py on a Windows laptop. torch.hub loaded best.pt. Tkinter GUI made
  with a designer tool (Tkinter Designer), three windows: Start, Main (ttk.Treeview with Product /
  QNTY in grams / Price in Rs, buttons Add, Remove selected, Checkout, Cancel, "TOTAL AMOUNT" text),
  Payment (a UPI QR code image, Back, Finish). Price per kg came from a CSV file my_table4.csv
  (Apple 240, Beetroot 50, Brinjal 40, Brinjal_w 40, Capsicum 120, Chilly 34, Coconut 80, Guava 80,
  Lemon 90, Mosambi 140, Onion 25, Pomegranate 210, Potato 60, Tomato 35).
  The detected class with the most boxes in the photo was taken as the item; cost = grams * rupees/kg * 0.001,
  rounded to 2 decimals and summed as floats.
- Known weaknesses of v1 (true, can be told as reasons for v2): three devices had to be on and connected
  (laptop, ESP8266, hotspot); hard-coded Windows paths; PyTorch + YOLOv5x too heavy for a small box;
  one item type per "Add"; money summed as floats; weight read only once with no steadiness check;
  no "wrong item" correction; no calibration file (constant 430 in firmware).
- The move to version 2 (the resume): everything on a Raspberry Pi 4, HX711 wired to the Pi's own pins,
  from-scratch NumPy CNN classifier on cropped single-item photos, 12 classes, touchscreen app with an
  itemised bill in paise.
