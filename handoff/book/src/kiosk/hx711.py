"""hx711.py - read the HX711 load cell amplifier through two Raspberry Pi GPIO pins.

Wiring (physical pin numbers on the 40-pin header):
  HX711 VCC -> pin 1 (3.3 V)     HX711 GND -> pin 6
  HX711 DT  -> pin 29 (GPIO 5)   HX711 SCK -> pin 31 (GPIO 6)

How one reading works:
  1. The HX711 pulls DT low when a new reading is ready (10 times a second).
  2. The Pi gives 24 short pulses on SCK. After each pulse the HX711 puts the
     next bit on DT, biggest bit first.
  3. A 25th pulse tells the HX711 "next time, channel A with gain 128 again".
  4. The 24 bits are a signed number in two's complement.
The trap: if SCK stays high for more than 60 microseconds, the HX711 powers
down and the reading is lost. Linux can pause this program at any moment, so
now and then a reading comes out wrong. weight_filter.py removes those.

On a laptop RPi.GPIO does not exist. A small stand-in keeps this file
importable, and SimulatedHX711 gives believable readings for demos.
"""
import random
import time

try:
    import RPi.GPIO as GPIO          # on the Pi this comes from the rpi-lgpio package
    ON_PI = True
except ImportError:                  # laptop: a do-nothing stand-in with the same names
    ON_PI = False

    class _FakeGPIO:
        BCM, IN, OUT, LOW, HIGH = "BCM", "IN", "OUT", 0, 1

        def setmode(self, mode): pass
        def setwarnings(self, flag): pass
        def setup(self, pin, direction, initial=0): pass
        def output(self, pin, value): pass
        def input(self, pin): return 0
        def cleanup(self, pins=None): pass

    GPIO = _FakeGPIO()

DT_PIN = 5       # GPIO 5 = physical pin 29, data from the HX711
SCK_PIN = 6      # GPIO 6 = physical pin 31, clock pulses from the Pi


class HX711:
    """The real chip, read bit by bit."""

    def __init__(self, dt_pin=DT_PIN, sck_pin=SCK_PIN):
        self.dt, self.sck = dt_pin, sck_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)                         # use GPIO numbers, not pin numbers
        GPIO.setup(self.sck, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dt, GPIO.IN)

    def is_ready(self):
        return GPIO.input(self.dt) == 0                # DT low means "a reading is waiting"

    def read_raw(self, timeout=1.0):
        """One 24-bit reading as a signed whole number, or None after `timeout` seconds."""
        deadline = time.monotonic() + timeout
        while not self.is_ready():
            if time.monotonic() > deadline:
                return None                            # wire loose, chip unpowered, or swapped pins
            time.sleep(0.001)
        value = 0
        for _ in range(24):                            # 24 bits, biggest bit first
            GPIO.output(self.sck, 1)                   # pulse up: the HX711 puts the next bit on DT
            GPIO.output(self.sck, 0)                   # pulse down at once: keep SCK high only briefly
            value = (value << 1) | GPIO.input(self.dt)
        GPIO.output(self.sck, 1)                       # 25th pulse: channel A, gain 128 next time
        GPIO.output(self.sck, 0)
        if value & 0x800000:                           # top bit set: a negative number
            value -= 1 << 24                           # two's complement for 24 bits
        return value

    def close(self):
        GPIO.cleanup([self.dt, self.sck])


class SimulatedHX711:
    """A pretend scale for laptop demos and tests.

    It behaves like my real one: offset 123,450 counts, 431 counts per gram,
    a little noise, and now and then a wild reading like the Linux timing trap.
    """

    def __init__(self, offset=123_450, counts_per_gram=431.0, noise_g=0.4, wild_every=1200, seed=1):
        self.offset, self.cpg = offset, counts_per_gram
        self.noise_g, self.wild_every = noise_g, wild_every
        self.grams = 0.0
        self.rng = random.Random(seed)

    def is_ready(self):
        return True                                    # a pretend reading is always waiting

    def set_load(self, grams):
        """Pretend an item of this weight is now on the tray (0 = empty)."""
        self.grams = float(grams)

    def read_raw(self, timeout=1.0):
        time.sleep(0)                                  # the real chip makes us wait; the demo does not
        if self.wild_every and self.rng.randrange(self.wild_every) == 0:
            return self.rng.choice([-1, 1]) * self.rng.randrange(1_000_000, 8_000_000)
        g = self.grams + self.rng.gauss(0, self.noise_g)
        return int(round(self.offset + g * self.cpg))

    def close(self):
        pass


if __name__ == "__main__":
    # On the Pi: print 20 raw readings. On a laptop: the same with the simulated scale.
    scale = HX711() if ON_PI else SimulatedHX711()
    print("real HX711" if ON_PI else "no RPi.GPIO here: simulated scale")
    for _ in range(20):
        print(scale.read_raw())
        time.sleep(0.1)
    scale.close()
