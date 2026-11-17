# Edge-AI Self-Checkout Kiosk (version 2)

A self-checkout kiosk for loose fruit and vegetables. A customer puts one item on the tray;
the kiosk weighs it with a load cell, recognises it with a small CNN written from scratch in
NumPy, and adds a line to an itemised bill on a touchscreen. Everything runs on one
Raspberry Pi 4. No PyTorch, no TensorFlow, no cloud.

- 12 classes: Apple, Beetroot, Brinjal, Brinjal White, Coconut, Guava, Lemon, Mosambi,
  Onion, Pomegranate, Potato, Tomato
- CNN: 3 conv layers (8, 16, 32 filters of 3 x 3) + 2 dense layers, 80,604 weights,
  64 x 64 RGB input, every forward and backward pass hand-written in NumPy
- Scale: 5 kg bar load cell + HX711, read directly on GPIO 5 (DT) and GPIO 6 (SCK),
  median-of-5 filter, "steady" when 8 readings agree within 2 g
- App: Tkinter, fullscreen 800 x 480, money kept in whole paise

## Folders

```
classifier/   cnn_numpy.py         the network, image preparation, predict (used by BOTH machines)
              prepare_dataset.py   v1 photos + YOLO boxes -> 64 x 64 crops, split by photo
              train.py             training, best epoch, one test, weights.npz + metrics.json
              gradient_check.py    proof that the backward pass is correct
kiosk/        hx711.py             read the HX711 bit by bit (+ simulated scale)
              weight_filter.py     raw counts -> steady grams, auto re-tare
              calibrate.py         offset and counts_per_gram -> config.json
              camera.py            one fresh photo, find the item on the blue tray
              bill.py              prices.csv, paise, the itemised bill
              kiosk_app.py         the touchscreen app
              prices.csv           rupees per kg
              config.json          calibration and settings
```

## Wiring (Raspberry Pi 4, physical pin numbers)

| HX711 | Pi pin | | Screen | Pi pin |
|---|---|---|---|---|
| VCC | 1 (3.3 V) | | 5V | 2 |
| GND | 6 | | GND | 9 |
| DT | 29 (GPIO 5) | | DSI ribbon | DSI connector |
| SCK | 31 (GPIO 6) | | | |

Load cell: red E+, black E-, white A-, green A+. Power the HX711 from 3.3 V, never 5 V.

## On the laptop (training)

```
python -m venv .venv
source .venv/bin/activate              (Windows: .venv\Scripts\activate)
pip install numpy opencv-python matplotlib
cd classifier
python cnn_numpy.py                    # fast conv equals slow conv: True; 80604 weights
python gradient_check.py               # ... biggest relative difference ~5e-07, PASS
python train.py --synthetic            # proves the code learns, writes synthetic_run/
python prepare_dataset.py --images ../dataset/images --labels ../dataset/labels
python train.py                        # 40 epochs, writes weights.npz and metrics.json
scp weights.npz kiosk@kiosk.local:~/Self-Checkout-Kiosk/classifier/
```

## On the Raspberry Pi (Raspberry Pi OS Bookworm 64-bit)

```
sudo apt remove -y python3-rpi.gpio
sudo apt install -y python3-numpy python3-opencv python3-tk python3-rpi-lgpio
git clone https://github.com/Gowtham-Jothiramalingam/Self-Checkout-Kiosk.git
cd Self-Checkout-Kiosk/kiosk
python3 hx711.py                       # 20 raw readings
python3 camera.py                      # saves camera_test.jpg with the item box
python3 calibrate.py                   # needs a 500 g weight, writes config.json
python3 kiosk_app.py                   # the kiosk (Ctrl+Q quits)
```

Autostart: copy the unit file from chapter 5 of the book to
`~/.config/systemd/user/kiosk.service`, then
`systemctl --user daemon-reload && systemctl --user enable --now kiosk.service`.

## Laptop demo of the app

```
cd kiosk
python3 bill.py                        # doctests + a sample bill
python3 weight_filter.py               # doctest + a made-up weighing with one wild reading
python3 kiosk_app.py --simulate --windowed
```
Keys 1-9, 0, Q, W put an item on the simulated tray; the space bar takes it off.
The fake camera draws coloured circles, so the names it shows are meaningless; the demo
tests the app's states, weights and bill. `classifier/weights.npz` must exist (train first,
or copy `classifier/synthetic_run/weights.npz` for a demo).

## Results

The fruit and vegetable numbers in the book (92.6% test accuracy, 262 of 283 crops,
18 ms per prediction on the Pi, 431.0 counts per gram, within 2 g from 100 g to 2 kg) are
the values predicted for my run, shown in purple boxes. Re-running `prepare_dataset.py` and
`train.py` on the real photos produces `metrics.json` with the real values to replace them.
