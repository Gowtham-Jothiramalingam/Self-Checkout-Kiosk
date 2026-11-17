"""calibrate.py - measure the scale's zero and slope once, and save them in config.json.

Run on the Pi with the kiosk app stopped:
    systemctl --user stop kiosk.service
    python3 calibrate.py
    systemctl --user start kiosk.service
You need one known weight (500 g). The script asks for an empty tray, then for
the weight in the middle of the tray, and works out:
    offset          = median raw reading with the empty tray
    counts_per_gram = (median raw with the weight - offset) / 500
On a laptop, `python3 calibrate.py --simulate` walks through the same steps
with the simulated scale and no questions.
"""
import argparse
import json
from pathlib import Path
from statistics import median

import hx711

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"
READINGS = 20                    # 20 readings = 2 s at 10 readings per second


def median_of_readings(scale, n=READINGS):
    """The median of n good readings; timed-out readings (None) are skipped."""
    values = [r for r in (scale.read_raw() for _ in range(n)) if r is not None]
    if len(values) < n // 2:
        raise SystemExit("The HX711 is not answering. Check VCC (pin 1), GND (pin 6), "
                         "DT (pin 29, GPIO 5) and SCK (pin 31, GPIO 6).")
    return median(values)


def ask(prompt, simulate):
    if simulate:
        print(prompt, "(simulated)")
    else:
        input(prompt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grams", type=float, default=500.0, help="the known check weight")
    ap.add_argument("--simulate", action="store_true", help="laptop walk-through with the simulated scale")
    args = ap.parse_args()
    scale = hx711.SimulatedHX711() if args.simulate else hx711.HX711()

    ask("Empty the tray and press Enter.", args.simulate)
    offset = median_of_readings(scale)
    print(f"empty tray: {offset:,.0f} counts")

    ask(f"Put the {args.grams:.0f} g weight in the middle of the tray and press Enter.", args.simulate)
    if args.simulate:
        scale.set_load(args.grams)
    loaded = median_of_readings(scale)
    print(f"with {args.grams:.0f} g: {loaded:,.0f} counts")

    cpg = (loaded - offset) / args.grams
    if cpg <= 0:
        raise SystemExit("The reading went DOWN when weight was added: swap the white and "
                         "green load cell wires at A- and A+ (chapter 4), then run this again.")
    print(f"counts_per_gram = ({loaded:,.0f} - {offset:,.0f}) / {args.grams:.0f} = {cpg:.1f}")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))   # keep every other setting
    config.update({"offset": int(round(offset)), "counts_per_gram": round(cpg, 1),
                   "calibrated_with_grams": int(args.grams)})
    if args.simulate:
        print("simulated run: config.json not changed")
    else:
        CONFIG.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        print("saved in", CONFIG)
    scale.close()


if __name__ == "__main__":
    main()
