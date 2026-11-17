"""weight_filter.py - turn noisy raw HX711 numbers into one steady weight in grams.

Three steps for every new raw reading:
  1. Clean:  take the median of the newest 5 raw readings. One wild reading
             (the Linux timing trap) can never be the middle of 5, so it vanishes.
  2. Convert: grams = (raw - offset) / counts_per_gram.
  3. Steady: the weight is "steady" when the newest 8 cleaned values differ by
             less than 2 g. The steady weight is their average.
It also re-tares by itself: if the tray has been empty and steady for 5 s
(50 readings), the current reading becomes the new zero. That removes slow drift.

Small example (offset 0, 1 count per gram, so raw numbers are grams):
>>> f = WeightFilter(offset=0, counts_per_gram=1.0)
>>> for raw in [412, 413, 2600, 412, 411, 412, 413, 412, 412, 411, 412]:
...     g = f.add(raw)
>>> round(g), f.steady, round(f.weight, 1)
(412, True, 412.1)
>>> f.add(None) == g          # a timed-out reading changes nothing
True
"""
from collections import deque
from statistics import median

MEDIAN_N = 5            # readings in the median window
STEADY_N = 8            # cleaned readings that must agree
STEADY_BAND_G = 2.0     # ... within this many grams
ITEM_ON_G = 20.0        # above this, something is on the tray
ITEM_OFF_G = 10.0       # below this, the tray counts as empty
RETARE_AFTER = 50       # empty and steady for 50 readings (5 s) -> new zero


class WeightFilter:
    def __init__(self, offset, counts_per_gram, median_n=MEDIAN_N, steady_n=STEADY_N,
                 band_g=STEADY_BAND_G):
        self.offset = float(offset)
        self.cpg = float(counts_per_gram)
        self.band = band_g
        self.raw = deque(maxlen=median_n)       # newest raw readings
        self.clean = deque(maxlen=steady_n)     # newest cleaned values, in grams
        self.empty_count = 0                    # readings in a row with an empty, steady tray

    def to_grams(self, raw):
        return (raw - self.offset) / self.cpg

    def add(self, raw):
        """Feed one raw reading (or None). Returns the newest cleaned weight in grams."""
        if raw is None:                         # read_raw timed out: keep what we have
            return self.clean[-1] if self.clean else 0.0
        self.raw.append(raw)
        g = self.to_grams(median(self.raw))
        self.clean.append(g)
        self._auto_retare()
        return g

    @property
    def steady(self):
        return len(self.clean) == self.clean.maxlen and max(self.clean) - min(self.clean) < self.band

    @property
    def weight(self):
        """The average of the newest cleaned values: the number I bill."""
        return sum(self.clean) / len(self.clean) if self.clean else 0.0

    def tare(self, raw_readings):
        """Make the median of these raw readings the new zero (start-up uses 20 readings)."""
        good = sorted(r for r in raw_readings if r is not None)
        if good:
            self.offset = float(median(good))
        self.raw.clear()
        self.clean.clear()

    def _auto_retare(self):
        if self.steady and abs(self.weight) < ITEM_OFF_G:
            self.empty_count += 1
            if self.empty_count >= RETARE_AFTER:
                self.offset = float(median(self.raw))   # the tray is empty: this is zero now
                self.clean.clear()
                self.empty_count = 0
        else:
            self.empty_count = 0


if __name__ == "__main__":
    import doctest
    print("doctest failures:", doctest.testmod().failed)

    # A made-up run at 10 readings per second, with my calibration numbers.
    offset, cpg = 123_450, 431.0
    f = WeightFilter(offset, cpg)
    readings = [offset + 3] * 10                                  # 1 s empty tray
    landing = [60, 250, 470, 395, 420]                            # the tomato lands and wobbles
    readings += [offset + int(g * cpg) for g in landing]
    readings += [offset + int((412 + d) * cpg) for d in (0.3, -0.4, 0.2, 0.0, -0.3, 0.4, 0.1)]
    readings += [offset + 2600 * 431]                             # one wild reading (2,600 g)
    readings += [offset + int((412 + d) * cpg) for d in (0.2, -0.1, 0.0, 0.3, -0.2, 0.1)]
    put_down = None
    for i, raw in enumerate(readings):
        t = i / 10
        if put_down is None and f.to_grams(raw) > ITEM_ON_G:
            put_down = t                                          # the first raw reading above 20 g
        was_steady = f.steady
        g = f.add(raw)
        print(f"t={t:3.1f} s  raw={raw:>10,}  cleaned={g:7.1f} g  {'steady' if f.steady else ''}")
        if put_down is not None and f.steady and not was_steady:
            print(f"   -> steady weight {f.weight:.1f} g, {t - put_down:.1f} s after the item was put down")
