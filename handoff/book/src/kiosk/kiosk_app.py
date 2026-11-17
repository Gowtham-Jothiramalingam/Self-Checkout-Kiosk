"""kiosk_app.py - the touchscreen self-checkout app (Tkinter, 800 x 480, fullscreen).

Run on the Pi:        python3 kiosk_app.py
Run on a laptop demo: python3 kiosk_app.py --simulate --windowed
  (a simulated scale and a fake camera; keys 1-9, 0, Q, W put an item on the
   tray, the space bar takes it off)

Start-up order: load weights -> open camera -> set up GPIO -> read config.json
and prices.csv -> tare -> show the first screen -> start the tick.

The tick runs 10 times a second. Each time it reads the scale once, feeds the
filter, and moves between the five states:
  Waiting -> Settling -> Identifying -> Showing -> Remove -> Waiting
"Wrong item" (or a top chance below 0.60) opens the Choose screen; "Finish"
opens the Bill screen.
"""
import argparse
import json
import sys
import traceback
from pathlib import Path
import tkinter as tk

import numpy as np

HERE = Path(__file__).resolve().parent              # .../kiosk
CLASSIFIER_DIR = HERE.parent / "classifier"         # .../classifier
sys.path.insert(0, str(CLASSIFIER_DIR))             # so "import cnn_numpy" finds the shared layer code

from cnn_numpy import CLASSES, Net, crop_with_margin, prepare_image, top_k   # noqa: E402
from bill import Bill, check_prices, load_prices, price_paise, rupees       # noqa: E402
from weight_filter import WeightFilter                                       # noqa: E402
import camera                                                                # noqa: E402
import hx711                                                                 # noqa: E402

TICK_MS = 100              # the tick runs every 100 ms = 10 times a second
TARE_READINGS = 20         # 2 s of readings with the empty tray at start-up
NO_READING_LIMIT = 30      # 30 ticks (3 s) without a reading -> "Scale not responding"
CHANGED_G = 5.0            # a steady weight this far from the shown item means a new item

WAITING, SETTLING, IDENTIFYING, SHOWING, CHOOSING, REMOVE, BILL = (
    "waiting", "settling", "identifying", "showing", "choosing", "remove", "bill")

BG, TEXT, GREY = "#f4f7f8", "#1c2b33", "#5b7083"
TEAL, GREEN, ORANGE = "#0f7c8c", "#2f8f4e", "#d9822b"
BIG, MID, SMALL, BUTTON = ("DejaVu Sans", 40, "bold"), ("DejaVu Sans", 24), ("DejaVu Sans", 15), ("DejaVu Sans", 20, "bold")

# Laptop demo only: key -> (class name, grams, BGR colour for the fake camera).
DEMO_ITEMS = {"1": ("Apple", 618, (40, 30, 190)), "2": ("Beetroot", 260, (70, 20, 110)),
              "3": ("Brinjal", 340, (90, 30, 70)), "4": ("Brinjal White", 300, (210, 225, 230)),
              "5": ("Coconut", 540, (40, 70, 110)), "6": ("Guava", 210, (90, 200, 150)),
              "7": ("Lemon", 97, (60, 220, 230)), "8": ("Mosambi", 180, (70, 200, 170)),
              "9": ("Onion", 1032.6, (120, 110, 170)), "0": ("Pomegranate", 380, (50, 40, 170)),
              "q": ("Potato", 450, (110, 160, 200)), "w": ("Tomato", 412, (30, 40, 210))}


class KioskApp:
    def __init__(self, root, simulate=False, windowed=False):
        self.root = root
        self.simulate = simulate

        # 1. Load the weights once. The first forward pass is slow, so do a dummy one now.
        weights = CLASSIFIER_DIR / "weights.npz"
        if not weights.exists():
            sys.exit(f"{weights} not found. Train on the laptop, then copy it with scp.")
        self.net = Net()
        self.net.load_weights(weights)
        top_k(self.net, np.zeros((1, 3, 64, 64), np.float32))

        # 2. Open the camera (it throws away its first dark frames).
        self.camera = camera.FakeCamera() if simulate else camera.Camera(0)

        # 3. Set up the GPIO pins for the HX711 (or the simulated scale).
        # 4. Read the calibration and settings, and the price table.
        self.config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
        self.prices = load_prices(HERE / "prices.csv")
        check_prices(self.prices, CLASSES)
        self.threshold = float(self.config["confidence_threshold"])
        self.on_g = float(self.config["item_on_grams"])
        self.off_g = float(self.config["item_off_grams"])
        if simulate:
            self.scale = hx711.SimulatedHX711(self.config["offset"], self.config["counts_per_gram"])
        else:
            self.scale = hx711.HX711()
        self.filter = WeightFilter(self.config["offset"], self.config["counts_per_gram"])

        # 5. Tare: the tray must be empty now.
        self.filter.tare([self.scale.read_raw() for _ in range(TARE_READINGS)])

        # 6. The window and the first screen, then 7. start the tick.
        self.bill = Bill()
        self.item = None             # the item being shown: {"grams": .., "guesses": [(index, chance), ..]}
        self.state = None
        self.no_reading = 0
        self.build_window(windowed)
        self.go(WAITING)
        self.root.after(TICK_MS, self.tick)

    # ------------------------------------------------------------------ window
    def build_window(self, windowed):
        r = self.root
        r.title("Self-checkout kiosk")
        r.configure(bg=BG)
        if windowed:
            r.geometry("800x480")
        else:
            r.attributes("-fullscreen", True)
            r.config(cursor="none")                  # a touchscreen needs no mouse pointer
        r.bind("<Control-q>", lambda e: self.quit())
        if self.simulate:
            r.bind("<Key>", self.demo_key)
        top = tk.Frame(r, bg=TEAL, height=48)
        top.pack(fill="x")
        tk.Label(top, text="Self-checkout", font=MID, fg="white", bg=TEAL).pack(side="left", padx=14)
        self.total_label = tk.Label(top, text="", font=MID, fg="white", bg=TEAL)
        self.total_label.pack(side="right", padx=14)
        self.body = tk.Frame(r, bg=BG)
        self.body.pack(fill="both", expand=True)
        self.status = tk.Label(r, text="", font=SMALL, fg=ORANGE, bg=BG)
        self.status.pack(fill="x", pady=4)

    def screen(self, big, small="", buttons=(), big_font=BIG):
        """Clear the middle of the window and draw one screen: a big line, a small line, buttons."""
        for w in self.body.winfo_children():
            w.destroy()
        self.big = tk.Label(self.body, text=big, font=big_font, fg=TEXT, bg=BG)
        self.big.pack(pady=(30, 6))
        self.small = tk.Label(self.body, text=small, font=MID, fg=GREY, bg=BG)
        self.small.pack(pady=6)
        row = tk.Frame(self.body, bg=BG)
        row.pack(side="bottom", pady=18)
        for text, command, colour in buttons:
            tk.Button(row, text=text, command=command, font=BUTTON, fg="white", bg=colour,
                      activebackground=colour, activeforeground="white", relief="flat",
                      width=max(8, len(text) + 4), height=2).pack(side="left", padx=10)
        n = len(self.bill.lines)
        self.total_label.config(text=f"{n} item{'s' if n != 1 else ''}   {rupees(self.bill.total_paise)}")

    # ------------------------------------------------------------------ states
    def go(self, state):
        """Change state and draw its screen."""
        self.state = state
        if state == WAITING:
            buttons = [("Finish", lambda: self.go(BILL), TEAL)] if self.bill.lines else []
            self.screen("Place an item", "One item, in the middle of the tray", buttons)
        elif state == SETTLING:
            self.screen("...", "Weighing, please wait")
        elif state == SHOWING:
            index, chance = self.item["guesses"][0]
            name = CLASSES[index]
            g, rpk = self.item["grams"], self.prices[name]
            self.screen(name, f"{g:.0f} g    Rs {rpk}/kg    {rupees(price_paise(g, rpk))}",
                        [("Add to bill", lambda: self.add(name), GREEN),
                         ("Wrong item", lambda: self.go(CHOOSING), ORANGE)])
        elif state == CHOOSING:
            self.choose_screen(full_list=not self.item["guesses"])
        elif state == REMOVE:
            name, g, rpk, p = self.bill.lines[-1]
            self.screen("Take the item off", f"Added: {name}, {g} g, {rupees(p)}")
        elif state == BILL:
            self.screen(self.bill.text(), "", [("Back", lambda: self.go(WAITING), GREY),
                                               ("New customer", self.new_customer, GREEN)],
                        big_font=("DejaVu Sans Mono", 18))

    def choose_screen(self, full_list=False):
        guesses = self.item["guesses"] or []
        sure = bool(guesses) and guesses[0][1] >= self.threshold
        title = "Which item is it?" if sure else "Not sure, please choose"
        if full_list:
            self.screen(title, "", [("Cancel", lambda: self.go(REMOVE if self.bill.lines else WAITING), GREY)],
                        big_font=MID)
            grid = tk.Frame(self.body, bg=BG)
            grid.pack()
            for k, name in enumerate(CLASSES):
                tk.Button(grid, text=name, font=SMALL, width=13, height=2, bg="white", fg=TEXT,
                          command=lambda n=name: self.add(n)).grid(row=k // 4, column=k % 4, padx=4, pady=4)
        else:
            buttons = [(CLASSES[i], lambda n=CLASSES[i]: self.add(n), TEAL) for i, _ in guesses[:3]]
            buttons.append(("Other items", lambda: self.choose_screen(full_list=True), GREY))
            self.screen(title, f"{self.item['grams']:.0f} g on the tray", buttons, big_font=MID)

    # ------------------------------------------------------------------ the tick
    def tick(self):
        """Runs every 100 ms: one scale reading, one filter update, one state step."""
        try:
            raw = self.scale.read_raw(timeout=0) if self.scale.is_ready() else None
            self.no_reading = 0 if raw is not None else self.no_reading + 1
            grams = self.filter.add(raw)
            self.status.config(text="Scale not responding" if self.no_reading > NO_READING_LIMIT else "")
            self.step(grams)
        except Exception:
            traceback.print_exc()                    # keep the kiosk alive; the log shows what happened
        finally:
            self.root.after(TICK_MS, self.tick)

    def step(self, grams):
        s, f = self.state, self.filter
        if s == WAITING:
            if grams > self.on_g:
                self.go(SETTLING)
        elif s == SETTLING:
            self.big.config(text=f"{grams:.0f} g")   # live weight
            if grams < self.off_g:
                self.go(WAITING)                     # it was lifted off again
            elif f.steady:
                self.identify()
        elif s in (SHOWING, CHOOSING):
            if grams < self.off_g:
                self.go(WAITING)                     # taken off without adding: nothing is billed
            elif f.steady and abs(f.weight - self.item["grams"]) > CHANGED_G:
                self.go(SETTLING)                    # something was added or swapped: weigh again
        elif s == REMOVE:
            if grams < self.off_g:
                self.go(WAITING)
        # BILL: the scale is ignored while the customer reads the bill

    def identify(self):
        """One photo, one prediction. Called once per item, when the weight is steady."""
        self.state = IDENTIFYING
        guesses = None
        photo = self.camera.take_photo()
        box = camera.find_item_box(photo) if photo is not None else None
        if box is not None:
            x = prepare_image(crop_with_margin(photo, box))
            guesses = top_k(self.net, x, 3)
        else:
            self.status.config(text="Could not see the item, please choose")
        self.item = {"grams": self.filter.weight, "guesses": guesses}
        if guesses and guesses[0][1] >= self.threshold:
            self.go(SHOWING)
        else:
            self.go(CHOOSING)

    # ------------------------------------------------------------------ buttons
    def add(self, name):
        self.bill.add(name, self.item["grams"], self.prices[name])
        self.go(REMOVE)

    def new_customer(self):
        self.bill.clear()
        self.go(WAITING)

    def demo_key(self, event):
        key = event.char.lower()
        if key == " ":
            self.scale.set_load(0)
        elif key in DEMO_ITEMS:
            name, grams, colour = DEMO_ITEMS[key]
            self.camera.colour = colour
            self.scale.set_load(grams)

    def quit(self):
        self.scale.close()
        self.camera.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Self-checkout kiosk app")
    parser.add_argument("--simulate", action="store_true", help="simulated scale and fake camera (laptop demo)")
    parser.add_argument("--windowed", action="store_true", help="an 800 x 480 window instead of fullscreen")
    args = parser.parse_args()
    root = tk.Tk()
    KioskApp(root, simulate=args.simulate, windowed=args.windowed)
    root.mainloop()


if __name__ == "__main__":
    main()
